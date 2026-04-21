const { io } = require('socket.io-client');

window.tabSubs = (() => {
  const registry      = {};
  const activateHooks = {};
  const deactivateHooks = {};
  let activeTabId     = null;
  let socketReady     = false;

  function currentActiveTabId() {
    const btn = document.querySelector('[data-bs-toggle="tab"].active');
    return btn?.dataset.bsTarget?.replace('#tab-', '') ?? null;
  }

  function attach(tabId) {
    if (!socketReady) return;
    (registry[tabId] || []).forEach(({ event, handler }) => {
      window.appSocket.off(event, handler);
      window.appSocket.on(event, handler);
    });
  }

  function detach(tabId) {
    if (!socketReady) return;
    (registry[tabId] || []).forEach(({ event, handler }) => {
      window.appSocket.off(event, handler);
    });
  }

  return {
    _socketReady() {
      socketReady = true;
      const tabId = activeTabId ?? currentActiveTabId();
      if (tabId) {
        activeTabId = tabId;
        attach(tabId);
        (activateHooks[tabId] || []).forEach(fn => fn());
      }
    },

    activate(tabId) {
      if (activeTabId && activeTabId !== tabId) {
        detach(activeTabId);
        (deactivateHooks[activeTabId] || []).forEach(fn => fn());
      }
      activeTabId = tabId;
      attach(tabId);
      (activateHooks[tabId] || []).forEach(fn => fn());
    },

    register(tabId, subscriptions) {
      registry[tabId] = subscriptions;
      if (socketReady && (activeTabId ?? currentActiveTabId()) === tabId) {
        attach(tabId);
      }
    },

    onActivate(tabId, fn) {
      if (!activateHooks[tabId]) activateHooks[tabId] = [];
      activateHooks[tabId].push(fn);
    },

    onDeactivate(tabId, fn) {
      if (!deactivateHooks[tabId]) deactivateHooks[tabId] = [];
      deactivateHooks[tabId].push(fn);
    },
  };
})();

// -- TAB SWITCHING -------------------------------------------------------------

document.querySelectorAll('[data-bs-toggle="tab"]').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(b => {
      b.classList.remove('active');
      b.setAttribute('aria-selected', 'false');
    });
    document.querySelectorAll('.tab-pane').forEach(p => {
      p.classList.remove('show', 'active');
    });
    btn.classList.add('active');
    btn.setAttribute('aria-selected', 'true');
    document.querySelector(btn.dataset.bsTarget).classList.add('show', 'active');

    const tabId = btn.dataset.bsTarget?.replace('#tab-', '');
    if (tabId) window.tabSubs.activate(tabId);
  });
});

// -- SOCKET SETUP -------------------------------------------------------------

$(document).ready(() => {
  window.appSocket = io('/ai_addon_data', { path: url_prefix + '/socket.io/' });

  window.appSocket.on('connect', () => {
    window.tabSubs._socketReady();
  });

  window.appSocket.on('reload', () => {
    if (document.getElementById('reload-banner')) return;
    const banner = document.createElement('div');
    banner.id        = 'reload-banner';
    banner.className = 'alert alert-warning alert-dismissible m-2';
    banner.innerHTML = `Configuration changed. <a href="#" onclick="location.reload()">Reload now</a> to apply updates.`;
    document.querySelector('main').prepend(banner);
  });
});