"""管理頁的 API（``/api/python-packages…``，只有系統管理員，ADR 0027）與頁面用的說明文字。

- ``GET /python-packages``：目前的版本、草稿與檢查的進度、裝置的準備狀態（頁面輪詢）。
- 草稿：``POST /draft/packages``（加入或修改）、``POST /draft/remove``（移除；有已發布的場景
  用到時要寫原因）、``POST /draft/check``（檢查；``upgrade`` 是檢查更新）、``POST /draft/publish``、
  ``DELETE /draft``。
- ``POST /revisions/<號碼>/restore``：回到某一版（建草稿並開始檢查）。
- ``GET /lookup?q=``（名稱或 import 名稱）、``GET /impact?name=``（用到的場景）。
- ``PUT /settings``、``POST /speed-test``。
"""

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Annotated, cast

from fastapi import APIRouter, Query
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from rpa_server.access import current_principal
from rpa_server.i18n import t
from rpa_server.pypackages.locks import PLATFORM_FAMILIES

if TYPE_CHECKING:
    from rpa_server.pypackages.service import Revision
    from rpa_server.services import Services

__all__ = ["dependencies", "describe", "devices", "package_rows", "python_packages_router"]


class _Body(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="forbid")


class AddBody(_Body):
    name: str = Field(max_length=100)
    spec: str = Field(default="", max_length=200)
    platforms: list[str] = Field(default_factory=list[str], max_length=len(PLATFORM_FAMILIES))
    note: str = Field(default="", max_length=300)
    allow_new: bool = False


class RemoveBody(_Body):
    name: str = Field(max_length=100)
    reason: str = Field(default="", max_length=500)


class CheckBody(_Body):
    upgrade: bool = False


class PublishBody(_Body):
    note: str = Field(default="", max_length=2000)


class SettingsBody(_Body):
    source: str = Field(max_length=20)
    custom_url: str = Field(default="", max_length=500)
    proxy: str = Field(default="", max_length=500)
    ca_file: str = Field(default="", max_length=1000)
    cooldown_days: int = Field(ge=0, le=365)
    parallel: int = Field(ge=1, le=16)
    worker_downloads: int = Field(ge=1, le=100)
    keep_versions: int = Field(ge=1, le=1000)


def _actor() -> str | None:
    principal = current_principal()
    return principal.label if principal is not None else None


def _names(value: object) -> object:
    """清單的值用目前語言的分隔符號接起來；其他的值不變。"""
    if not isinstance(value, list):
        return value
    items = cast("list[object]", value)
    return t("js.list_separator").join(str(item) for item in items)


def describe(item: Mapping[str, object]) -> str:
    """檢查的一個錯誤或提醒的說明（目前語言）；不認得的代碼原樣顯示。"""
    code = str(item.get("code") or "")
    values: dict[str, object] = {key: _names(value) for key, value in item.items()}
    values.setdefault("platform", "")
    values.setdefault("file", "")
    try:
        return t(f"pypackages.issue_{code}", **values)
    except KeyError:
        return code


def devices(services: "Services") -> list[dict[str, object]]:
    """已登記的 worker 與它們對目前套件版本的準備狀態。"""
    packages = services.packages
    number = packages.current_number()
    found: list[dict[str, object]] = []
    for record in services.workers.list_workers():
        if record.disabled:
            continue
        status = packages.device_status(record.id)
        state = "unknown"
        if status is not None and status.get("revision") == number:
            state = str(status.get("state"))
        elif status is not None:
            state = "outdated"
        found.append(
            {
                "id": record.id,
                "name": record.name,
                "platform": record.platform,
                "online": record.status in ("online", "busy"),
                "state": state,
                "revision": status.get("revision") if status is not None else None,
                "error": status.get("error") if status is not None else None,
                "at": status.get("at") if status is not None else None,
            }
        )
    return found


def overview(services: "Services") -> dict[str, object]:
    packages = services.packages
    data = packages.status()
    data["revision"] = packages.current().to_json()
    data["devices"] = devices(services)
    return data


def _platforms(values: Sequence[str]) -> list[str]:
    return [value for value in values if value in PLATFORM_FAMILIES]


def python_packages_router(services: "Services") -> APIRouter:
    router = APIRouter(prefix="/python-packages")
    packages = services.packages

    @router.get("")
    def get_overview() -> dict[str, object]:
        return overview(services)

    @router.post("/draft/packages")
    def add_package(body: AddBody) -> dict[str, object]:
        revision = packages.add(
            body.name,
            body.spec,
            _platforms(body.platforms),
            note=body.note,
            allow_new=body.allow_new,
            actor=_actor(),
        )
        return revision.to_json()

    @router.post("/draft/remove")
    def remove_package(body: RemoveBody) -> dict[str, object]:
        return packages.remove(body.name, reason=body.reason, actor=_actor()).to_json()

    @router.delete("/draft", status_code=204)
    def discard() -> None:
        packages.discard()

    @router.post("/draft/check", status_code=202)
    def check(body: CheckBody | None = None) -> dict[str, object]:
        upgrade = body.upgrade if body is not None else False
        return packages.start_check(upgrade=upgrade, actor=_actor()).to_json()

    @router.post("/draft/publish")
    def publish(body: PublishBody | None = None) -> dict[str, object]:
        note = body.note if body is not None else ""
        return packages.publish(note=note, actor=_actor()).to_json()

    @router.post("/revisions/{number}/restore", status_code=202)
    def restore(number: int) -> dict[str, object]:
        return packages.restore(number, actor=_actor()).to_json()

    @router.get("/lookup")
    def lookup(q: Annotated[str, Query(max_length=100)]) -> dict[str, object]:
        return packages.lookup(q)

    @router.get("/impact")
    def impact(name: Annotated[str, Query(max_length=100)]) -> dict[str, object]:
        return {"scenes": packages.impact(name)}

    @router.put("/settings")
    def save_settings(body: SettingsBody) -> dict[str, object]:
        data = cast("dict[str, object]", body.model_dump(by_alias=True))
        return packages.save_settings(data).to_json()

    @router.post("/speed-test")
    def speed_test() -> dict[str, object]:
        packages.speed_test()
        return packages.speed_results() or {"results": []}

    return router


def package_rows(current: "Revision", view: "Revision") -> list[dict[str, object]]:
    """套件清單的每一列（直接加的套件）：草稿和目前的版本比，新加的、改了的、要移除的。"""
    before = {item.key: item for item in current.requirements}
    rows: list[dict[str, object]] = []
    for item in view.requirements:
        old = before.get(item.key)
        change = "new" if old is None else "same"
        if old is not None and (old.spec, old.platforms, old.allow_new) != (
            item.spec,
            item.platforms,
            item.allow_new,
        ):
            change = "changed"
        info = view.packages.get(item.key) or {}
        pending = change != "same" and view.status != "checked"  # 版本要檢查後才知道
        version = None if pending else info.get("version")
        rows.append({"item": item, "change": change, "version": version, "info": info})
    keys = {item.key for item in view.requirements}
    for item in current.requirements:
        if item.key not in keys:
            info = current.packages.get(item.key) or {}
            rows.append(
                {"item": item, "change": "removed", "version": info.get("version"), "info": info}
            )
    return rows


def dependencies(view: "Revision") -> list[dict[str, object]]:
    """不是直接加的套件（被其他套件需要的），依名稱排序。"""
    direct = view.direct()
    return sorted(
        (
            {"key": key, **info}
            for key, info in view.packages.items()
            if key not in direct and not info.get("direct")
        ),
        key=lambda item: str(item.get("name", "")).lower(),
    )
