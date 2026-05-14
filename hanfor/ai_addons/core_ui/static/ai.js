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

function activateAddon(id) {
  reloadWithState(window.post(ADDON_NAME, "/addon/activate", { addon_id: id }));
}

function deactivateAddon(id) {
  reloadWithState(window.post(ADDON_NAME, "/addon/deactivate", { addon_id: id }));
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
  "activate-addon":       ({ addon })           => activateAddon(addon),
  "deactivate-addon":     ({ addon })           => deactivateAddon(addon)
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

// LED - Bootstrap badge dot
window.aiLed = function aiLed(activity) {
  const color =
    activity === "ACTIVE"      ? "bg-success" :
    activity === "NOT_TESTED"  ? "bg-warning"  :
                                 "bg-danger";
  return `<span class="badge rounded-pill ${color} p-1">&nbsp;</span>`;
};

function btnDefault(isDefault, action, dataset) {
  if (isDefault) {
    return `<span class="badge text-bg-success">default</span>`;
  }
  const data = Object.entries(dataset)
    .map(([k, v]) => `data-${k}="${v}"`)
    .join(" ");
  return `<button class="btn btn-outline-secondary btn-sm" data-action="${action}" ${data}>set default</button>`;
}


// --------------------------------------------------------------------------------
// COMPONENTS
// --------------------------------------------------------------------------------

function modelCard(provider, m) {
  return `
    <div class="card mb-2 border-0 bg-light">
      <div class="card-body py-2 px-3">
        <div class="d-flex align-items-center justify-content-between mb-1">
          <div class="d-flex align-items-center gap-2">
            ${aiLed(m.active)}
            <span class="fw-semibold small">${m.name}</span>
          </div>
          <div class="d-flex align-items-center gap-1">
            <button class="btn btn-outline-secondary btn-sm"
              data-action="test-model"
              data-provider="${provider}"
              data-model="${m.name}">test</button>
            ${btnDefault(m.default, "set-default-model", { provider, model: m.name })}
          </div>
        </div>
        <p class="text-muted mb-0" style="font-size:11px;">${m.desc}</p>
      </div>
    </div>
  `;
}

function providerCard(p) {
  return `
    <div class="card" style="width:340px; flex-shrink:0;">
      <div class="card-header d-flex align-items-center justify-content-between py-2">
        <div class="d-flex align-items-center gap-2">
          ${aiLed(p.reachable)}
          <span class="fw-semibold">${p.name}</span>
        </div>
        <div class="d-flex align-items-center gap-1">
          <button class="btn btn-outline-secondary btn-sm"
            data-action="test-provider"
            data-provider="${p.name}">test</button>
          ${btnDefault(p.default, "set-default-provider", { provider: p.name })}
        </div>
      </div>
      <ul class="list-group list-group-flush">
        <li class="list-group-item d-flex justify-content-between py-1 px-3" style="font-size:12px;">
          <span class="text-muted">Max Concurrent Requests</span>
          <span>${p.max_request}</span>
        </li>
        <li class="list-group-item d-flex justify-content-between py-1 px-3" style="font-size:12px;">
          <span class="text-muted">Method</span>
          <span>${p.api_method}</span>
        </li>
        <li class="list-group-item py-1 px-3" style="font-size:12px;">
          <span class="text-muted d-block">URL</span>
          <code style="font-size:11px; word-break:break-all;">${p.url}</code>
        </li>
      </ul>
      <div class="card-body p-2 overflow-auto" style="max-height:260px;">
        ${p.models.map(m => modelCard(p.name, m)).join("")}
      </div>
    </div>
  `;
}

function addonCard(a) {
  const borderClass = a.enabled ? "border-success" : "border-secondary";
  const btnClass    = a.enabled ? "btn-outline-danger" : "btn-outline-success";
  const btnAction   = a.enabled ? "deactivate-addon" : "activate-addon";
  const btnLabel    = a.enabled ? "Deactivate" : "Activate";

  return `
    <div class="col">
      <div class="card h-100 ${borderClass}" id="addon-${a.id}" style="border-left-width:4px;">
        <div class="card-body d-flex flex-column gap-2 py-2 px-3">
          <span class="fw-semibold">${a.name}</span>
          <p class="text-muted mb-0 flex-grow-1" style="font-size:12px;">${a.desc}</p>
          <div class="d-flex justify-content-end">
            <button class="btn btn-sm ${btnClass}"
              data-action="${btnAction}"
              data-addon="${a.id}">${btnLabel}</button>
          </div>
        </div>
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
  if (activeTab) sessionStorage.setItem("activeTab", activeTab.id);
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
    reloadWithState(window.post(ADDON_NAME, "addon/activate_all"));
  });

document
  .getElementById("ai-deactivate-all-addons-btn")
  ?.addEventListener("click", () => {
    reloadWithState(window.post(ADDON_NAME, "addon/deactivate_all"));
  });