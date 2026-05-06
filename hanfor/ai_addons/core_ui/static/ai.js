// --------------------------------------------------------------------------------
// CONFIG
// --------------------------------------------------------------------------------

let addonData;
let providerData;

const ADDON_NAME = "ai";
const TAB_ID     = "ai_addons_ai";


// --------------------------------------------------------------------------------
// SOCKET SUBSCRIPTIONS
// --------------------------------------------------------------------------------

window.tabSubs.register(TAB_ID, [
  {
    event: "socket_provider_info",
    handler: ({ providers }) => {
      if (providers) renderProviders(providers);
    }
  }
]);

window.tabSubs.onActivate(TAB_ID, load);


// --------------------------------------------------------------------------------
// ACTIONS
// --------------------------------------------------------------------------------

function setDefaultProvider(name) {
  window.post(ADDON_NAME, "/provider/set_default", { provider: name });
}

function setDefaultModel(provider, model) {
  window.post(ADDON_NAME, "/model/set_default", { provider, model });
}

function testProvider(provider) {
  window.post(ADDON_NAME, "/provider/test", { provider });
}

function testModel(provider, model) {
  window.post(ADDON_NAME, "/model/test", { provider, model });
}

function toggleAddon(id) {
  saveState();

  window
    .post(ADDON_NAME, "/addon/toggle", { addon_id: id })
    .then(() => window.location.reload());
}

function reloadWithState(promise) {
  saveState();
  promise.then(() => window.location.reload());
}


// --------------------------------------------------------------------------------
// ACTION ROUTER (EVENT DELEGATION)
// --------------------------------------------------------------------------------

const actions = {
  "test-provider":        ({ provider })        => testProvider(provider),
  "set-default-provider": ({ provider })        => setDefaultProvider(provider),
  "test-model":           ({ provider, model }) => testModel(provider, model),
  "set-default-model":    ({ provider, model }) => setDefaultModel(provider, model),
  "toggle-addon":         ({ addon })           => toggleAddon(addon)
};

document.addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-action]");
  if (!btn) return;

  const fn = actions[btn.dataset.action];
  if (fn) fn(btn.dataset);
});


// --------------------------------------------------------------------------------
// HELPERS
// --------------------------------------------------------------------------------

window.aiLed = function aiLed(activity) {
  const color =
    activity === "ACTIVE"
      ? "led-on"
      : activity === "NOT_TESTED"
        ? "led-yellow"
        : "led-off";

  return `<span class="led ${color}"></span>`;
};

function btnDefault(isDefault, action, dataset) {
  if (isDefault) {
    return `<span class="ai-tag-default">default</span>`;
  }

  const data = Object.entries(dataset)
    .map(([k, v]) => `data-${k}="${v}"`)
    .join(" ");

  return `<button class="btn-bright" data-action="${action}" ${data}>set default</button>`;
}


// --------------------------------------------------------------------------------
// COMPONENTS
// --------------------------------------------------------------------------------

function modelCard(provider, m) {
  return `
    <div class="ai-model-card">

      <div class="ai-model-header">

        <div class="ai-model-title">
          ${aiLed(m.active)}
          <span class="ai-model-name">${m.name}</span>
        </div>

        <div class="ai-model-actions">

          <button
            class="btn-bright"
            data-action="test-model"
            data-provider="${provider}"
            data-model="${m.name}">
            test
          </button>

          ${btnDefault(
      m.default,
      "set-default-model",
      {provider, model: m.name}
  )}

        </div>
      </div>

      <div class="ai-model-desc">
        ${m.desc}
      </div>

    </div>
  `;
}

function providerCard(p) {
  return `
    <div class="ai-provider-card">

      <div class="ai-provider-header">

        <div class="ai-provider-title">
          ${aiLed(p.reachable)}
          <span class="ai-provider-name">${p.name}</span>
        </div>

        <div class="ai-provider-actions">

          <button
            class="btn-bright"
            data-action="test-provider"
            data-provider="${p.name}">
            test
          </button>

          ${btnDefault(
      p.default,
      "set-default-provider",
      {provider: p.name}
  )}

        </div>
      </div>

      <div class="ai-provider-info">

        <div class="ai-info-row">
          <span class="ai-info-label">Max Concurrent Requests</span>
          <span>${p.max_request}</span>
        </div>

        <div class="ai-info-row">
          <span class="ai-info-label">Method</span>
          <span>${p.api_method}</span>
        </div>

        <div class="ai-info-row">
          <span class="ai-info-label">URL</span>
          <span class="ai-info-url">${p.url}</span>
        </div>

      </div>

      <div class="ai-provider-models scrollbar">
        ${p.models.map(m => modelCard(p.name, m)).join("")}
      </div>

    </div>
  `;
}

function addonCard(a) {
  return `
    <div class="ai-addon-card ${a.enabled ? "addon-enabled" : ""}" id="addon-${a.id}">

      <div class="ai-addon-header">
        <span class="ai-addon-name">${a.name}</span>
      </div>

      <div class="ai-addon-desc">
        ${a.desc}
      </div>

      <div class="ai-addon-footer">

        <button
          class="ai-status-tag ${a.enabled ? "enabled" : "disabled"}"
          data-action="toggle-addon"
          data-addon="${a.id}">
          ${a.enabled ? "active" : "deactivate"}
        </button>

      </div>

    </div>
  `;
}


// --------------------------------------------------------------------------------
// RENDER
// --------------------------------------------------------------------------------

function renderProviders(providers) {
  const el = document.getElementById("ai-providers-list");
  if (el) el.innerHTML = providers.map(providerCard).join("");
}

function renderAddons(addons) {
  const el = document.getElementById("ai-addon-grid");
  if (el) el.innerHTML = addons.map(addonCard).join("");
}


// --------------------------------------------------------------------------------
// STATE
// --------------------------------------------------------------------------------

function saveState() {
  const activeTab = document.querySelector("#tab-list-ai .nav-link.active");

  if (activeTab) {
    sessionStorage.setItem("activeTab", activeTab.id);
  }

  sessionStorage.setItem("scrollY", window.scrollY);
}

function restoreState() {
  const tabId   = sessionStorage.getItem("activeTab");
  const scrollY = sessionStorage.getItem("scrollY");

  if (tabId) {
    document.getElementById(tabId)?.click();
    sessionStorage.removeItem("activeTab");
  }

  if (scrollY) {
    window.scrollTo(0, parseInt(scrollY));
    sessionStorage.removeItem("scrollY");
  }
}

document.addEventListener("DOMContentLoaded", restoreState);


// --------------------------------------------------------------------------------
// DATA
// --------------------------------------------------------------------------------

async function load() {

  const [providerRes, addonRes] = await Promise.all([
    window.get("core-ai-addon", "ai-provider-data"),
    window.get(ADDON_NAME, "")
  ]);

  providerData = providerRes;
  addonData    = addonRes;

  renderProviders(providerData.providers);
  renderAddons(addonData.addons);
}


// --------------------------------------------------------------------------------
// BUTTON LISTENERS
// --------------------------------------------------------------------------------

document
  .getElementById("ai-rescan-provider-btn")
  ?.addEventListener("click", () => {
    window.post(ADDON_NAME, "/provider/rescan");
  });

document
  .getElementById("ai-test-all-provider-btn")
  ?.addEventListener("click", () => {
    window.post(ADDON_NAME, "/provider/test_all");
  });

document
  .getElementById("ai-activate-all-addons-btn")
  ?.addEventListener("click", () => {
    reloadWithState(window.post(ADDON_NAME, "/addon/activate_all"));
  });

document
  .getElementById("ai-deactivate-all-addons-btn")
  ?.addEventListener("click", () => {
    reloadWithState(window.post(ADDON_NAME, "/addon/deactivate_all"));
  });