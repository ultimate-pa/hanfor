const TAB_ID = "ai_addons_tag_mapper";
const ADDON_NAME = "tag-mapper";

let availableTags = [];
let providerCatalog = [];

const listEl = () => document.getElementById("tag-mapper-list");
const rowTemplate = () => document.getElementById("tag-mapping-row-template");

function debounce(fn, delayMs) {
    let timer = null;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delayMs);
    };
}

function findTag(name) {
    return availableTags.find((t) => t.name === name);
}


function updateTagColorDot(row) {
    const input = row.querySelector(".tag-search-input");
    const tag = findTag(input.value.trim());

    if (tag) {
        input.style.backgroundColor = tag.color;
        input.style.color = "#fff";
        input.style.borderColor = tag.color;
    } else {
        input.style.backgroundColor = "";
        input.style.color = "";
        input.style.borderColor = "";
    }
}

// -------------------------------------------------------------------------
// Provider / model selection
// -------------------------------------------------------------------------

const ACTIVITY_EMOJI = {
    ACTIVE: "🟢",
    NOT_TESTED: "🟡",
    INACTIVE: "🔴",
};

function activityEmoji(status) {
    return ACTIVITY_EMOJI[status] || "⚪";
}

async function loadProviderCatalog() {
    try {
        const data = await window.get("core-ai-addon", "ai-provider-data");
        providerCatalog = data.providers || [];
        renderProviderOptions();
    } catch (e) {
        if (e.message === "Addon is disabled") return;
        window.showBanner("Failed to load AI providers", "danger");
    }
}

async function loadSelection() {
    try {
        const selection = await window.get(ADDON_NAME, "selection");
        applySelectionToDropdowns(selection.provider, selection.model);
    } catch (e) {
        if (e.message !== "Addon is disabled") {
            window.showBanner("Failed to load AI selection", "danger");
        }
    }
}

function renderProviderOptions() {
    const select = document.getElementById("provider-select");

    if (providerCatalog.length === 0) {
        select.innerHTML = '<option value="">No providers available</option>';
        select.disabled = true;
        return;
    }

    select.disabled = false;
    select.innerHTML = "";
    providerCatalog.forEach((provider) => {
        const opt = document.createElement("option");
        opt.value = provider.name;
        opt.textContent = `${activityEmoji(provider.reachable)} ${provider.name}`;
        select.appendChild(opt);
    });
}

function renderModelOptions(providerName) {
    const modelSelect = document.getElementById("model-select");
    const provider = providerCatalog.find((p) => p.name === providerName);

    if (!provider) {
        modelSelect.innerHTML = '<option value="">-</option>';
        modelSelect.disabled = true;
        return;
    }

    const models = provider.models || [];
    if (models.length === 0) {
        modelSelect.innerHTML = '<option value="">No models available</option>';
        modelSelect.disabled = true;
        return;
    }

    modelSelect.disabled = false;
    modelSelect.innerHTML = "";
    models.forEach((model) => {
        const opt = document.createElement("option");
        opt.value = model.name;
        opt.textContent = `${activityEmoji(model.active)} ${model.name}`;
        modelSelect.appendChild(opt);
    });
}

function applySelectionToDropdowns(providerName, modelName) {
    document.getElementById("provider-select").value = providerName || "";
    renderModelOptions(providerName);
    document.getElementById("model-select").value = modelName || "";
}

async function persistSelection(providerName, modelName) {
    try {
        const selection = await window.post(ADDON_NAME, "selection", {
            provider: providerName || null,
            model: modelName || null,
        });
        applySelectionToDropdowns(selection.provider, selection.model);
    } catch (e) {
        if (e.message === "Addon is disabled") return;
        window.showBanner("Failed to update AI provider/model selection", "danger");
    }
}

async function onProviderChange() {
    const providerName = document.getElementById("provider-select").value;
    renderModelOptions(providerName);

    // Auto-pick the new provider's default model as a convenience.
    const provider = providerCatalog.find((p) => p.name === providerName);
    const defaultModel = provider ? (provider.models || []).find((m) => m.default) : null;
    const modelName = defaultModel ? defaultModel.name : "";
    document.getElementById("model-select").value = modelName;

    await persistSelection(providerName, modelName);
}

async function onModelChange() {
    const providerName = document.getElementById("provider-select").value;
    const modelName = document.getElementById("model-select").value;
    await persistSelection(providerName, modelName);
}

// -------------------------------------------------------------------------
// Rendering
// -------------------------------------------------------------------------

function renderMappings(mappings) {
    const list = listEl();
    list.innerHTML = "";
    mappings.forEach((mapping) => list.appendChild(buildRow(mapping)));
}

function buildRow(mapping) {
    const node = rowTemplate().content.firstElementChild.cloneNode(true);
    node.dataset.mappingId = mapping.id;

    const tagInput = node.querySelector(".tag-search-input");
    tagInput.value = mapping.tag || "";

    const promptInput = node.querySelector(".prompt-editor");
    promptInput.value = mapping.prompt || "";

    // Auto-save: debounced so we don't fire a request on every keystroke.
    // The backend itself throttles broadcasts to other clients separately.
    const debouncedSync = debounce(() => syncRow(node), 500);
    tagInput.addEventListener("input", debouncedSync);
    tagInput.addEventListener("input", () => updateTagColorDot(node));
    promptInput.addEventListener("input", debouncedSync);

    setupTagSelector(node, tagInput, () => {
        updateTagColorDot(node);
        syncRow(node);
    });

    updateTagColorDot(node);
    applyMappingStatus(node, mapping);

    node.querySelector(".btn-run-mapping").addEventListener("click", () => runMapping(node));
    node.querySelector(".btn-delete-mapping").addEventListener("click", () => deleteMapping(node));

    return node;
}

/** Merge a freshly-broadcast mapping list into the DOM without disturbing
 * whatever the current user is actively typing in. */
function applyIncomingMappings(mappings) {
    const activeElement = document.activeElement;
    const activeRow = activeElement ? activeElement.closest(".tag-mapping-row") : null;
    const activeMappingId = activeRow ? activeRow.dataset.mappingId : null;

    const incomingIds = new Set(mappings.map((m) => String(m.id)));

    Array.from(document.querySelectorAll(".tag-mapping-row")).forEach((row) => {
        if (!incomingIds.has(row.dataset.mappingId)) row.remove();
    });

    mappings.forEach((mapping) => {
        const idStr = String(mapping.id);
        const existingRow = findRowByMappingId(idStr);

        if (!existingRow) {
            listEl().appendChild(buildRow(mapping));
            return;
        }

        // Run status + assignment log are always fresh, even while this row is being edited.
        applyMappingStatus(existingRow, mapping);

        if (idStr === activeMappingId) return; // don't clobber tag/prompt text being typed right now

        const tagInput = existingRow.querySelector(".tag-search-input");
        const promptInput = existingRow.querySelector(".prompt-editor");
        if (document.activeElement !== tagInput && tagInput.value !== mapping.tag) {
            tagInput.value = mapping.tag;
            updateTagColorDot(existingRow);
        }
        if (document.activeElement !== promptInput && promptInput.value !== mapping.prompt) {
            promptInput.value = mapping.prompt;
        }
    });
}

// -------------------------------------------------------------------------
// Tag selector - search existing tags, create new ones on the fly
// -------------------------------------------------------------------------

function setupTagSelector(row, input, onTagChosen) {
    const menu = row.querySelector(".tag-dropdown-menu");
    const closeMenu = () => menu.classList.remove("show");

    const openMenu = () => {
        const query = input.value.trim().toLowerCase();
        const matches = availableTags.filter((t) => t.name.toLowerCase().includes(query));

        menu.innerHTML = "";

        matches.forEach((tag) => {
            const item = document.createElement("button");
            item.type = "button";
            item.className = "dropdown-item";

            const badge = document.createElement("span");
            badge.className = "badge";
            badge.style.backgroundColor = tag.color;
            badge.textContent = tag.name;
            item.appendChild(badge);

            item.addEventListener("mousedown", (e) => {
                e.preventDefault();
                input.value = tag.name;
                closeMenu();
                onTagChosen();
            });
            menu.appendChild(item);
        });

        const exactMatch = availableTags.some((t) => t.name.toLowerCase() === query);
        if (query && !exactMatch) {
            const createItem = document.createElement("button");
            createItem.type = "button";
            createItem.className = "dropdown-item text-primary";
            createItem.textContent = `Create new tag "${input.value.trim()}"`;
            createItem.addEventListener("mousedown", async (e) => {
                e.preventDefault();
                const newTag = input.value.trim();
                await createTag(newTag);
                input.value = newTag;
                closeMenu();
                onTagChosen();
            });
            menu.appendChild(createItem);
        }

        menu.classList.toggle("show", matches.length > 0 || (query && !exactMatch));
    };

    input.addEventListener("focus", openMenu);
    input.addEventListener("input", openMenu);
    input.addEventListener("blur", () => setTimeout(closeMenu, 150));
}

async function createTag(name) {
    if (!name) return;
    try {
        const result = await window.post(ADDON_NAME, "tags", { name });
        if (result.created) {
            window.showBanner(`Tag "${name}" created`, "success");
        }
    } catch (e) {
        if (e.message === "Addon is disabled") return;
        window.showBanner("Failed to create tag", "danger");
    }
}

// -------------------------------------------------------------------------
// Data loading
// -------------------------------------------------------------------------

async function loadMappings() {
    try {
        const mappings = await window.get(ADDON_NAME, "mappings");
        renderMappings(mappings || []);
    } catch (e) {
        if (e.message === "Addon is disabled") return;
        window.showBanner("Failed to load mappings", "danger");
    }
}

async function loadTags() {
    try {
        availableTags = (await window.get("", "tags")) || [];
    } catch (e) {
        if (e.message !== "Addon is disabled") {
            window.showBanner("Failed to load tags", "danger");
        }
    }
}

function collectRowData(row) {
    return {
        id: row.dataset.mappingId ? Number(row.dataset.mappingId) : null,
        tag: row.querySelector(".tag-search-input").value.trim(),
        prompt: row.querySelector(".prompt-editor").value,
    };
}

// -------------------------------------------------------------------------
// Mapping actions
// -------------------------------------------------------------------------

async function addMapping() {
    try {
        await window.post(ADDON_NAME, "mappings", { tag: "", prompt: "" });
        // Row appears once "socket_tag_mapper_mappings_updated" comes back.
    } catch (e) {
        if (e.message === "Addon is disabled") return;
        window.showBanner("Failed to add mapping", "danger");
    }
}

async function deleteMapping(row) {
    const mappingId = row.dataset.mappingId;
    try {
        if (mappingId) {
            await window.del(ADDON_NAME, `mappings/${mappingId}`);
        }
        row.remove();
    } catch (e) {
        if (e.message === "Addon is disabled") return;
        window.showBanner("Failed to delete mapping", "danger");
    }
}

/** Push a single row's current tag/prompt to the backend. Called debounced
 * while typing, and immediately on discrete actions (tag picked, run clicked). */
async function syncRow(row) {
    const mappingId = row.dataset.mappingId;
    if (!mappingId) return;

    const data = collectRowData(row);
    try {
        await window.post(ADDON_NAME, `mappings/${mappingId}/update`, { tag: data.tag, prompt: data.prompt });
    } catch (e) {
        if (e.message === "Addon is disabled") return;
        window.showBanner("Failed to save mapping", "danger");
    }
}

function flushAllRows() {
    return Promise.all(Array.from(document.querySelectorAll(".tag-mapping-row")).map(syncRow));
}

async function saveConfiguration() {
    try {
        await flushAllRows();
        await window.post(ADDON_NAME, "save");
        window.showBanner("Configuration saved", "success");
    } catch (e) {
        if (e.message === "Addon is disabled") return;
        window.showBanner("Failed to save configuration", "danger");
    }
}

async function runMapping(row) {
    const mappingId = row.dataset.mappingId;
    if (!mappingId) return;

    setRowRunning(row, true);

    try {
        await syncRow(row);
        await window.post(ADDON_NAME, `run/${mappingId}`);
    } catch (e) {
        setRowRunning(row, false);
        if (e.message === "Addon is disabled") return;
        window.showBanner("Failed to run mapping", "danger");
    }
}

async function runAll() {
    try {
        await flushAllRows();
        document.querySelectorAll(".tag-mapping-row").forEach((row) => setRowRunning(row, true));
        await window.post(ADDON_NAME, "run-all");
    } catch (e) {
        if (e.message === "Addon is disabled") return;
        window.showBanner("Failed to run all mappings", "danger");
    }
}

function setRowRunning(row, running) {
    row.querySelector(".run-spinner").classList.toggle("d-none", !running);
    row.querySelector(".btn-run-mapping").disabled = running;
}

function findRowByMappingId(mappingId) {
    return document.querySelector(`.tag-mapping-row[data-mapping-id="${mappingId}"]`);
}

function refreshAllTagColorDots() {
    document.querySelectorAll(".tag-mapping-row").forEach(updateTagColorDot);
}

function applyMappingStatus(row, mapping) {
    setRowRunning(row, !!mapping.running);

    const statusEl = row.querySelector(".mapping-status");
    if (mapping.running) {
        const progress = mapping.progress || {};
        const progressText = progress.total ? ` (${progress.processed || 0}/${progress.total})` : "";
        const lastEvent = mapping.last_event ? ` - ${mapping.last_event}` : "";
        statusEl.textContent = `Running...${progressText}${lastEvent}`;
    } else if (mapping.assigned_requirements && mapping.assigned_requirements.length) {
        statusEl.textContent = `Assigned to: ${mapping.assigned_requirements.join(", ")}`;
    } else {
        statusEl.textContent = "";
    }
}

// -------------------------------------------------------------------------
// Socket - live progress, no page reload needed
// -------------------------------------------------------------------------

window.tabSubs.register(TAB_ID, [
    {
        event: "socket_tag_mapper_mappings_updated",
        handler: (data) => applyIncomingMappings(data || []),
    },
    {
        event: "socket_tag_mapper_tags_updated",
        handler: (data) => {
            availableTags = data || [];
            refreshAllTagColorDots();
        },
    },
    {
        event: "socket_tag_mapper_selection_updated",
        handler: (data) => applySelectionToDropdowns(data.provider, data.model),
    },
]);

// -------------------------------------------------------------------------
// Lifecycle
// -------------------------------------------------------------------------

window.tabSubs.onActivate(TAB_ID, async () => {
    await loadProviderCatalog();
    await loadSelection();
    await loadTags();
    await loadMappings();
});

// -------------------------------------------------------------------------
// Global buttons / controls
// -------------------------------------------------------------------------

document.getElementById("provider-select").addEventListener("change", onProviderChange);
document.getElementById("model-select").addEventListener("change", onModelChange);

document.getElementById("btn-add-mapping").addEventListener("click", addMapping);
document.getElementById("btn-save-config").addEventListener("click", saveConfiguration);
document.getElementById("btn-run-all").addEventListener("click", runAll);