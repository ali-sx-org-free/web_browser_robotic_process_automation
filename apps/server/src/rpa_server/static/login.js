// 登入、建立第一個系統管理員（M8，ADR 0025）：伺服器沒有表單解析，用 JSON 送出。
(() => {
  'use strict';
  const form = document.getElementById('auth-form');
  if (!form) return;
  const error = form.querySelector('.form-error');
  const button = form.querySelector('button[type="submit"]');
  form.addEventListener('submit', async event => {
    event.preventDefault();
    error.textContent = '';
    const setup = form.dataset.mode === 'setup';
    const value = name => (form.elements[name] ? form.elements[name].value : '');
    if (setup && value('password') !== value('again')) {
      error.textContent = error.dataset.mismatch;
      return;
    }
    const body = setup
      ? {username: value('username').trim().toLowerCase(), displayName: value('displayName'), password: value('password')}
      : {username: value('username').trim(), password: value('password'), next: form.dataset.next};
    button.disabled = true;
    try {
      const response = await fetch(setup ? '/setup' : '/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', Accept: 'application/json'},
        credentials: 'same-origin',
        body: JSON.stringify(body),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const detail = data.error ? data.error.message : Array.isArray(data.detail) ? data.detail.map(item => item.msg).join('; ') : '';
        error.textContent = detail || String(response.status);
        return;
      }
      location.assign(data.next || '/scenes');
    } catch {
      error.textContent = error.dataset.offline;
    } finally {
      button.disabled = false;
    }
  });
})();
