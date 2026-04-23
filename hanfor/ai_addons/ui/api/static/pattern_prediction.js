// -- CONSTANTS -----------------------------------------------------------------

const QUESTION_NODE_WIDTH  = 200;
const QUESTION_NODE_HEIGHT = 56;
const ANSWER_NODE_WIDTH    = 100;
const ANSWER_NODE_HEIGHT   = 34;
const PATTERN_NODE_WIDTH   = 210;
const PATTERN_NODE_HEIGHT  = 54;
const HORIZONTAL_GAP       = 60;
const VERTICAL_GAP         = 80;
const SVG_NS               = 'http://www.w3.org/2000/svg';

// -- STATE ---------------------------------------------------------------------

let treeData;
let requestIds;
let svgElement  = null;
let activeTrace = null;
let nodeRegistry = {};
let chosenId;
let ensembleEntries = [];
let ensembleIdCounter = 0;

const predictButton = document.getElementById('predict-pattern-btn');

// -- TEXT HELPERS --------------------------------------------------------------

function wrapTextIntoLines(lines, nodeWidth) {
  const maxPx = nodeWidth - 16;
  const result = [];
  lines.forEach(line => {
    const words = line.split(' ');
    let current = '';
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

// -- LAYOUT ENGINE -------------------------------------------------------------

function assignNodeLevels(node, level, parentId) {
  if (!node) return;
  node._level    = level;
  node._parentId = parentId;
  nodeRegistry[node.id] = node;

  if (!node.answers) return;
  node.answers.forEach(answer => {
    answer._answerId           = `ans_${node.id}_${answer.answer.replace(/\s/g, '_')}`;
    answer._parentQuestionId   = node.id;
    nodeRegistry[answer._answerId] = answer;
    assignNodeLevels(answer.next, level + 2, answer._answerId);
  });
}

function calculateNodePositions(node, offsetX, depth, startY = 0) {
  if (!node) return 0;

  if (node.pattern !== undefined) {
    node._x = offsetX;
    node._y = startY;
    node._height = calcDynamicHeight(node.pattern, PATTERN_NODE_WIDTH, PATTERN_NODE_HEIGHT, 14, 15, 10);
    return PATTERN_NODE_WIDTH;
  }

  if (node.answers) {
    node._height = calcDynamicHeight(node.question, QUESTION_NODE_WIDTH, QUESTION_NODE_HEIGHT, 10, 15, 10);
    node._x = offsetX;
    node._y = startY;

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

// -- RENDER TREE ---------------------------------------------------------------

function renderTree() {
  nodeRegistry = {};
  assignNodeLevels(treeData, 0, null);
  calculateNodePositions(treeData, 0, 0, 0);

  svgElement = document.getElementById('tree-svg');

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

  const PAD = 60;
  const totalWidth  = maxX - minX + PAD * 2;
  const totalHeight = maxY - minY + PAD * 2;

  svgElement.setAttribute('width',  totalWidth);
  svgElement.setAttribute('height', totalHeight);
  svgElement.innerHTML = '';

  const rootGroup = document.createElementNS(SVG_NS, 'g');
  rootGroup.setAttribute('transform', `translate(${PAD - minX},${PAD - minY})`);
  svgElement.appendChild(rootGroup);

  drawEdges(rootGroup, treeData);
  drawNodes(rootGroup, treeData);

  initPanZoom(totalWidth, totalHeight);
  updateMinimap(totalWidth, totalHeight);
}

// -- EDGES ---------------------------------------------------------------------

function drawEdges(parentGroup, node) {
  if (!node?.answers) return;
  node.answers.forEach(answer => {
    drawEdge(parentGroup, node,   answer,      'question-to-answer');
    if (answer.next) {
      drawEdge(parentGroup, answer, answer.next, 'answer-to-next');
      drawEdges(parentGroup, answer.next);
    }
  });
}

function drawEdge(parentGroup, fromNode, toNode, edgeType) {
  if (fromNode._x === undefined || toNode._x === undefined) return;

  let x1, y1, x2, y2;
  if (edgeType === 'question-to-answer') {
    const fromH = fromNode._height ?? QUESTION_NODE_HEIGHT;
    x1 = fromNode._x + QUESTION_NODE_WIDTH / 2;
    y1 = fromNode._y + fromH;
    x2 = toNode._x   + ANSWER_NODE_WIDTH / 2;
    y2 = toNode._y;
  } else {
    const toW = toNode.answers ? QUESTION_NODE_WIDTH : (toNode.pattern ? PATTERN_NODE_WIDTH : ANSWER_NODE_WIDTH);
    x1 = fromNode._x + ANSWER_NODE_WIDTH / 2;
    y1 = fromNode._y + ANSWER_NODE_HEIGHT;
    x2 = toNode._x   + toW / 2;
    y2 = toNode._y;
  }

  const cy = (y1 + y2) / 2;
  const path = document.createElementNS(SVG_NS, 'path');
  path.setAttribute('d', `M${x1},${y1} C${x1},${cy} ${x2},${cy} ${x2},${y2}`);
  path.setAttribute('class', 'edge');
  path.setAttribute('data-edge-id', `edge_${fromNode.id || fromNode._answerId}_${toNode.id || toNode._answerId}`);
  parentGroup.appendChild(path);
}

// -- NODES ---------------------------------------------------------------------

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

function svgRect(x, y, w, h, rx) {
  const r = document.createElementNS(SVG_NS, 'rect');
  r.setAttribute('x', x); r.setAttribute('y', y);
  r.setAttribute('width', w); r.setAttribute('height', h);
  r.setAttribute('rx', rx);
  return r;
}

function svgText(x, y, content, anchor = 'middle') {
  const t = document.createElementNS(SVG_NS, 'text');
  t.setAttribute('x', x); t.setAttribute('y', y);
  t.setAttribute('text-anchor', anchor);
  t.textContent = content;
  return t;
}

function drawQuestionNode(parentGroup, node) {
  const group = document.createElementNS(SVG_NS, 'g');
  group.setAttribute('class', 'node-q');
  group.setAttribute('data-node-id', node.id);

  const h       = node._height ?? QUESTION_NODE_HEIGHT;
  const LINE_H  = 15;
  const lines   = wrapTextIntoLines([node.question], QUESTION_NODE_WIDTH);
  const textH   = lines.length * LINE_H;
  const startY  = node._y + (h - textH) / 2 + LINE_H;

  group.appendChild(svgRect(node._x, node._y, QUESTION_NODE_WIDTH, h, 8));
  lines.forEach((line, i) =>
    group.appendChild(svgText(node._x + QUESTION_NODE_WIDTH / 2, startY + i * LINE_H, line))
  );
  parentGroup.appendChild(group);
}

function drawAnswerNode(parentGroup, answer) {
  const group = document.createElementNS(SVG_NS, 'g');
  group.setAttribute('class', 'node-a');
  group.setAttribute('data-node-id', answer._answerId);

  group.appendChild(svgRect(answer._x, answer._y, ANSWER_NODE_WIDTH, ANSWER_NODE_HEIGHT, 20));
  group.appendChild(svgText(
    answer._x + ANSWER_NODE_WIDTH / 2,
    answer._y + ANSWER_NODE_HEIGHT / 2 + 7,
    answer.answer
  ));
  parentGroup.appendChild(group);
}

function drawPatternNode(parentGroup, node) {
  const group = document.createElementNS(SVG_NS, 'g');
  group.setAttribute('class', 'node-p');
  group.setAttribute('data-node-id', node.id);

  const h      = node._height ?? PATTERN_NODE_HEIGHT;
  const LINE_H = 15;
  const lines  = wrapTextIntoLines([node.pattern], PATTERN_NODE_WIDTH);
  const textH  = lines.length * LINE_H;
  const startY = node._y + (h - textH) / 2 + LINE_H;

  group.appendChild(svgRect(node._x, node._y, PATTERN_NODE_WIDTH, h, 8));

  // Subtle "PATTERN" category label
  const label = document.createElementNS(SVG_NS, 'text');
  label.setAttribute('x', node._x + PATTERN_NODE_WIDTH / 2);
  label.setAttribute('y', node._y + 14);
  label.setAttribute('text-anchor', 'middle');
  label.setAttribute('fill', '#607899');
  label.setAttribute('font-size', '9');
  group.appendChild(label);

  lines.forEach((line, i) =>
    group.appendChild(svgText(node._x + PATTERN_NODE_WIDTH / 2, startY + i * LINE_H, line))
  );
  parentGroup.appendChild(group);
}

// -- TRACE HIGHLIGHTING --------------------------------------------------------

async function applyTrace(requestId) {
  if (requestId === null) {
    applyTraceHighlighting(null);
    removeTraceInfoBlock();
    await fetch('/ai_addons/pattern_prediction/clear_trace_sid', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ req_id: requestId, sid: window.appSocket.id }),
    });
    return;
  }

  await fetch('/ai_addons/pattern_prediction/set_trace_sid', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ req_id: requestId, sid: window.appSocket.id }),
  });
}

function applyTraceHighlighting(traceData) {
  if (!svgElement) return;

  // Clear previous state
  svgElement.querySelectorAll(
    '.trace-active, .trace-inactive, .trace-edge-active, .trace-edge-inactive'
  ).forEach(el => el.classList.remove('trace-active', 'trace-inactive', 'trace-edge-active', 'trace-edge-inactive'));
  svgElement.querySelectorAll('.prob-badge').forEach(el => el.remove());

  if (!traceData?.steps?.length) return;

  traceData.steps.forEach((step, stepIndex) => {
    const questionEl = svgElement.querySelector(`[data-node-id="${step.nodeId}"]`);
    if (questionEl) questionEl.classList.add('trace-active');

    Object.entries(step.confidences || {}).forEach(([answerText, confidence]) => {
      const answerNode = Object.values(nodeRegistry).find(
        n => n._parentQuestionId === step.nodeId && n.answer === answerText
      );
      if (!answerNode) return;

      const answerEdgeId       = answerNode.id || answerNode._answerId;
      const edgeQuestionAnswer = svgElement.querySelector(`[data-edge-id="edge_${step.nodeId}_${answerEdgeId}"]`);
      const answerEl           = svgElement.querySelector(`[data-node-id="${answerNode._answerId}"]`);

      // Probability badge
      if (answerEl) {
        const badge  = document.createElementNS(SVG_NS, 'g');
        badge.setAttribute('class', 'prob-badge');

        const textEl = document.createElementNS(SVG_NS, 'text');
        textEl.textContent = (confidence * 100).toFixed(0) + '%';
        textEl.setAttribute('text-anchor', 'middle');
        textEl.setAttribute('dominant-baseline', 'middle');

        const bgRect = document.createElementNS(SVG_NS, 'rect');
        bgRect.setAttribute('rx', 4);
        bgRect.setAttribute('ry', 4);
        badge.appendChild(bgRect);
        badge.appendChild(textEl);
        svgElement.querySelector('g').appendChild(badge);

        const bb = textEl.getBBox();
        bgRect.setAttribute('width',  bb.width  + 8);
        bgRect.setAttribute('height', bb.height + 4);
        bgRect.setAttribute('x', -(bb.width  + 8) / 2);
        bgRect.setAttribute('y', -(bb.height + 4) / 2);
        badge.setAttribute('transform', `translate(${answerNode._x + ANSWER_NODE_WIDTH / 2},${answerNode._y - bb.height + 4})`);
      }

      const chosen = step.answer === answerText;
      if (chosen) {
        if (edgeQuestionAnswer) edgeQuestionAnswer.classList.add('trace-edge-active');
        if (answerEl) answerEl.classList.add('trace-active');

        const nextNodeId = traceData.steps[stepIndex + 1]?.nodeId;
        if (nextNodeId) {
          const edgeAnswerNext = svgElement.querySelector(`[data-edge-id="edge_${answerEdgeId}_${nextNodeId}"]`);
          if (edgeAnswerNext) edgeAnswerNext.classList.add('trace-edge-active');
        }
      } else {
        if (edgeQuestionAnswer) edgeQuestionAnswer.classList.add('trace-edge-inactive');
        if (answerEl) answerEl.classList.add('trace-inactive');
      }
    });
  });
}

// -- TRACE INFO BLOCK ---------------------------------------------------------

function removeTraceInfoBlock() {
  document.getElementById('trace-info-block')?.remove();
}

function renderTraceInfoBlock(traceData) {
  let infoBlock = document.getElementById('trace-info-block');

  if (!infoBlock) {
    infoBlock = document.createElement('div');
    infoBlock.id        = 'trace-info-block';
    infoBlock.className = 'trace-info-block';

    const toggleBtn = document.createElement('button');
    toggleBtn.textContent = '−';
    toggleBtn.className   = 'trace-toggle-btn';
    toggleBtn.onclick = () => {
      const content = infoBlock.querySelector('.trace-content');
      const collapsed = content.style.display === 'none';
      content.style.display  = collapsed ? 'block' : 'none';
      toggleBtn.textContent  = collapsed ? '−' : '+';
      infoBlock.classList.toggle('minimized', !collapsed);
    };

    const contentEl = document.createElement('div');
    contentEl.className = 'trace-content';
    infoBlock.appendChild(toggleBtn);
    infoBlock.appendChild(contentEl);
    document.getElementById('canvas-wrap').appendChild(infoBlock);
  }

  const patternText = traceData.pattern && traceData.pattern !== 'none' ? traceData.pattern : 'none';
  infoBlock.querySelector('.trace-content').innerHTML =
    `<strong>Description:</strong> ${traceData.desc || '–'}<br><br><strong>Pattern:</strong> ${patternText}`;
}

function showErrorBanner(message) {
  window.showBanner(`<strong>Prediction error:</strong> ${message}`, 'danger', 'prediction-error-banner');
}

// -- PAN / ZOOM ----------------------------------------------------------------

let panX = 40, panY = 40, zoomScale = 1.0;
let isPanning = false, panStartX = 0, panStartY = 0;
let canvasWidth = 0, canvasHeight = 0;

function applyCanvasTransform() {
  document.getElementById('canvas').style.transform =
    `translate(${panX}px,${panY}px) scale(${zoomScale})`;
  updateMinimapViewport();
}

function initPanZoom(width, height) {
  canvasWidth  = width;
  canvasHeight = height;

  const wrapper  = document.getElementById('canvas-wrap');
  const vpW = wrapper.clientWidth;
  const vpH = wrapper.clientHeight;

  zoomScale = Math.min(1, (vpW - 80) / width, (vpH - 80) / height);
  panX = (vpW - width * zoomScale) / 2;
  panY = 30;
  applyCanvasTransform();

  // Mouse
  wrapper.addEventListener('mousedown', e => {
    if (e.button !== 0) return;
    isPanning = true;
    panStartX = e.clientX - panX;
    panStartY = e.clientY - panY;
    wrapper.classList.add('dragging');
  });
  wrapper.addEventListener('mousemove', e => {
    if (!isPanning) return;
    panX = e.clientX - panStartX;
    panY = e.clientY - panStartY;
    applyCanvasTransform();
  });
  wrapper.addEventListener('mouseup',    () => { isPanning = false; wrapper.classList.remove('dragging'); });
  wrapper.addEventListener('mouseleave', () => { isPanning = false; wrapper.classList.remove('dragging'); });

  // Wheel zoom
  wrapper.addEventListener('wheel', e => {
    if (e.target.closest('.trace-info-block')) return;
    e.preventDefault();
    const factor = e.deltaY > 0 ? 0.9 : 1.1;
    const bounds = wrapper.getBoundingClientRect();
    const mx = e.clientX - bounds.left;
    const my = e.clientY - bounds.top;
    panX = mx - (mx - panX) * factor;
    panY = my - (my - panY) * factor;
    zoomScale = Math.max(0.1, Math.min(3, zoomScale * factor));
    applyCanvasTransform();
  }, { passive: false });

  // Touch
  let lastPinchDist = null;
  wrapper.addEventListener('touchstart', e => {
    if (e.touches.length === 1) {
      isPanning = true;
      panStartX = e.touches[0].clientX - panX;
      panStartY = e.touches[0].clientY - panY;
    }
    if (e.touches.length === 2) lastPinchDist = null;
  });
  wrapper.addEventListener('touchmove', e => {
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
  wrapper.addEventListener('touchend', () => { isPanning = false; lastPinchDist = null; });

  // Toolbar buttons
  document.getElementById('zoom-in').onclick    = () => { zoomScale = Math.min(3,   zoomScale * 1.2); applyCanvasTransform(); };
  document.getElementById('zoom-out').onclick   = () => { zoomScale = Math.max(0.1, zoomScale / 1.2); applyCanvasTransform(); };
  document.getElementById('zoom-reset').onclick = resetZoom;
}

function resetZoom() {
  const wrapper = document.getElementById('canvas-wrap');
  if (!wrapper) return;
  const vpW = wrapper.clientWidth;
  const vpH = wrapper.clientHeight;
  zoomScale = Math.min(1, (vpW - 80) / canvasWidth, (vpH - 80) / canvasHeight);
  panX = (vpW - canvasWidth * zoomScale) / 2;
  panY = 30;
  applyCanvasTransform();
}

// -- MINIMAP -------------------------------------------------------------------

const MINIMAP_W = 160, MINIMAP_H = 100;

function updateMinimap(treeWidth, treeHeight) {
  const mmSvg  = document.getElementById('minimap-svg');
  const scale  = Math.min(MINIMAP_W / treeWidth, MINIMAP_H / treeHeight) * 0.9;
  const offX   = (MINIMAP_W - treeWidth  * scale) / 2;
  const offY   = (MINIMAP_H - treeHeight * scale) / 2;

  mmSvg.innerHTML = '';
  const group = document.createElementNS(SVG_NS, 'g');
  group.setAttribute('transform', `translate(${offX},${offY}) scale(${scale})`);

  Object.values(nodeRegistry).forEach(node => {
    if (node._x === undefined) return;
    const isQ = !!node.answers;
    const isP = node.pattern !== undefined;
    const w   = isP ? PATTERN_NODE_WIDTH : (isQ ? QUESTION_NODE_WIDTH : ANSWER_NODE_WIDTH);
    const h   = node._height ?? (isP ? PATTERN_NODE_HEIGHT : (isQ ? QUESTION_NODE_HEIGHT : ANSWER_NODE_HEIGHT));
    const r   = document.createElementNS(SVG_NS, 'rect');
    r.setAttribute('x',       node._x); r.setAttribute('y',      node._y);
    r.setAttribute('width',   w);       r.setAttribute('height',  h);
    r.setAttribute('rx',      4);       r.setAttribute('opacity', '0.8');
    r.setAttribute('fill',    isP ? '#2b6cb0' : (isQ ? '#3a3a38' : '#1a3a2a'));
    group.appendChild(r);
  });

  mmSvg.appendChild(group);
  updateMinimapViewport();
}

function updateMinimapViewport() {
  const wrapper = document.getElementById('canvas-wrap');
  const scale   = Math.min(MINIMAP_W / canvasWidth, MINIMAP_H / canvasHeight) * 0.9;
  const offX    = (MINIMAP_W - canvasWidth  * scale) / 2;
  const offY    = (MINIMAP_H - canvasHeight * scale) / 2;
  const vpW     = wrapper.clientWidth;
  const vpH     = wrapper.clientHeight - 54;

  const vp = document.getElementById('minimap-viewport');
  vp.style.left   = Math.max(0, (-panX / zoomScale) * scale + offX) + 'px';
  vp.style.top    = Math.max(0, (-panY / zoomScale) * scale + offY) + 'px';
  vp.style.width  = Math.min(MINIMAP_W, (vpW / zoomScale) * scale) + 'px';
  vp.style.height = Math.min(MINIMAP_H, (vpH / zoomScale) * scale) + 'px';
}

// -- TRACE SEARCH UI -----------------------------------------------------------

function buildRequestIdList(filter = '') {
  const listEl      = document.getElementById('trace-list');
  const filterLower = filter.toLowerCase();
  listEl.innerHTML  = '';
  predictButton.disabled = true;

  requestIds
    .filter(id => id.toLowerCase().includes(filterLower))
    .forEach(id => {
      const item = document.createElement('div');
      item.className = 'trace-item' + (activeTrace === id ? ' active' : '');
      item.innerHTML = `<div class="trace-id">${id}</div>`;
      item.onclick   = () => {
        activeTrace   = id;
        chosenId      = id;
        searchInput.value          = id;
        predictButton.disabled     = false;
        listEl.classList.remove('open');
        applyTrace(id);
      };
      listEl.appendChild(item);
    });
}

const searchInput = document.getElementById('trace-search');

searchInput.addEventListener('focus', () => {
  if (activeTrace) { searchInput.value = ''; predictButton.disabled = true; }
  buildRequestIdList(searchInput.value);
  document.getElementById('trace-list').classList.add('open');
});

searchInput.addEventListener('input', e => {
  buildRequestIdList(e.target.value);
  document.getElementById('trace-list').classList.add('open');
});

document.addEventListener('click', e => {
  if (!document.getElementById('trace-dropdown').contains(e.target))
    document.getElementById('trace-list').classList.remove('open');
});

document.getElementById('clear-trace-btn').onclick = () => {
  activeTrace = null;
  searchInput.value       = '';
  predictButton.disabled  = true;
  applyTrace(null);
};

predictButton.onclick = async () => {
  await fetch('/ai_addons/pattern_prediction/generate_trace', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ req_id: chosenId }),
  });
};

document.getElementById('predict-pattern-all-btn').addEventListener('click', async () => {
  await fetch('/ai_addons/pattern_prediction/generate_trace_all', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ req_id: chosenId }),
  });
});

// -- PROVIDER / MODEL SELECTOR -------------------------------------------------

let providerData     = [];
let selectedProvider = null;
let selectedModel    = null;

function ledEmoji(activity) {
  if (activity === 'ACTIVE')      return '🟢';
  if (activity === 'NOT_TESTED')  return '🟡';
  return '🔴';
}

async function loadProviderData() {
  const [provRes, selRes] = await Promise.all([
    fetch('/core_ai_addon/ai_provider_data'),
    fetch('/ai_addons/pattern_prediction/get_selected_ensemble'),
  ]);
  const provJson = await provRes.json();
  const selJson  = await selRes.json();

  providerData = provJson.providers;
  ensembleEntries = selJson.ensemble
  renderEnsembleList()
}

// -- SOCKET SUBSCRIPTIONS ----------------------------------------------------------

window.tabSubs.register('ai_addons_pattern_prediction', [
  {
    event:   'socket_provider_info',
    handler: ({ providers }) => {
      if (providers) {
        providerData = providers;
        renderEnsembleList();
      }
    },
  },
  {
    event:   'socket_pattern_prediction',
    handler: newData => {
      if (newData) { applyTraceHighlighting(newData); renderTraceInfoBlock(newData); }
    },
  },
  {
    event:   'socket_pattern_prediction_error',
    handler: ({ error } = {}) => { if (error) showErrorBanner(error); },
  },
  {
    event:   'socket_pattern_prediction_ensemble',
    handler: newData => {
    ensembleEntries = newData.ensemble
    renderEnsembleList()
    },
  },
  {
    event:   'socket_pattern_prediction_new_tree',
    handler:  newTree => {
        console.log(newTree)
        treeData     = newTree.tree;
        selectedFile = newTree.file;
        treeInput.value = selectedFile ?? '';
        renderTree();
        renderTreeList(treefiles);
    },
  },
]);

window.tabSubs.onActivate('ai_addons_pattern_prediction', () => {
  loadTreeData();
  loadProviderData();
  setTimeout(resetZoom, 100);
});

window.tabSubs.onDeactivate('ai_addons_pattern_prediction', async () => {
  document.getElementById('clear-trace-btn').click();
  await fetch('/ai_addons/pattern_prediction/clear_trace_sid', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ req_id: chosenId, sid: window.appSocket.id }),
    });
});

// -- SVG DOWNLOAD --------------------------------------------------------------

document.getElementById('download-svg-btn').addEventListener('click', () => {
  const svg   = document.getElementById('tree-svg');
  const clone = svg.cloneNode(true);

  const styleEl = document.createElementNS(SVG_NS, 'style');
  styleEl.textContent = Array.from(document.styleSheets)
    .flatMap(sheet => { try { return Array.from(sheet.cssRules).map(r => r.cssText); } catch { return []; } })
    .join('\n');
  clone.insertBefore(styleEl, clone.firstChild);

  const svgStr = '<?xml version="1.0" encoding="UTF-8"?>\n' + new XMLSerializer().serializeToString(clone);
  const url    = URL.createObjectURL(new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' }));
  const a      = Object.assign(document.createElement('a'), { href: url, download: 'tree.svg' });
  a.click();
  URL.revokeObjectURL(url);
});

// -- TAB CHANGE LISTENER -------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
  const observer = new MutationObserver(() => {
    const tabButton = document.querySelector(
      '[data-bs-toggle="tab"][data-bs-target="#tab-ai_addons_pattern_prediction"]'
    );
    if (tabButton && !tabButton.dataset.listenerSet) {
      tabButton.addEventListener('click', () => { if (typeof resetZoom === 'function') setTimeout(resetZoom, 100); });
      tabButton.dataset.listenerSet = 'true';
      observer.disconnect();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });
});

// -- SETTINGS MODAL -----------------------------------------------------------

document.getElementById('open-settings-btn').addEventListener('click', () => {
  document.getElementById('settings-overlay').hidden = false;
});

function closeSettings() {
  document.getElementById('settings-overlay').hidden = true;
  document.querySelectorAll('#provider-list, #model-list, .ensemble-dropdown-list')
    .forEach(el => el.classList.remove('open'));
}

document.getElementById('close-settings-btn').addEventListener('click', closeSettings);
document.getElementById('settings-overlay').addEventListener('click', e => {
  if (e.target === e.currentTarget) closeSettings();
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeSettings();
});

// Tab switching
document.querySelectorAll('.stab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.stab').forEach(b => {
      b.classList.remove('active');
      b.setAttribute('aria-selected', 'false');
    });
    btn.classList.add('active');
    btn.setAttribute('aria-selected', 'true');
    document.querySelectorAll('.settings-panel').forEach(p => { p.hidden = true; });
    document.getElementById('stab-' + btn.dataset.tab).hidden = false;
  });
});

// Close dropdowns when clicking outside modal panels
document.addEventListener('click', e => {
  if (!e.target.closest('#provider-dropdown'))
    document.getElementById('provider-list')?.classList.remove('open');
  if (!e.target.closest('#model-dropdown'))
    document.getElementById('model-list')?.classList.remove('open');
  if (!e.target.closest('.ensemble-entry-dropwrap'))
    document.querySelectorAll('.ensemble-dropdown-list').forEach(el => el.classList.remove('open'));
});

// -- ENSEMBLE LIST ------------------------------------------------------------
function ensembleProviderReachable(providerName) {
  const p = providerData.find(p => p.name === providerName);
  return p ? p.reachable : null;
}

function ensembleModelReachable(providerName, modelName) {
  const p = providerData.find(p => p.name === providerName);
  if (!p) return null;
  const m = p.models.find(m => (typeof m === 'string' ? m : m.name) === modelName);
  if (!m || typeof m === 'string') return null;
  return m.active ?? null;
}

function renderEnsembleList() {
  const container = document.getElementById('ensemble-list');
  container.innerHTML = '';

  ensembleEntries.forEach(entry => {
    const provReachable  = entry.provider ? ensembleProviderReachable(entry.provider) : null;
    const modReachable   = (entry.provider && entry.model) ? ensembleModelReachable(entry.provider, entry.model) : null;
    const provDisplay    = entry.provider ? `${ledEmoji(provReachable)} ${entry.provider}` : '';
    const modDisplay     = entry.model    ? `${ledEmoji(modReachable)} ${entry.model}`     : '';

    const el = document.createElement('div');
    el.className = 'ensemble-entry';
    el.dataset.id = entry.id;
    el.innerHTML = `
      <div class="ensemble-entry-fields">
        <div class="ensemble-entry-dropwrap half" data-entry-id="${entry.id}" data-role="provider">
          <input class="ensemble-input ensemble-provider-input"
                 type="text" placeholder="Provider…" autocomplete="off" readonly
                 value="${provDisplay}">
          <div class="ensemble-dropdown-list"></div>
        </div>
        <div class="ensemble-entry-dropwrap half" data-entry-id="${entry.id}" data-role="model">
          <input class="ensemble-input ensemble-model-input"
                 type="text" placeholder="Model…" autocomplete="off" readonly
                 value="${modDisplay}" ${entry.provider ? '' : 'disabled'}>
          <div class="ensemble-dropdown-list"></div>
        </div>
      </div>
      <div class="ensemble-entry-nums">
        <div class="ensemble-num-wrap">
          <input class="ensemble-num-input ensemble-count-input"
                 type="number" min="1" step="1" value="${entry.count}" title="Times to ask">
          <div class="ensemble-num-label">Count</div>
        </div>
        <div class="ensemble-num-wrap">
          <input class="ensemble-num-input ensemble-weight-input"
                 type="number" min="0" step="0.1" value="${entry.weight}" title="Weight">
          <div class="ensemble-num-label">Weight</div>
        </div>
      </div>
      <button class="ensemble-remove-btn" title="Remove">✕</button>
    `;

    // Provider dropdown
    const provWrap  = el.querySelector('[data-role="provider"]');
    const provInput = provWrap.querySelector('.ensemble-provider-input');
    const provList  = provWrap.querySelector('.ensemble-dropdown-list');

    provInput.addEventListener('click', () => {
      document.querySelectorAll('.ensemble-dropdown-list').forEach(d => d.classList.remove('open'));
      buildEnsembleProviderList(provList, entry);
      provList.classList.add('open');
    });

    // Model dropdown
    const modWrap  = el.querySelector('[data-role="model"]');
    const modInput = modWrap.querySelector('.ensemble-model-input');
    const modList  = modWrap.querySelector('.ensemble-dropdown-list');

    modInput.addEventListener('click', () => {
      if (!entry.provider) return;
      document.querySelectorAll('.ensemble-dropdown-list').forEach(d => d.classList.remove('open'));
      buildEnsembleModelList(modList, entry);
      modList.classList.add('open');
    });

    // Count
    el.querySelector('.ensemble-count-input').addEventListener('change', e => {
      entry.count = Math.max(1, parseInt(e.target.value) || 1);
      e.target.value = entry.count;
    });

    // Weight
    el.querySelector('.ensemble-weight-input').addEventListener('change', e => {
      const v = parseFloat(e.target.value);
      entry.weight = isNaN(v) ? 1 : Math.max(0, v);
      e.target.value = entry.weight;
    });

    // Remove
    el.querySelector('.ensemble-remove-btn').addEventListener('click', () => {
      ensembleEntries = ensembleEntries.filter(en => en.id !== entry.id);
      renderEnsembleList();
    });

    container.appendChild(el);
  });
}

function buildEnsembleProviderList(listEl, entry) {
  listEl.innerHTML = '';
  providerData.forEach(p => {
    const item = document.createElement('div');
    item.className = 'trace-item' + (entry.provider === p.name ? ' active' : '');
    item.innerHTML = `<div class="trace-id">${led(p.reachable)} ${p.name}</div>`;
    item.addEventListener('click', e => {
      e.stopPropagation();
      entry.provider = p.name;
      entry.model    = null;
      listEl.classList.remove('open');
      renderEnsembleList();
    });
    listEl.appendChild(item);
  });
}

function buildEnsembleModelList(listEl, entry) {
  listEl.innerHTML = '';
  const prov = providerData.find(p => p.name === entry.provider);
  if (!prov) return;
  prov.models.forEach(m => {
    const name      = typeof m === 'string' ? m : m.name;
    const reachable = typeof m === 'string' ? null : (m.active ?? null);
    const item      = document.createElement('div');
    item.className  = 'trace-item' + (entry.model === name ? ' active' : '');
    item.innerHTML  = `<div class="trace-id">${reachable !== null ? led(reachable) : ''} ${name}</div>`;
    item.addEventListener('click', e => {
      e.stopPropagation();
      entry.model = name;
      listEl.classList.remove('open');
      renderEnsembleList();
    });
    listEl.appendChild(item);
  });
}

document.getElementById('add-ensemble-entry-btn').addEventListener('click', () => {
  ensembleEntries.push({ id: ++ensembleIdCounter, provider: null, model: null, count: 1, weight: 1 });
  renderEnsembleList();
});

document.getElementById('save-ensemble-entry-btn').addEventListener('click', async () =>{

  await fetch('/ai_addons/pattern_prediction/set_selected_ensemble', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ "ensemble": ensembleEntries }),
  });
});

document.getElementById('download-detailed-traces-btn').addEventListener('click', async () => {
    const response = await fetch('/ai_addons/pattern_prediction/get_all_detailed_traces_as_file', {
        method: 'GET',
    });

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'detailed_traces.json';
    a.click();
    URL.revokeObjectURL(url);
});

// -------- TREE ------------------------------------------------------------------------------

let treefiles;
let selectedFile;
const treeInput = document.getElementById('tree-search');
const treeList  = document.getElementById('tree-list');

function renderTreeList(files) {
  treeList.innerHTML = '';
  files.forEach(filename => {
    const item = document.createElement('div');
    item.className = 'tree-item';
    item.textContent = filename;
    item.addEventListener('click', () => {
    treeList.classList.remove('open');
    fetch('/ai_addons/pattern_prediction/select_tree_file', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file: filename })
    });
  });
    treeList.appendChild(item);
  });
}

function filterList(query) {
  const items = treeList.querySelectorAll('.tree-item');
  items.forEach(item => {
    item.style.display = item.textContent.toLowerCase().includes(query.toLowerCase())
      ? '' : 'none';
  });
}

treeInput.addEventListener('focus', () => {
  if (activeTrace) { searchInput.value = ''; predictButton.disabled = true; }
  treeList.classList.add('open');
});

treeInput.addEventListener('input', e => {
  treeList.classList.add('open');
  filterList(e.target.value);
});

document.addEventListener('click', e => {
  if (!document.getElementById('tree-dropdown').contains(e.target))
    treeList.classList.remove('open');
});


// -- INIT ----------------------------------------------------------------------

async function loadTreeData() {
  const [idsRes, treeRes, treefilesRes] = await Promise.all([
    fetch('/core_ai_addon/req_ids'),
    fetch('/ai_addons/pattern_prediction/tree'),
    fetch('/ai_addons/pattern_prediction/get_all_tree_file')
  ]);

  const treeJson = await treeRes.json();

  requestIds   = await idsRes.json();
  treeData     = treeJson.tree;
  selectedFile = treeJson.file;
  treeInput.value = selectedFile ?? '';
  treefiles    = await treefilesRes.json();

  renderTree();
  renderTreeList(treefiles);
}