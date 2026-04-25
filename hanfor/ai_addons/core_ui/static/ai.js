let addonData;
let providerData;
const ADDON_NAME = "ai"

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


function setDefaultProvider(name)                { window.post(ADDON_NAME,'/provider/set_default',  { provider: name }); }
function setDefaultModel(providerName, modelName){ window.post(ADDON_NAME,'/model/set_default',     { provider: providerName, model: modelName }); }
function testProvider(name)                      { window.post(ADDON_NAME,'/provider/test',          { provider: name }); }
function testModel(providerName, modelName)      { window.post(ADDON_NAME,'/model/test',             { provider: providerName, model: modelName }); }


function toggleAddon(id) {
  const activeTab = document.querySelector('#tab-list-ai .nav-link.active');
  if (activeTab) sessionStorage.setItem('activeTab', activeTab.id);
  sessionStorage.setItem('scrollY', window.scrollY);
  window.post(ADDON_NAME,'/addon/toggle', { addon_id: id }).then(() => window.location.reload());
}

function reloadWithState(promise) {
  const activeTab = document.querySelector('#tab-list-ai .nav-link.active');
  if (activeTab) sessionStorage.setItem('activeTab', activeTab.id);
  sessionStorage.setItem('scrollY', window.scrollY);
  promise.then(() => window.location.reload());
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
  const [providerDataRes, addonDataRes] = await Promise.all([
    window.get("core-ai-addon", "ai-provider-data"),
    window.get(ADDON_NAME, "")
  ]);
  providerData = providerDataRes
  addonData = addonDataRes
  renderProviders(providerData.providers);
  renderAddons(addonDataRes.addons);
}

// -- BUTTON LISTENERS ----------------------------------------------------------

document.getElementById('rescan-provider-btn').addEventListener('click', () => {
  window.post(ADDON_NAME,'/provider/rescan');
});

document.getElementById('test-all-provider-btn').addEventListener('click', () => {
  window.post(ADDON_NAME,'/provider/test_all');
});

document.getElementById('activate-all-addons-btn').addEventListener('click', () => {
  reloadWithState(window.post(ADDON_NAME,'/addon/activate_all'));
});

document.getElementById('deactivate-all-addons-btn').addEventListener('click', () => {
  reloadWithState(window.post(ADDON_NAME,'/addon/deactivate_all'));
});

// Expose to inline onclick handlers
window.testModel          = testModel;
window.setDefaultModel    = setDefaultModel;
window.testProvider       = testProvider;
window.setDefaultProvider = setDefaultProvider;
window.toggleAddon        = toggleAddon;