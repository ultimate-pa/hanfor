let addon_data;
let provider_data;

// -- HELPER FUNCTIONS ---------------------------------------------------------
function led(activity) {
    let color = "led-off";
    if (activity === "ACTIVE") color = "led-on";
    else if (activity === "NOT_TESTED") color = "led-yellow";
    return `<span class="led ${color}"></span>`;
}

// Combined default tag + button
function btnDefault(isDefault, action) {
  if (isDefault) {
    return `<span class="tag-default">default</span>`;
  }
  return `<button class="default-btn" onclick="${action}">set default</button>`;
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
      ${p.models.map(m => modelCard(p.name, m)).join("")}
    </div>
  </div>`;
}

function addonCard(a) {
  return `
  <div class="addon-card ${a.enabled ? "addon-enabled" : ""}" id="addon-${a.id}">
    
    <div class="addon-header">
      <div class="addon-title">
        <span class="addon-name">${a.name}</span>
      </div>
    </div>

    <div class="addon-desc">
      ${a.desc}
    </div>

    <div class="addon-footer">
      <button 
        class="status-tag ${a.enabled ? "enabled" : "disabled"}"
        onclick="toggleAddon('${a.id}', ${!a.enabled})"
      >
        ${a.enabled ? "active" : "deactivate"}
      </button>
    </div>

  </div>
  `;
}

// -- RENDER -------------------------------------------------------------------
function renderProviders(providers) {
  const c = document.getElementById("providers-container");
  if (!c) return;
  c.innerHTML = providers.map(providerCard).join("");
}

function renderAddons(data) {
  const c = document.getElementById("addon-container");
  if (!c) return;
  c.innerHTML = data.map(addonCard).join("");
}

// -- ACTIONS ------------------------------------------------------------------
function setDefaultProvider(name) {
    fetch("/ai_addons/ui/api/set_default_provider", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ provider: name })
    })
}


if (window.appSocket) {
  window.appSocket.on('socket_provider_info', (newData) => {
    if (newData.providers) {
          renderProviders(newData.providers);
    }
  });
} else {
  window.addEventListener('load', () => {
    window.appSocket.on('socket_provider_info', (newData) => {
      if (newData.providers) {
          renderProviders(newData.providers);
      }
    });
  });
}



function setDefaultModel(providerName, modelName) {
    fetch("/ai_addons/ui/api/set_default_model", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({provider: providerName, model: modelName})
    })
}

function testProvider(name) {
    fetch("/ai_addons/ui/api/test_provider", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider: name })
    })
}

function testModel(providerName, modelName) {
    fetch("/ai_addons/ui/api/test_model", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider: providerName, model: modelName })
    })
}

function toggleAddon(id) {
    // Save current tab and scroll position before reload
    const activeTab = document.querySelector('#tab-list-ai .nav-link.active');
    if (activeTab) sessionStorage.setItem('activeTab', activeTab.id);
    sessionStorage.setItem('scrollY', window.scrollY);

    fetch("/ai_addons/ui/api/toggle_addon", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ addon: id })
    }).then(() => {
        window.location.reload();
    });
}

function restoreState() {
    const tabId = sessionStorage.getItem('activeTab');
    const scrollY = sessionStorage.getItem('scrollY');

    if (tabId) {
        const btn = document.getElementById(tabId);
        if (btn) btn.click();
        sessionStorage.removeItem('activeTab');
    }
    if (scrollY) {
        window.scrollTo(0, parseInt(scrollY));
        sessionStorage.removeItem('scrollY');
    }
}

document.addEventListener('DOMContentLoaded', restoreState);

// -- INIT ---------------------------------------------------------------------

async function load() {
  const provider_response = await fetch("/ai_addons/ui/api/ai_provider_data");
  provider_data = await provider_response.json();
  renderProviders(provider_data.providers);

  const addon_response = await fetch("/ai_addons/ui/api/ai_addon_data");
  addon_data = await addon_response.json();
  renderAddons(addon_data.addons);
}

load();

window.testModel = testModel;
window.setDefaultModel = setDefaultModel;
window.testProvider = testProvider;
window.setDefaultProvider = setDefaultProvider;
window.toggleAddon = toggleAddon;