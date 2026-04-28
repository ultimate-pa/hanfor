// --------------------------------------------------------------------------------
// CONFIG
// --------------------------------------------------------------------------------

const ADDON_NAME = "pattern-prediction";
const TAB_ID     = "ai_addons_pattern_prediction";

const QUESTION_NODE_WIDTH  = 200;
const QUESTION_NODE_HEIGHT = 56;
const ANSWER_NODE_WIDTH    = 100;
const ANSWER_NODE_HEIGHT   = 34;
const PATTERN_NODE_WIDTH   = 210;
const PATTERN_NODE_HEIGHT  = 54;
const HORIZONTAL_GAP       = 60;
const VERTICAL_GAP         = 80;
const SVG_NS               = "http://www.w3.org/2000/svg";


// --------------------------------------------------------------------------------
// STATE
// --------------------------------------------------------------------------------

let treeData;
let requestIds;
let svgElement      = null;
let activeTrace     = null;
let nodeRegistry    = {};
let chosenId;
let ensembleEntries    = [];
let ensembleIdCounter  = 0;
let providerData       = [];
let treefiles;
let selectedFile;
let panX = 40, panY = 40, zoomScale = 1.0;
let isPanning = false, panStartX = 0, panStartY = 0;
let canvasWidth = 0, canvasHeight = 0;

const predictButton = document.getElementById("pp-predict-pattern-btn");
const searchInput   = document.getElementById("pp-trace-search");
const treeInput     = document.getElementById("pp-tree-search");
const treeList      = document.getElementById("pp-tree-list");


// --------------------------------------------------------------------------------
// SOCKET SUBSCRIPTIONS
// --------------------------------------------------------------------------------

window.tabSubs.register(TAB_ID, [
  {
    event:   "socket_provider_info",
    handler: ({ providers }) => {
      if (providers) {
        providerData = providers;
        renderEnsembleList();
      }
    }
  },
  {
    event:   "socket_pattern_prediction",
    handler: newData => {
      if (newData) { applyTraceHighlighting(newData); renderTraceInfoBlock(newData); }
    }
  },
  {
    event:   "socket_pattern_prediction_error",
    handler: ({ error } = {}) => { if (error) showErrorBanner(error); }
  },
  {
    event:   "socket_pattern_prediction_ensemble",
    handler: newData => {
      ensembleEntries   = newData.ensemble;
      ensembleIdCounter = ensembleEntries.length;
      renderEnsembleList();
    }
  },
  {
    event:   "socket_pattern_prediction_new_tree",
    handler: newTree => {
      treeData        = newTree.tree;
      selectedFile    = newTree.file;
      treeInput.value = selectedFile ?? "";
      renderTree();
      renderTreeList(treefiles);
    }
  }
]);

window.tabSubs.onActivate(TAB_ID, () => {
  loadTreeData();
  loadProviderData();
  setTimeout(resetZoom, 100);
});

window.tabSubs.onDeactivate(TAB_ID, async () => {
  document.getElementById("pp-clear-trace-btn").click();
  await window.del(ADDON_NAME, "trace-sid", { req_id: chosenId, sid: window.appSocket.id });
});


// --------------------------------------------------------------------------------
// ACTIONS
// --------------------------------------------------------------------------------

function applyTrace(requestId) {
  if (requestId === null) {
    applyTraceHighlighting(null);
    removeTraceInfoBlock();
    window.del(ADDON_NAME, "trace-sid", { req_id: chosenId, sid: window.appSocket.id });
  } else {
    window.post(ADDON_NAME, "trace-sid", { req_id: requestId, sid: window.appSocket.id });
  }
}

function showErrorBanner(message) {
  window.showBanner(`<strong>Prediction error:</strong> ${message}`, "danger", "prediction-error-banner");
}


// --------------------------------------------------------------------------------
// ACTION ROUTER (EVENT DELEGATION)
// --------------------------------------------------------------------------------

document.getElementById("pp-zoom-in").onclick    = () => { zoomScale = Math.min(3,   zoomScale * 1.2); applyCanvasTransform(); };
document.getElementById("pp-zoom-out").onclick   = () => { zoomScale = Math.max(0.1, zoomScale / 1.2); applyCanvasTransform(); };
document.getElementById("pp-zoom-reset").onclick = resetZoom;

document.getElementById("pp-clear-trace-btn").onclick = () => {
  activeTrace            = null;
  searchInput.value      = "";
  predictButton.disabled = true;
  applyTrace(null);
};

predictButton.onclick = async () => {
  await window.post(ADDON_NAME, "generate-trace/" + encodeURIComponent(chosenId));
};

document.getElementById("pp-predict-pattern-all-btn").addEventListener("click", async () => {
  await window.post(ADDON_NAME, "generate-trace/__all__");
});

document.getElementById("pp-rescan-provider-btn")?.addEventListener("click", () => {
  window.post(ADDON_NAME, "/provider/rescan");
});

document.getElementById("pp-add-ensemble-entry-btn").addEventListener("click", () => {
  ensembleEntries.push({ id: ++ensembleIdCounter, provider: null, model: null, count: 1, weight: 1 });
  renderEnsembleList();
});

document.getElementById("pp-save-ensemble-entry-btn").addEventListener("click", async () => {
  await window.post(ADDON_NAME, "ensemble", { ensemble: ensembleEntries });
});

document.getElementById("pp-download-svg-btn").addEventListener("click", () => {
  const svg   = document.getElementById("pp-tree-svg");
  const clone = svg.cloneNode(true);

  const styleEl = document.createElementNS(SVG_NS, "style");
  styleEl.textContent = Array.from(document.styleSheets)
    .flatMap(sheet => { try { return Array.from(sheet.cssRules).map(r => r.cssText); } catch { return []; } })
    .join("\n");
  clone.insertBefore(styleEl, clone.firstChild);

  const svgStr = '<?xml version="1.0" encoding="UTF-8"?>\n' + new XMLSerializer().serializeToString(clone);
  const url    = URL.createObjectURL(new Blob([svgStr], { type: "image/svg+xml;charset=utf-8" }));
  const a      = Object.assign(document.createElement("a"), { href: url, download: "tree.svg" });
  a.click();
  URL.revokeObjectURL(url);
});

document.getElementById("pp-download-detailed-traces-btn").addEventListener("click", async () => {
  const response = await window.get(ADDON_NAME, "detailed-traces-file", { raw: true });
  const blob = await response.blob();
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement("a");
  a.href     = url;
  a.download = "detailed_traces.json";
  a.click();
  URL.revokeObjectURL(url);
});

document.getElementById("pp-open-settings-btn").addEventListener("click", () => {
  document.getElementById("pp-settings-overlay").hidden = false;
});

document.getElementById("pp-close-settings-btn").addEventListener("click", closeSettings);

document.getElementById("pp-settings-overlay").addEventListener("click", e => {
  if (e.target === e.currentTarget) closeSettings();
});

document.addEventListener("keydown", e => {
  if (e.key === "Escape") closeSettings();
});


// --------------------------------------------------------------------------------
// HELPERS
// --------------------------------------------------------------------------------

function ledEmoji(activity) {
  if (activity === "ACTIVE")     return "🟢";
  if (activity === "NOT_TESTED") return "🟡";
  return "🔴";
}

function wrapTextIntoLines(lines, nodeWidth) {
  const maxPx = nodeWidth - 16;
  const result = [];
  lines.forEach(line => {
    const words = line.split(" ");
    let current = "";
    words.forEach(word => {
      const candidate = current ? `${current} ${word}` : word;
      if (candidate.length * 7 > maxPx && current) {
        result.push(current);
        current = word;
      } else {
        current = candidate;
      }
    });
    if (current) result.push(current);
  });
  return result;
}

function calcDynamicHeight(text, nodeWidth, minHeight, topPad, lineHeight, bottomPad) {
  const lines = wrapTextIntoLines([text], nodeWidth);
  return Math.max(minHeight, topPad + lines.length * lineHeight + bottomPad);
}

function svgRect(x, y, w, h, rx) {
  const r = document.createElementNS(SVG_NS, "rect");
  r.setAttribute("x", x);   r.setAttribute("y", y);
  r.setAttribute("width", w); r.setAttribute("height", h);
  r.setAttribute("rx", rx);
  return r;
}

function svgText(x, y, content, anchor = "middle") {
  const t = document.createElementNS(SVG_NS, "text");
  t.setAttribute("x", x);           t.setAttribute("y", y);
  t.setAttribute("text-anchor", anchor);
  t.textContent = content;
  return t;
}

function ensembleProviderReachable(providerName) {
  const p = providerData.find(p => p.name === providerName);
  return p ? p.reachable : null;
}

function ensembleModelReachable(providerName, modelName) {
  const p = providerData.find(p => p.name === providerName);
  if (!p) return null;
  const m = p.models.find(m => (typeof m === "string" ? m : m.name) === modelName);
  if (!m || typeof m === "string") return null;
  return m.active ?? null;
}

function closeSettings() {
  document.getElementById("pp-settings-overlay").hidden = true;
  document.querySelectorAll("#pp-provider-list, #pp-model-list, .pp-ensemble-dropdown-list")
    .forEach(el => el.classList.remove("open"));
}


// --------------------------------------------------------------------------------
// LAYOUT ENGINE
// --------------------------------------------------------------------------------

function assignNodeLevels(node, level, parentId) {
  if (!node) return;
  node._level    = level;
  node._parentId = parentId;
  nodeRegistry[node.id] = node;

  if (!node.answers) return;
  node.answers.forEach(answer => {
    answer._answerId         = `ans_${node.id}_${answer.answer.replace(/\s/g, "_")}`;
    answer._parentQuestionId = node.id;
    nodeRegistry[answer._answerId] = answer;
    assignNodeLevels(answer.next, level + 2, answer._answerId);
  });
}

function calculateNodePositions(node, offsetX, depth, startY = 0) {
  if (!node) return 0;

  if (node.pattern !== undefined) {
    node._x      = offsetX;
    node._y      = startY;
    node._height = calcDynamicHeight(node.pattern, PATTERN_NODE_WIDTH, PATTERN_NODE_HEIGHT, 14, 15, 10);
    return PATTERN_NODE_WIDTH;
  }

  if (node.answers) {
    node._height = calcDynamicHeight(node.question, QUESTION_NODE_WIDTH, QUESTION_NODE_HEIGHT, 10, 15, 10);
    node._x      = offsetX;
    node._y      = startY;

    const answerRowY = startY + node._height + VERTICAL_GAP;
    const childRowY  = answerRowY + ANSWER_NODE_HEIGHT + VERTICAL_GAP;

    let totalWidth = 0;
    const childCenterXs = [];

    node.answers.forEach(answer => {
      const childWidth = calculateNodePositions(answer.next, offsetX + totalWidth, depth + 2, childRowY);
      childCenterXs.push(offsetX + totalWidth + childWidth / 2);
      totalWidth += childWidth + HORIZONTAL_GAP;
    });
    totalWidth -= HORIZONTAL_GAP;

    node._x = (childCenterXs[0] + childCenterXs[childCenterXs.length - 1]) / 2 - QUESTION_NODE_WIDTH / 2;
    node.answers.forEach((answer, i) => {
      answer._x = childCenterXs[i] - ANSWER_NODE_WIDTH / 2;
      answer._y = answerRowY;
    });

    return totalWidth;
  }
}


// --------------------------------------------------------------------------------
// COMPONENTS
// --------------------------------------------------------------------------------

function drawQuestionNode(parentGroup, node) {
  const group  = document.createElementNS(SVG_NS, "g");
  group.setAttribute("class", "pp-node-q");
  group.setAttribute("data-node-id", node.id);

  const h      = node._height ?? QUESTION_NODE_HEIGHT;
  const LINE_H = 15;
  const lines  = wrapTextIntoLines([node.question], QUESTION_NODE_WIDTH);
  const textH  = lines.length * LINE_H;
  const startY = node._y + (h - textH) / 2 + LINE_H;

  group.appendChild(svgRect(node._x, node._y, QUESTION_NODE_WIDTH, h, 8));
  lines.forEach((line, i) =>
    group.appendChild(svgText(node._x + QUESTION_NODE_WIDTH / 2, startY + i * LINE_H, line))
  );
  parentGroup.appendChild(group);
}

function drawAnswerNode(parentGroup, answer) {
  const group = document.createElementNS(SVG_NS, "g");
  group.setAttribute("class", "pp-node-a");
  group.setAttribute("data-node-id", answer._answerId);

  group.appendChild(svgRect(answer._x, answer._y, ANSWER_NODE_WIDTH, ANSWER_NODE_HEIGHT, 20));
  group.appendChild(svgText(
    answer._x + ANSWER_NODE_WIDTH / 2,
    answer._y + ANSWER_NODE_HEIGHT / 2 + 7,
    answer.answer
  ));
  parentGroup.appendChild(group);
}

function drawPatternNode(parentGroup, node) {
  const group  = document.createElementNS(SVG_NS, "g");
  group.setAttribute("class", "pp-node-p");
  group.setAttribute("data-node-id", node.id);

  const h      = node._height ?? PATTERN_NODE_HEIGHT;
  const LINE_H = 15;
  const lines  = wrapTextIntoLines([node.pattern], PATTERN_NODE_WIDTH);
  const textH  = lines.length * LINE_H;
  const startY = node._y + (h - textH) / 2 + LINE_H;

  group.appendChild(svgRect(node._x, node._y, PATTERN_NODE_WIDTH, h, 8));

  const label = document.createElementNS(SVG_NS, "text");
  label.setAttribute("x",           node._x + PATTERN_NODE_WIDTH / 2);
  label.setAttribute("y",           node._y + 14);
  label.setAttribute("text-anchor", "middle");
  label.setAttribute("fill",        "#607899");
  label.setAttribute("font-size",   "9");
  group.appendChild(label);

  lines.forEach((line, i) =>
    group.appendChild(svgText(node._x + PATTERN_NODE_WIDTH / 2, startY + i * LINE_H, line))
  );
  parentGroup.appendChild(group);
}

function ensembleEntryCard(entry) {
  const provReachable = entry.provider ? ensembleProviderReachable(entry.provider) : null;
  const modReachable  = (entry.provider && entry.model) ? ensembleModelReachable(entry.provider, entry.model) : null;

  const provDisplay = entry.provider ? `${ledEmoji(provReachable)} ${entry.provider}` : "";
  const modDisplay  = entry.model    ? `${ledEmoji(modReachable)} ${entry.model}`    : "";

  const el = document.createElement("div");
  el.className = "pp-ensemble-entry";

  el.innerHTML = `
    <div class="pp-ensemble-entry-main">

      <div class="pp-ensemble-entry-left">

        <div class="pp-ensemble-entry-fields">
          <div class="search-dropdown half" data-role="provider">
            <input class="pp-provider-input search"
                   type="text"
                   placeholder="Provider…"
                   readonly
                   value="${provDisplay}">
            <div class="search-list pp-provider-list"></div>
          </div>

          <div class="search-dropdown half" data-role="model">
            <input class="pp-model-input search"
                   type="text"
                   placeholder="Model…"
                   readonly
                   value="${modDisplay}"
                   ${entry.provider ? "" : "disabled"}>
            <div class="search-list pp-model-list"></div>
          </div>
        </div>

        <div class="pp-ensemble-entry-nums">
          <div class="pp-ensemble-num-wrap">
            <div class="pp-ensemble-num-label">Count</div>
            <input class="pp-ensemble-count-input search" type="number" min="1" step="1" value="${entry.count}">
          </div>

          <div class="pp-ensemble-num-wrap">
            <div class="pp-ensemble-num-label">Weight</div>
            <input class="pp-ensemble-weight-input search" type="number" min="0" step="0.1" value="${entry.weight}">
          </div>
        </div>

      </div>

      <button class="pp-ensemble-remove-btn btn" id="pp-ensemble-close-btn">X</button>

    </div>
  `;

  const provInput   = el.querySelector(".pp-provider-input");
  const provList    = el.querySelector(".pp-provider-list");
  const modInput    = el.querySelector(".pp-model-input");
  const modList     = el.querySelector(".pp-model-list");
  const countInput  = el.querySelector(".pp-ensemble-count-input");
  const weightInput = el.querySelector(".pp-ensemble-weight-input");

  provInput.addEventListener("click", () => {
    document.querySelectorAll(".search-list").forEach(d => d.classList.remove("open"));
    buildEnsembleProviderList(provList, entry);
    provList.classList.add("open");
  });

  modInput.addEventListener("click", () => {
    if (!entry.provider) return;
    document.querySelectorAll(".search-list").forEach(d => d.classList.remove("open"));
    buildEnsembleModelList(modList, entry);
    modList.classList.add("open");
  });

  countInput.addEventListener("change", e => {
    entry.count    = Math.max(1, parseInt(e.target.value) || 1);
    e.target.value = entry.count;
  });

  weightInput.addEventListener("change", e => {
    const v        = parseFloat(e.target.value);
    entry.weight   = isNaN(v) ? 1 : Math.max(0, v);
    e.target.value = entry.weight;
  });

  el.querySelector(".pp-ensemble-remove-btn").addEventListener("click", () => {
    ensembleEntries = ensembleEntries.filter(en => en.id !== entry.id);
    renderEnsembleList();
  });

  return el;
}

function buildEnsembleProviderList(listEl, entry) {
  listEl.innerHTML = "";
  providerData.forEach(p => {
    const item = document.createElement("div");
    item.className = "search-list-item" + (entry.provider === p.name ? " active" : "");
    item.innerHTML = `<div class="trace-id">${ledEmoji(p.reachable)} ${p.name}</div>`;
    item.addEventListener("click", e => {
      e.stopPropagation();
      entry.provider = p.name;
      entry.model    = null;
      listEl.classList.remove("open");
      renderEnsembleList();
    });
    listEl.appendChild(item);
  });
}

function buildEnsembleModelList(listEl, entry) {
  listEl.innerHTML = "";
  const prov = providerData.find(p => p.name === entry.provider);
  if (!prov) return;
  prov.models.forEach(m => {
    const name      = typeof m === "string" ? m : m.name;
    const reachable = typeof m === "string" ? null : (m.active ?? null);
    const item      = document.createElement("div");
    item.className  = "search-list-item" + (entry.model === name ? " active" : "");
    item.innerHTML  = `<div class="trace-id">${reachable !== null ? ledEmoji(reachable) : ""} ${name}</div>`;
    item.addEventListener("click", e => {
      e.stopPropagation();
      entry.model = name;
      listEl.classList.remove("open");
      renderEnsembleList();
    });
    listEl.appendChild(item);
  });
}


// --------------------------------------------------------------------------------
// RENDER
// --------------------------------------------------------------------------------

function renderTree() {
  nodeRegistry = {};
  assignNodeLevels(treeData, 0, null);
  calculateNodePositions(treeData, 0, 0, 0);

  svgElement = document.getElementById("pp-tree-svg");

  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  Object.values(nodeRegistry).forEach(node => {
    if (node._x === undefined) return;
    const w = node.pattern  ? PATTERN_NODE_WIDTH  : (node.answers ? QUESTION_NODE_WIDTH  : ANSWER_NODE_WIDTH);
    const h = node._height  ?? (node.pattern ? PATTERN_NODE_HEIGHT : (node.answers ? QUESTION_NODE_HEIGHT : ANSWER_NODE_HEIGHT));
    minX = Math.min(minX, node._x);
    maxX = Math.max(maxX, node._x + w);
    minY = Math.min(minY, node._y);
    maxY = Math.max(maxY, node._y + h);
  });

  const PAD         = 60;
  const totalWidth  = maxX - minX + PAD * 2;
  const totalHeight = maxY - minY + PAD * 2;

  svgElement.setAttribute("width",  totalWidth);
  svgElement.setAttribute("height", totalHeight);
  svgElement.innerHTML = "";

  const rootGroup = document.createElementNS(SVG_NS, "g");
  rootGroup.setAttribute("transform", `translate(${PAD - minX},${PAD - minY})`);
  svgElement.appendChild(rootGroup);

  drawEdges(rootGroup, treeData);
  drawNodes(rootGroup, treeData);

  initPanZoom(totalWidth, totalHeight);
  updateMinimap(totalWidth, totalHeight);
}

function renderEnsembleList() {
  const container = document.getElementById("pp-ensemble-list");
  container.innerHTML = "";
  ensembleEntries.forEach(entry => container.appendChild(ensembleEntryCard(entry)));
}

function renderTreeList(files) {
  treeList.innerHTML = "";
  files.forEach(filename => {
    const item = document.createElement("div");
    item.className   = "search-list-item";
    item.textContent = filename;
    item.addEventListener("click", () => {
      treeList.classList.remove("open");
      window.post(ADDON_NAME, "tree-file", { file: filename });
    });
    treeList.appendChild(item);
  });
}

function renderTraceInfoBlock(traceData) {
  let infoBlock = document.getElementById("pp-trace-info-block");

  if (!infoBlock) {
    infoBlock = document.createElement("div");
    infoBlock.id        = "pp-trace-info-block";
    infoBlock.className = "pp-trace-info-block scrollbar";

    const toggleBtn = document.createElement("button");
    toggleBtn.textContent = "−";
    toggleBtn.className   = "btn";
    toggleBtn.id = "pp-trace-toggle-btn";
    toggleBtn.onclick = () => {
      const content   = infoBlock.querySelector(".trace-content");
      const collapsed = content.style.display === "none";
      content.style.display = collapsed ? "block" : "none";
      toggleBtn.textContent = collapsed ? "−" : "+";
      infoBlock.classList.toggle("minimized", !collapsed);
    };

    const contentEl = document.createElement("div");
    contentEl.className = "trace-content";
    infoBlock.appendChild(toggleBtn);
    infoBlock.appendChild(contentEl);
    document.getElementById("pp-canvas-wrap").appendChild(infoBlock);
    infoBlock.addEventListener("wheel", e => e.stopPropagation());
  }

  const patternText = traceData.pattern && traceData.pattern !== "none" ? traceData.pattern : "none";
  infoBlock.querySelector(".trace-content").innerHTML =
    `<strong>Description:</strong> ${traceData.desc || "–"}<br><br><strong>Pattern:</strong> ${patternText}`;
}

function removeTraceInfoBlock() {
  document.getElementById("pp-trace-info-block")?.remove();
}


// --------------------------------------------------------------------------------
// EDGES & NODES
// --------------------------------------------------------------------------------

function drawEdges(parentGroup, node) {
  if (!node?.answers) return;
  node.answers.forEach(answer => {
    drawEdge(parentGroup, node,   answer,      "question-to-answer");
    if (answer.next) {
      drawEdge(parentGroup, answer, answer.next, "answer-to-next");
      drawEdges(parentGroup, answer.next);
    }
  });
}

function drawEdge(parentGroup, fromNode, toNode, edgeType) {
  if (fromNode._x === undefined || toNode._x === undefined) return;

  let x1, y1, x2, y2;
  if (edgeType === "question-to-answer") {
    const fromH = fromNode._height ?? QUESTION_NODE_HEIGHT;
    x1 = fromNode._x + QUESTION_NODE_WIDTH / 2;
    y1 = fromNode._y + fromH;
    x2 = toNode._x   + ANSWER_NODE_WIDTH  / 2;
    y2 = toNode._y;
  } else {
    const toW = toNode.answers ? QUESTION_NODE_WIDTH : (toNode.pattern ? PATTERN_NODE_WIDTH : ANSWER_NODE_WIDTH);
    x1 = fromNode._x + ANSWER_NODE_WIDTH / 2;
    y1 = fromNode._y + ANSWER_NODE_HEIGHT;
    x2 = toNode._x   + toW / 2;
    y2 = toNode._y;
  }

  const cy   = (y1 + y2) / 2;
  const path = document.createElementNS(SVG_NS, "path");
  path.setAttribute("d",            `M${x1},${y1} C${x1},${cy} ${x2},${cy} ${x2},${y2}`);
  path.setAttribute("class",        "pp-edge");
  path.setAttribute("data-edge-id", `edge_${fromNode.id || fromNode._answerId}_${toNode.id || toNode._answerId}`);
  parentGroup.appendChild(path);
}

function drawNodes(parentGroup, node) {
  if (!node) return;
  if (node.pattern !== undefined) { drawPatternNode(parentGroup, node); return; }
  if (node.answers) {
    drawQuestionNode(parentGroup, node);
    node.answers.forEach(answer => {
      drawAnswerNode(parentGroup, answer);
      drawNodes(parentGroup, answer.next);
    });
  }
}


// --------------------------------------------------------------------------------
// TRACE HIGHLIGHTING
// --------------------------------------------------------------------------------

function applyTraceHighlighting(traceData) {
  if (!svgElement) return;

  svgElement.querySelectorAll(
    ".trace-active, .trace-inactive, .trace-edge-active, .trace-edge-inactive"
  ).forEach(el => el.classList.remove("trace-active", "trace-inactive", "trace-edge-active", "trace-edge-inactive"));
  svgElement.querySelectorAll(".pp-prob-badge").forEach(el => el.remove());

  if (!traceData?.steps?.length) return;

  traceData.steps.forEach((step, stepIndex) => {
    const questionEl = svgElement.querySelector(`[data-node-id="${step.nodeId}"]`);
    if (questionEl) questionEl.classList.add("trace-active");

    Object.entries(step.confidences || {}).forEach(([answerText, confidence]) => {
      const answerNode = Object.values(nodeRegistry).find(
        n => n._parentQuestionId === step.nodeId && n.answer === answerText
      );
      if (!answerNode) return;

      const answerEdgeId       = answerNode.id || answerNode._answerId;
      const edgeQuestionAnswer = svgElement.querySelector(`[data-edge-id="edge_${step.nodeId}_${answerEdgeId}"]`);
      const answerEl           = svgElement.querySelector(`[data-node-id="${answerNode._answerId}"]`);

      if (answerEl) {
        const badge  = document.createElementNS(SVG_NS, "g");
        badge.setAttribute("class", "pp-prob-badge");

        const textEl = document.createElementNS(SVG_NS, "text");
        textEl.textContent = (confidence * 100).toFixed(0) + "%";
        textEl.setAttribute("text-anchor",        "middle");
        textEl.setAttribute("dominant-baseline",  "middle");

        const bgRect = document.createElementNS(SVG_NS, "rect");
        bgRect.setAttribute("rx", 4);
        bgRect.setAttribute("ry", 4);
        badge.appendChild(bgRect);
        badge.appendChild(textEl);
        svgElement.querySelector("g").appendChild(badge);

        const bb = textEl.getBBox();
        bgRect.setAttribute("width",  bb.width  + 8);
        bgRect.setAttribute("height", bb.height + 4);
        bgRect.setAttribute("x",     -(bb.width  + 8) / 2);
        bgRect.setAttribute("y",     -(bb.height + 4) / 2);
        badge.setAttribute("transform", `translate(${answerNode._x + ANSWER_NODE_WIDTH / 2},${answerNode._y - bb.height + 4})`);
      }

      const chosen = step.answer === answerText;
      if (chosen) {
        if (edgeQuestionAnswer) edgeQuestionAnswer.classList.add("trace-edge-active");
        if (answerEl)           answerEl.classList.add("trace-active");

        const nextNodeId = traceData.steps[stepIndex + 1]?.nodeId;
        if (nextNodeId) {
          const edgeAnswerNext = svgElement.querySelector(`[data-edge-id="edge_${answerEdgeId}_${nextNodeId}"]`);
          if (edgeAnswerNext) edgeAnswerNext.classList.add("trace-edge-active");
        }
      } else {
        if (edgeQuestionAnswer) edgeQuestionAnswer.classList.add("trace-edge-inactive");
        if (answerEl)           answerEl.classList.add("trace-inactive");
      }
    });
  });
}


// --------------------------------------------------------------------------------
// PAN / ZOOM
// --------------------------------------------------------------------------------

function applyCanvasTransform() {
  document.getElementById("pp-canvas").style.transform =
    `translate(${panX}px,${panY}px) scale(${zoomScale})`;
  updateMinimapViewport();
}

function initPanZoom(width, height) {
  canvasWidth  = width;
  canvasHeight = height;

  const wrapper = document.getElementById("pp-canvas-wrap");
  const vpW     = wrapper.clientWidth;
  const vpH     = wrapper.clientHeight;

  zoomScale = Math.min(1, (vpW - 80) / width, (vpH - 80) / height);
  panX = (vpW - width * zoomScale) / 2;
  panY = 30;
  applyCanvasTransform();

  // Mouse
  wrapper.addEventListener("mousedown", e => {
    if (e.button !== 0) return;
    isPanning = true;
    panStartX = e.clientX - panX;
    panStartY = e.clientY - panY;
    wrapper.classList.add("dragging");
  });
  wrapper.addEventListener("mousemove", e => {
    if (!isPanning) return;
    panX = e.clientX - panStartX;
    panY = e.clientY - panStartY;
    applyCanvasTransform();
  });
  wrapper.addEventListener("mouseup",    () => { isPanning = false; wrapper.classList.remove("dragging"); });
  wrapper.addEventListener("mouseleave", () => { isPanning = false; wrapper.classList.remove("dragging"); });

  // Wheel zoom
  wrapper.addEventListener("wheel", e => {
    if (e.target.closest(".trace-info-block")) return;
    e.preventDefault();
    const factor = e.deltaY > 0 ? 0.9 : 1.1;
    const bounds = wrapper.getBoundingClientRect();
    const mx = e.clientX - bounds.left;
    const my = e.clientY - bounds.top;
    panX      = mx - (mx - panX) * factor;
    panY      = my - (my - panY) * factor;
    zoomScale = Math.max(0.1, Math.min(3, zoomScale * factor));
    applyCanvasTransform();
  }, { passive: false });

  // Touch
  let lastPinchDist = null;
  wrapper.addEventListener("touchstart", e => {
    if (e.touches.length === 1) {
      isPanning = true;
      panStartX = e.touches[0].clientX - panX;
      panStartY = e.touches[0].clientY - panY;
    }
    if (e.touches.length === 2) lastPinchDist = null;
  });
  wrapper.addEventListener("touchmove", e => {
    e.preventDefault();
    if (e.touches.length === 1 && isPanning) {
      panX = e.touches[0].clientX - panStartX;
      panY = e.touches[0].clientY - panStartY;
      applyCanvasTransform();
    }
    if (e.touches.length === 2) {
      const dx   = e.touches[0].clientX - e.touches[1].clientX;
      const dy   = e.touches[0].clientY - e.touches[1].clientY;
      const dist = Math.hypot(dx, dy);
      if (lastPinchDist) {
        zoomScale = Math.max(0.1, Math.min(3, zoomScale * (dist / lastPinchDist)));
        applyCanvasTransform();
      }
      lastPinchDist = dist;
    }
  }, { passive: false });
  wrapper.addEventListener("touchend", () => { isPanning = false; lastPinchDist = null; });
}

function resetZoom() {
  const wrapper = document.getElementById("pp-canvas-wrap");
  if (!wrapper) return;
  const vpW = wrapper.clientWidth;
  const vpH = wrapper.clientHeight;
  zoomScale = Math.min(1, (vpW - 80) / canvasWidth, (vpH - 80) / canvasHeight);
  panX = (vpW - canvasWidth * zoomScale) / 2;
  panY = 30;
  applyCanvasTransform();
}


// --------------------------------------------------------------------------------
// MINIMAP
// --------------------------------------------------------------------------------

let lastTreeWidth = 0, lastTreeHeight = 0;

function getMinimapDimensions() {
  const mmContainer = document.getElementById("pp-minimap");
  return {
    w: mmContainer.offsetWidth,
    h: mmContainer.offsetHeight
  };
}

function updateMinimap(treeWidth, treeHeight) {
  if (treeWidth  !== undefined) lastTreeWidth  = treeWidth;
  if (treeHeight !== undefined) lastTreeHeight = treeHeight;
  treeWidth  = lastTreeWidth;
  treeHeight = lastTreeHeight;

  const { w: MINIMAP_W, h: MINIMAP_H } = getMinimapDimensions();
  const mmSvg = document.getElementById("pp-minimap-svg");

  const scale = Math.min(MINIMAP_W / treeWidth, MINIMAP_H / treeHeight);
  const offX  = (MINIMAP_W - treeWidth  * scale) / 2;
  const offY  = (MINIMAP_H - treeHeight * scale) / 2;

  mmSvg.innerHTML = "";
  const group = document.createElementNS(SVG_NS, "g");
  group.setAttribute("transform", `translate(${offX},${offY}) scale(${scale})`);

  Object.values(nodeRegistry).forEach(node => {
    if (node._x === undefined) return;
    const isQ = !!node.answers;
    const isP = node.pattern !== undefined;
    const w   = isP ? PATTERN_NODE_WIDTH : (isQ ? QUESTION_NODE_WIDTH  : ANSWER_NODE_WIDTH);
    const h   = node._height ?? (isP ? PATTERN_NODE_HEIGHT : (isQ ? QUESTION_NODE_HEIGHT : ANSWER_NODE_HEIGHT));
    const r   = document.createElementNS(SVG_NS, "rect");
    r.setAttribute("x",       node._x); r.setAttribute("y",      node._y);
    r.setAttribute("width",   w);       r.setAttribute("height", h);
    r.setAttribute("rx",      4);       r.setAttribute("opacity", "0.8");
    r.setAttribute("fill",    isP ? "#2b6cb0" : (isQ ? "#3a3a38" : "#1a3a2a"));
    group.appendChild(r);
  });

  mmSvg.appendChild(group);
  updateMinimapViewport();
}

function updateMinimapViewport() {
  const { w: MINIMAP_W, h: MINIMAP_H } = getMinimapDimensions();
  const wrapper = document.getElementById("pp-canvas-wrap");

  const scale = Math.min(MINIMAP_W / canvasWidth, MINIMAP_H / canvasHeight);
  const offX  = (MINIMAP_W - canvasWidth  * scale) / 2;
  const offY  = (MINIMAP_H - canvasHeight * scale) / 2;

  const vpW = wrapper.clientWidth;
  const vpH = wrapper.clientHeight - 54;

  const vp = document.getElementById("pp-minimap-viewport");
  vp.style.left   = ((-panX / zoomScale) * scale + offX) + "px";
  vp.style.top    = ((-panY / zoomScale) * scale + offY) + "px";
  vp.style.width  = (vpW  / zoomScale)   * scale + "px";
  vp.style.height = (vpH  / zoomScale)   * scale + "px";
}

window.addEventListener("resize", () => updateMinimap());

// --------------------------------------------------------------------------------
// TRACE SEARCH UI
// --------------------------------------------------------------------------------

function buildRequestIdList(filter = "") {
  const listEl      = document.getElementById("pp-trace-list");
  const filterLower = filter.toLowerCase();
  listEl.innerHTML  = "";
  predictButton.disabled = true;

  requestIds
    .filter(id => id.toLowerCase().includes(filterLower))
    .forEach(id => {
      const item = document.createElement("div");
      item.className = "search-list-item" + (activeTrace === id ? " active" : "");
      item.innerHTML = `<div id="pp-search-item">${id}</div>`;
      item.onclick   = () => {
        activeTrace            = id;
        chosenId               = id;
        searchInput.value      = id;
        predictButton.disabled = false;
        listEl.classList.remove("open");
        applyTrace(id);
      };
      listEl.appendChild(item);
    });
}

searchInput.addEventListener("focus", () => {
  if (activeTrace) { searchInput.value = ""; predictButton.disabled = true; }
  buildRequestIdList(searchInput.value);
  document.getElementById("pp-trace-list").classList.add("open");
});

searchInput.addEventListener("input", e => {
  buildRequestIdList(e.target.value);
  document.getElementById("pp-trace-list").classList.add("open");
});

treeInput.addEventListener("focus", () => {
  if (activeTrace) { searchInput.value = ""; predictButton.disabled = true; }
  treeList.classList.add("open");
});

treeInput.addEventListener("input", e => {
  treeList.classList.add("open");
  const query = e.target.value.toLowerCase();
  treeList.querySelectorAll(".tree-item").forEach(item => {
    item.style.display = item.textContent.toLowerCase().includes(query) ? "" : "none";
  });
});

document.addEventListener("click", e => {
  if (!document.getElementById("pp-trace-dropdown").contains(e.target))
    document.getElementById("pp-trace-list").classList.remove("open");

  if (!document.getElementById("pp-tree-dropdown").contains(e.target))
    treeList.classList.remove("open");

  if (!e.target.closest("#provider-dropdown"))
    document.getElementById("pp-provider-list")?.classList.remove("open");

  if (!e.target.closest("#model-dropdown"))
    document.getElementById("pp-model-list")?.classList.remove("open");

  if (!e.target.closest(".pp-ensemble-entry-dropwrap"))
    document.querySelectorAll(".pp-ensemble-dropdown-list").forEach(el => el.classList.remove("open"));
});


// --------------------------------------------------------------------------------
// SETTINGS TABS
// --------------------------------------------------------------------------------

document.querySelectorAll(".settings-tab").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".settings-tab").forEach(b => {
      b.classList.remove("active");
      b.setAttribute("aria-selected", "false");
    });
    btn.classList.add("active");
    btn.setAttribute("aria-selected", "true");
    document.querySelectorAll(".settings-panel").forEach(p => { p.hidden = true; });
    document.getElementById("pp-settings-tab-" + btn.dataset.tab).hidden = false;
  });
});


// --------------------------------------------------------------------------------
// TAB CHANGE LISTENER
// --------------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
  const observer = new MutationObserver(() => {
    const tabButton = document.querySelector(
      '[data-bs-toggle="tab"][data-bs-target="#tab-ai_addons_pattern_prediction"]'
    );
    if (tabButton && !tabButton.dataset.listenerSet) {
      tabButton.addEventListener("click", () => { if (typeof resetZoom === "function") setTimeout(resetZoom, 100); });
      tabButton.dataset.listenerSet = "true";
      observer.disconnect();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });
});


// --------------------------------------------------------------------------------
// DATA
// --------------------------------------------------------------------------------

async function loadTreeData() {
  const [idsRes, tree, treefilesResponse] = await Promise.all([
    window.get("core-ai-addon", "req-ids"),
    window.get(ADDON_NAME,      "tree"),
    window.get(ADDON_NAME,      "tree-file"),
  ]);

  requestIds      = idsRes.ids;
  treeData        = tree.tree;
  selectedFile    = tree.file;
  treeInput.value = selectedFile ?? "";
  treefiles       = treefilesResponse;

  renderTree();
  renderTreeList(treefiles);
}

async function loadProviderData() {
  const [prov, selectedEnsemble] = await Promise.all([
    window.get("core-ai-addon", "ai-provider-data"),
    window.get(ADDON_NAME,      "ensemble"),
  ]);

  providerData      = prov.providers;
  ensembleEntries   = selectedEnsemble.ensemble;
  ensembleIdCounter = ensembleEntries.length;
  renderEnsembleList();
}