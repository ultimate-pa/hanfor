require('../../../telemetry/static/telemetry')
require("bootstrap");
const { io } = require('socket.io-client');

// --------------------------------------------------------------------------------
// WINDOW FUNCTIONS FOR ALL ADDONS
// --------------------------------------------------------------------------------

// Helper function
async function handleResponse(response) {
  if (response.status === 204) return null;
  if (response.status === 403) throw new Error("Addon is disabled");
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json();
}

function createUrl(addon_url, route_url){
  return addon_url
          ? `${window.baseUrl}/api/v1/${addon_url}/${route_url}`
          : `${window.baseUrl}/api/v1/${route_url}`
}

window.get = async function get(addon_url = "", route_url = "", { raw = false } = {}) {
  const response = await fetch(createUrl(addon_url, route_url), { method: "GET" });
  if (raw) return response;
  return handleResponse(response);
}

window.post = async function post(addon_url = "", route_url = "", body = {}) {
  const response = await fetch(createUrl(addon_url, route_url), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse(response);
}

window.del = async function del(addon_url = "", route_url = "", body = {}) {
  const response = await fetch(createUrl(addon_url, route_url), {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse(response);
}

window.showBanner = function showBanner(message, type = 'info', id = 'generic-banner') {
  document.getElementById(id)?.remove();

  const banner = document.createElement('div');
  banner.id        = id;
  banner.className = `alert alert-${type} alert-dismissible m-2`;
  banner.innerHTML = `
    ${message}
    <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
  `;
  document.querySelector('main').prepend(banner);
}

// --------------------------------------------------------------------------------
// SOCKET SETUP
// --------------------------------------------------------------------------------

$(document).ready(() => {
  window.appSocket = io('/ai_addon_data', { path: url_prefix + '/socket.io/' });

  window.appSocket.on('connect', () => {
    window.tabSubs._socketReady();
  });

  window.appSocket.on('reload', () => {
      showBanner(
      'Configuration changed. <a href="#" onclick="location.reload()">Reload now</a> to apply updates.',
      'warning',
      'reload-banner'
    );
  });
});


// ---------------------------------------------------------------------------------
// BOOTSTRAP TAB EVENTS
// ---------------------------------------------------------------------------------

document.addEventListener('shown.bs.tab', event => {
  const target = event.target;

  const tabId =
    target.getAttribute('data-bs-target')
      ?.replace('#tab-', '') ||
    target.getAttribute('href')
      ?.replace('#tab-', '')
      ?.replace('-pane', '');

  if (tabId) {
    window.tabSubs.activate(tabId);
  }
});


// ---------------------------------------------------------------------------------
// HELPER FUNCTIONS
// ---------------------------------------------------------------------------------

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