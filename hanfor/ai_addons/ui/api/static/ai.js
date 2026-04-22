let addonData;
let providerData;

// -- HELPERS -------------------------------------------------------------------

window.led = function led(activity) {
  const color = activity === 'ACTIVE' ? 'led-on'
              : activity === 'NOT_TESTED' ? 'led-yellow'
              : 'led-off';
  return `<span class="led ${color}"></span>`;
}

function btnDefault(isDefault, action) {
  return isDefault
    ? `<span class="tag-default">default</span>`
    : `<button class="default-btn" onclick="${action}">set default</button>`;
}

function modelCard(provider, m) {
  return `
    <div class="model-card">
      <div class="model-header">
        <div class="model-title">
          ${led(m.active)}
          <span class="model-name">${m.name}</span>
        </div>
        <div class="model-actions">
          <button class="test-btn" onclick="testModel('${provider}','${m.name}')">test</button>
          ${btnDefault(m.default, `setDefaultModel('${provider}','${m.name}')`)}
        </div>
      </div>
      <div class="model-desc">${m.desc}</div>
    </div>`;
}

function providerCard(p) {
  return `
    <div class="provider-card">
      <div class="provider-header">
        <div class="provider-title">
          ${led(p.reachable)}
          <span class="provider-name">${p.name}</span>
        </div>
        <div class="provider-actions">
          <button class="test-btn" onclick="testProvider('${p.name}')">test</button>
          ${btnDefault(p.default, `setDefaultProvider('${p.name}')`)}
        </div>
      </div>
      <div class="provider-info">
        <div class="info-row"><span class="info-label">Max Concurrent Requests</span><span>${p.max_request}</span></div>
        <div class="info-row"><span class="info-label">Method</span><span>${p.api_method}</span></div>
        <div class="info-row"><span class="info-label">URL</span><span class="info-url">${p.url}</span></div>
      </div>
      <div class="provider-models">
        ${p.models.map(m => modelCard(p.name, m)).join('')}
      </div>
    </div>`;
}

function addonCard(a) {
  return `
    <div class="addon-card ${a.enabled ? 'addon-enabled' : ''}" id="addon-${a.id}">
      <div class="addon-header">
        <span class="addon-name">${a.name}</span>
      </div>
      <div class="addon-desc">${a.desc}</div>
      <div class="addon-footer">
        <button
          class="status-tag ${a.enabled ? 'enabled' : 'disabled'}"
          onclick="toggleAddon('${a.id}')"
        >${a.enabled ? 'active' : 'deactivate'}</button>
      </div>
    </div>`;
}

// -- RENDER --------------------------------------------------------------------

function renderProviders(providers) {
  const c = document.getElementById('providers-container');
  if (c) c.innerHTML = providers.map(providerCard).join('');
}

function renderAddons(addons) {
  const c = document.getElementById('addon-container');
  if (c) c.innerHTML = addons.map(addonCard).join('');
}

// -- ACTIONS -------------------------------------------------------------------

function post(url, body) {
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}

function setDefaultProvider(name)               { post('/ai/set_default_provider',  { provider: name }); }
function setDefaultModel(providerName, modelName){ post('/ai/set_default_model',     { provider: providerName, model: modelName }); }
function testProvider(name)                      { post('/ai/test_provider',          { provider: name }); }
function testModel(providerName, modelName)      { post('/ai/test_model',             { provider: providerName, model: modelName }); }

function toggleAddon(id) {
  // Persist active tab + scroll so they survive the reload
  const activeTab = document.querySelector('#tab-list-ai .nav-link.active');
  if (activeTab) sessionStorage.setItem('activeTab', activeTab.id);
  sessionStorage.setItem('scrollY', window.scrollY);

  post('/ai/toggle_addon', { addon: id }).then(() => window.location.reload());
}

function restoreState() {
  const tabId   = sessionStorage.getItem('activeTab');
  const scrollY = sessionStorage.getItem('scrollY');
  if (tabId)   { document.getElementById(tabId)?.click(); sessionStorage.removeItem('activeTab'); }
  if (scrollY) { window.scrollTo(0, parseInt(scrollY));   sessionStorage.removeItem('scrollY');  }
}

document.addEventListener('DOMContentLoaded', restoreState);

// -- SOCKET SUBSCRIPTIONS --------------------------------------------------------------

window.tabSubs.register('ai_addons_ai', [
  {
    event:   'socket_provider_info',
    handler: ({ providers }) => {
      if (providers) renderProviders(providers); },
  },
]);

window.tabSubs.onActivate('ai_addons_ai', load);

// -- INIT ----------------------------------------------------------------------

async function load() {
  const [provRes, addonRes] = await Promise.all([
    fetch('/core_ai_addon/ai_provider_data'),
    fetch('/ai/ai_addon_data'),
  ]);
  providerData = await provRes.json();
  addonData    = await addonRes.json();
  renderProviders(providerData.providers);
  renderAddons(addonData.addons);
}

document.getElementById('rescan-provider-btn').addEventListener("click", async () => {
    await fetch("/ai/rescan_provider", {
        method: "POST",
    });
});

document.getElementById('test-all-provider-btn').addEventListener("click", async () => {
    await fetch("/ai/test_all_provider", {
        method: "POST",
    });
});

document.getElementById('activate-all-addons-btn').addEventListener("click", async () => {
      // Persist active tab + scroll so they survive the reload
  const activeTab = document.querySelector('#tab-list-ai .nav-link.active');
  if (activeTab) sessionStorage.setItem('activeTab', activeTab.id);
  sessionStorage.setItem('scrollY', window.scrollY);
    await fetch("/ai/activate_all_addons", {
        method: "POST",
    }).then(() => window.location.reload());
});

document.getElementById('deactivate-all-addons-btn').addEventListener("click", async () => {
      // Persist active tab + scroll so they survive the reload
  const activeTab = document.querySelector('#tab-list-ai .nav-link.active');
  if (activeTab) sessionStorage.setItem('activeTab', activeTab.id);
  sessionStorage.setItem('scrollY', window.scrollY);
    await fetch("/ai/deactivate_all_addons", {
        method: "POST",
    }).then(() => window.location.reload());
});

// Expose to inline onclick handlers
window.testModel          = testModel;
window.setDefaultModel    = setDefaultModel;
window.testProvider       = testProvider;
window.setDefaultProvider = setDefaultProvider;
window.toggleAddon        = toggleAddon;