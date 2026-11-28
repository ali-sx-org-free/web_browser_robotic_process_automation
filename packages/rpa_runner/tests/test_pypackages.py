"""套件環境的組裝（ADR 0027，rpa_runner.pypackages）。

「內附的運行環境」用這次測試的 Python 建的 venv 代替，裡面用 :func:`install_wheel` 放兩個假的
套件（和真的運行環境一樣有 dist-info 與 RECORD）；wheel 是測試自己產生的純 Python 套件，
``fetch`` 從測試的資料夾複製，不連網。
"""

import base64
import hashlib
import json
import os
import subprocess
import sys
import time
import zipfile
from collections.abc import Callable, Mapping
from pathlib import Path

import pytest

from rpa_runner.pypackages import (
    ENVS,
    WHEELS,
    PackageFile,
    PackageSet,
    PackagesUnavailableError,
    base_packages,
    env_status,
    install_wheel,
    normalize,
    prepare_packages,
    prune,
    site_packages,
)
from rpa_runner.pyruntime import PreparedRuntime, clean_environment, platform_tag, python_path

LOCK_A = "a" * 64
LOCK_B = "b" * 64


def make_wheel(folder: Path, name: str, version: str, files: Mapping[str, bytes]) -> Path:
    """一個 wheel：files 的路徑相對於 wheel 的根目錄（可以有 <名稱>-<版本>.data/…）。"""
    folder.mkdir(parents=True, exist_ok=True)
    stem = f"{name.replace('-', '_')}-{version}"
    path = folder / f"{stem}-py3-none-any.whl"
    content = dict(files)
    content[f"{stem}.dist-info/METADATA"] = (
        f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n\nbody\n".encode()
    )
    content[f"{stem}.dist-info/WHEEL"] = (
        b"Wheel-Version: 1.0\nGenerator: test\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
    )
    rows: list[str] = []
    for key, data in content.items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
        rows.append(f"{key},sha256={digest},{len(data)}")
    rows.append(f"{stem}.dist-info/RECORD,,")
    content[f"{stem}.dist-info/RECORD"] = ("\n".join(rows) + "\n").encode()
    with zipfile.ZipFile(path, "w") as archive:
        for key, data in content.items():
            archive.writestr(key, data)
    return path


def entry(wheel: Path, name: str, version: str) -> PackageFile:
    data = wheel.read_bytes()
    return PackageFile(name, version, wheel.name, hashlib.sha256(data).hexdigest(), len(data))


def run_python(python: Path, code: str) -> str:
    completed = subprocess.run(
        [str(python), "-E", "-s", "-B", "-c", code],
        capture_output=True,
        text=True,
        check=False,
        env=clean_environment(os.environ),
    )
    assert completed.returncode == 0, completed.stderr
    return completed.stdout.strip()


@pytest.fixture(scope="module")
def base_root(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """假的內附運行環境：一個 venv，site-packages 裡有 bundled-pkg 1.0 與 only-base 1.0。"""
    root = tmp_path_factory.mktemp("base") / "runtime"
    subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(root)], check=True)
    site = site_packages(root)
    assert site is not None
    wheels = tmp_path_factory.mktemp("base-wheels")
    for name, module in (("bundled-pkg", "bundled_pkg"), ("only-base", "only_base")):
        wheel = make_wheel(wheels, name, "1.0", {f"{module}/__init__.py": b"WHERE = 'base'\n"})
        install_wheel(wheel, site, root)
    return root


@pytest.fixture
def runtime(base_root: Path) -> PreparedRuntime:
    return PreparedRuntime(
        root=base_root,
        version="1.0.0",
        platform=platform_tag(),
        python_version="3",
        reused=True,
        prepared_ms=0,
    )


@pytest.fixture
def env(tmp_path: Path) -> dict[str, str]:
    return {**os.environ, "RPA_CACHE_DIR": str(tmp_path / "cache")}


class Source:
    """假的伺服器：sha256 → wheel；記下下載了哪些。"""

    def __init__(self, *wheels: Path) -> None:
        self.files = {hashlib.sha256(path.read_bytes()).hexdigest(): path for path in wheels}
        self.fetched: list[str] = []

    def __call__(self, item: PackageFile, target: Path, progress: Callable[[int], None]) -> None:
        self.fetched.append(item.filename)
        data = self.files[item.sha256].read_bytes()
        target.write_bytes(data)
        progress(len(data))


def bundled_entry(base_root: Path, name: str) -> PackageFile:
    """內附的套件在清單裡的樣子（sha256 不重要：同名同版的直接從內附的複製）。"""
    return PackageFile(name, "1.0", f"{name.replace('-', '_')}-1.0-py3-none-any.whl", "0" * 64, 1)


def test_same_as_bundled_uses_bundled_runtime(
    runtime: PreparedRuntime, env: dict[str, str], base_root: Path
) -> None:
    packages = PackageSet(
        1,
        LOCK_A,
        runtime.platform,
        (bundled_entry(base_root, "Bundled_Pkg"), bundled_entry(base_root, "only-base")),
    )
    source = Source()
    prepared = prepare_packages(runtime, packages, fetch=source, environ=env)
    assert prepared.bundled
    assert prepared.python == runtime.python
    assert source.fetched == []
    assert not (Path(env["RPA_CACHE_DIR"]) / "python" / ENVS).exists()
    assert env_status(packages, runtime, env)


def test_builds_env_copies_bundled_and_installs_new(
    tmp_path: Path, runtime: PreparedRuntime, env: dict[str, str], base_root: Path
) -> None:
    extra = make_wheel(
        tmp_path / "wheels",
        "extra-pkg",
        "2.0",
        {
            "extra_pkg/__init__.py": b"from bundled_pkg import WHERE\nVALUE = 42\n",
            "extra_pkg-2.0.data/data/share/extra/readme.txt": b"data file\n",
            "extra_pkg-2.0.data/scripts/extra-tool": b"#!/bin/sh\necho no\n",
            "extra_pkg-2.0.data/purelib/extra_plugin.py": b"PLUGIN = True\n",
        },
    )
    packages = PackageSet(
        2,
        LOCK_A,
        runtime.platform,
        (bundled_entry(base_root, "bundled-pkg"), entry(extra, "extra-pkg", "2.0")),
        direct=("extra-pkg",),
    )
    source = Source(extra)
    progress: list[tuple[int, int]] = []
    prepared = prepare_packages(
        runtime,
        packages,
        fetch=source,
        environ=env,
        on_progress=lambda done, total: progress.append((done, total)),
    )
    assert not prepared.bundled
    assert not prepared.reused
    assert prepared.copied == 1
    assert prepared.downloaded == 1
    assert prepared.downloaded_bytes == extra.stat().st_size
    assert progress[-1] == (extra.stat().st_size, extra.stat().st_size)
    assert prepared.root.parent == Path(env["RPA_CACHE_DIR"]) / "python" / ENVS
    assert prepared.root.name.endswith(f"-{runtime.platform}")
    assert prepared.python == python_path(prepared.root)
    out = run_python(
        prepared.python,
        "import sys, extra_pkg, extra_plugin, bundled_pkg, importlib.util as u;"
        "print(extra_pkg.VALUE, bundled_pkg.WHERE, extra_plugin.PLUGIN,"
        " u.find_spec('only_base') is None, sys.prefix != sys.base_prefix)",
    )
    assert out == "42 base True True True"
    assert (prepared.root / "share" / "extra" / "readme.txt").is_file()
    assert not list(prepared.root.rglob("extra-tool"))  # 不產生命令列程式
    site = site_packages(prepared.root)
    assert site is not None
    assert (site / "extra_pkg-2.0.dist-info" / "INSTALLER").read_text() == "rpa\n"
    assert list((site / "extra_pkg" / "__pycache__").glob("__init__.*.pyc"))  # compileall
    wheel = Path(env["RPA_CACHE_DIR"]) / "python" / WHEELS / f"{packages.files[1].sha256}.whl"
    assert wheel.is_file()
    info = json.loads((prepared.root / "rpa-packages.json").read_text())
    assert info["revision"] == 2
    assert info["runtime"] == "1.0.0"
    assert env_status(packages, runtime, env)

    again = prepare_packages(runtime, packages, fetch=source, environ=env)
    assert again.reused
    assert again.root == prepared.root
    assert source.fetched == [extra.name]

    # 內附的運行環境換了版本（App 更新）：重建，wheel 已經在快取，不再下載
    newer = PreparedRuntime(base_root, "1.0.1", runtime.platform, "3", True, 0)
    rebuilt = prepare_packages(newer, packages, fetch=source, environ=env)
    assert rebuilt.root != prepared.root
    assert not rebuilt.reused
    assert rebuilt.downloaded == 0
    assert source.fetched == [extra.name]


def test_sha256_mismatch_is_rejected(
    tmp_path: Path, runtime: PreparedRuntime, env: dict[str, str]
) -> None:
    good = make_wheel(tmp_path / "good", "pkg-x", "1.0", {"pkg_x/__init__.py": b""})
    evil = make_wheel(tmp_path / "evil", "pkg-x", "1.0", {"pkg_x/__init__.py": b"EVIL = 1\n"})
    item = entry(good, "pkg-x", "1.0")
    source = Source(evil)
    source.files[item.sha256] = evil  # 伺服器（或中間人）給了不同的檔案
    packages = PackageSet(3, LOCK_B, runtime.platform, (item,))
    with pytest.raises(PackagesUnavailableError, match="sha256"):
        prepare_packages(runtime, packages, fetch=source, environ=env)
    cache = Path(env["RPA_CACHE_DIR"]) / "python"
    assert not list((cache / WHEELS).iterdir())
    assert not [path for path in (cache / ENVS).iterdir() if not path.name.endswith(".lock")]


def test_import_check_failure_discards_env(
    tmp_path: Path, runtime: PreparedRuntime, env: dict[str, str]
) -> None:
    broken = make_wheel(
        tmp_path / "w",
        "broken-pkg",
        "1.0",
        {"broken_pkg/__init__.py": b"raise ImportError('needs libfoo')\n"},
    )
    packages = PackageSet(4, LOCK_B, runtime.platform, (entry(broken, "broken-pkg", "1.0"),))
    packages = PackageSet(4, LOCK_B, runtime.platform, packages.files, direct=("broken-pkg",))
    with pytest.raises(PackagesUnavailableError, match="needs libfoo"):
        prepare_packages(runtime, packages, fetch=Source(broken), environ=env)
    envs = Path(env["RPA_CACHE_DIR"]) / "python" / ENVS
    assert not [path for path in envs.iterdir() if not path.name.startswith(".")]
    assert not list(envs.glob(".tmp-*"))
    # 不檢查時照樣能組（伺服器檢查之外的用法，例如測試）
    prepared = prepare_packages(runtime, packages, fetch=Source(broken), environ=env, check=False)
    assert prepared.python.exists()


def test_platform_mismatch(runtime: PreparedRuntime, env: dict[str, str]) -> None:
    packages = PackageSet(2, LOCK_A, "other-platform", ())
    with pytest.raises(PackagesUnavailableError, match="other-platform"):
        prepare_packages(runtime, packages, fetch=Source(), environ=env)


def test_install_wheel_rejects_unsafe_paths(tmp_path: Path) -> None:
    wheel = make_wheel(tmp_path, "bad", "1.0", {"../outside.py": b"x = 1\n"})
    site = tmp_path / "site"
    site.mkdir()
    with pytest.raises(PackagesUnavailableError, match="unsafe path"):
        install_wheel(wheel, site, tmp_path / "prefix")
    assert not (tmp_path / "outside.py").exists()


def test_base_packages_reads_dist_info(base_root: Path) -> None:
    found = base_packages(base_root)
    assert set(found) == {("bundled-pkg", "1.0"), ("only-base", "1.0")}
    files = found[("bundled-pkg", "1.0")].files
    assert "bundled_pkg/__init__.py" in files


def test_prune_keeps_recent_envs_and_their_wheels(tmp_path: Path) -> None:
    cache = tmp_path / "python"
    envs, wheels = cache / ENVS, cache / WHEELS
    wheels.mkdir(parents=True)
    now = time.time()
    for index in range(5):
        folder = envs / f"env{index}"
        folder.mkdir(parents=True)
        (folder / ".ready").write_text("x")
        (folder / "rpa-packages.json").write_text(json.dumps({"wheels": [f"{index:064d}"]}))
        os.utime(folder / ".ready", (now - 100 * index, now - 100 * index))
        wheel = wheels / f"{index:064d}.whl"
        wheel.write_bytes(b"w")
        os.utime(wheel, (now - 3 * 86400, now - 3 * 86400))
    fresh = wheels / f"{9:064d}.whl"  # 剛下載、還沒有環境用到
    fresh.write_bytes(b"w")
    removed = prune(cache, keep=(envs / "env4",), now=now)
    assert {path.name for path in removed} == {"env3"}
    assert sorted(path.name for path in envs.iterdir()) == ["env0", "env1", "env2", "env4"]
    assert not (wheels / f"{3:064d}.whl").exists()
    assert (wheels / f"{4:064d}.whl").exists()
    assert fresh.exists()


def test_package_set_json_round_trip() -> None:
    item = PackageFile("Tabulate", "0.10.0", "tabulate-0.10.0-py3-none-any.whl", "c" * 64, 10)
    packages = PackageSet(5, LOCK_A, "linux-x86_64", (item,), direct=("Tabulate",))
    data = packages.to_json()
    assert PackageSet.from_json(data) == PackageSet(
        5, LOCK_A, "linux-x86_64", (item,), direct=("tabulate",)
    )
    assert packages.key("1.0.0") != packages.key("1.0.1")
    for bad in (
        {**data, "revision": 0},
        {**data, "lock": "xyz"},
        {**data, "files": [{**item.to_json(), "sha256": "nothex"}]},
        {**data, "files": [{**item.to_json(), "filename": "../x.whl"}]},
    ):
        with pytest.raises(PackagesUnavailableError):
            PackageSet.from_json(bad)
    assert normalize("Python_Docx.ext") == "python-docx-ext"
