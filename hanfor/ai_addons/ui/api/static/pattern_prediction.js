// --- CONSTANTS ----------------------------------------------------------------

const QUESTION_NODE_WIDTH  = 200;
const QUESTION_NODE_HEIGHT = 56;
const ANSWER_NODE_WIDTH    = 100;
const ANSWER_NODE_HEIGHT   = 34;
const PATTERN_NODE_WIDTH   = 210;
const PATTERN_NODE_HEIGHT  = 54;
const HORIZONTAL_GAP       = 60;
const VERTICAL_GAP         = 80;

const SVG_NS = "http://www.w3.org/2000/svg";

// --- STATE --------------------------------------------------------------------

let treeData;       // raw tree JSON from the API
let requestIds;     // list of request IDs for the trace search

let svgElement   = null;  // main SVG DOM element
let activeTrace  = null;  // currently selected request ID

let nodeRegistry = {};  // flat map of all nodes by their ID, built during layout

const predictButton = document.getElementById('predict-pattern-btn');

// --- LAYOUT ENGINE ------------------------------------------------------------

/**
 * Recursively walks the tree and assigns a level depth and parent reference
 * to each node. Also registers every node in the flat nodeRegistry map.
 */
function assignNodeLevels(node, level, parentId) {
  if (!node) return;

  node._level    = level;
  node._parentId = parentId;
  nodeRegistry[node.id] = node;

  if (!node.answers) return;

  node.answers.forEach(answer => {
    answer._answerId      = `ans_${node.id}_${answer.answer.replace(/\s/g, '_')}`;
    answer._parentQuestionId = node.id;
    nodeRegistry[answer._answerId] = answer;
    assignNodeLevels(answer.next, level + 2, answer._answerId);
  });
}

/**
 * Recursively calculates x/y positions for every node and returns
 * the total width consumed by this subtree.
 */
function calculateNodePositions(node, offsetX, depth) {
  if (!node) return 0;

  const rowY = depth * (QUESTION_NODE_HEIGHT + VERTICAL_GAP);

  // Pattern (leaf) node - fixed size, no children
  if (node.pattern !== undefined) {
    node._x = offsetX;
    node._y = rowY;
    return PATTERN_NODE_WIDTH;
  }

  // Question node - recursively lay out children first, then center parent
  if (node.answers) {
    let totalWidth  = 0;
    const childCenterXs = [];

    node.answers.forEach(answer => {
      const childWidth = calculateNodePositions(answer.next, offsetX + totalWidth, depth + 2);
      childCenterXs.push(offsetX + totalWidth + childWidth / 2);
      totalWidth += childWidth + HORIZONTAL_GAP;
    });

    totalWidth -= HORIZONTAL_GAP; // remove trailing gap

    // Center parent question node over its children
    node._x = (childCenterXs[0] + childCenterXs[childCenterXs.length - 1]) / 2 - QUESTION_NODE_WIDTH / 2;
    node._y = rowY;

    // Position each answer bubble between parent and next question
    node.answers.forEach((answer, index) => {
      answer._x = childCenterXs[index] - ANSWER_NODE_WIDTH / 2;
      answer._y = (depth + 1) * (QUESTION_NODE_HEIGHT + VERTICAL_GAP);
    });

    return totalWidth;
  }
}

// --- RENDERING ----------------------------------------------------------------

/**
 * Rebuilds the entire SVG from scratch using the current treeData.
 */
function renderTree() {
  nodeRegistry = {};
  assignNodeLevels(treeData, 0, null);
  calculateNodePositions(treeData, 0, 0);

  svgElement = document.getElementById('tree-svg');

  // Calculate bounding box across all registered nodes
  let minX = Infinity, maxX = -Infinity;
  let minY = Infinity, maxY = -Infinity;

  Object.values(nodeRegistry).forEach(node => {
    if (node._x === undefined) return;
    const w = node.pattern  ? PATTERN_NODE_WIDTH  : (node.answers ? QUESTION_NODE_WIDTH  : ANSWER_NODE_WIDTH);
    const h = node.pattern  ? PATTERN_NODE_HEIGHT : (node.answers ? QUESTION_NODE_HEIGHT : ANSWER_NODE_HEIGHT);
    minX = Math.min(minX, node._x);
    maxX = Math.max(maxX, node._x + w);
    minY = Math.min(minY, node._y);
    maxY = Math.max(maxY, node._y + h);
  });

  const PADDING = 60;
  const totalWidth  = maxX - minX + PADDING * 2;
  const totalHeight = maxY - minY + PADDING * 2;

  svgElement.setAttribute('width',  totalWidth);
  svgElement.setAttribute('height', totalHeight);
  svgElement.innerHTML = '';

  const rootGroup = document.createElementNS(SVG_NS, 'g');
  rootGroup.setAttribute('transform', `translate(${PADDING - minX},${PADDING - minY})`);
  svgElement.appendChild(rootGroup);

  drawEdges(rootGroup, treeData);
  drawNodes(rootGroup, treeData);

  initPanZoom(totalWidth, totalHeight);
  updateMinimap(totalWidth, totalHeight);
}

// --- EDGES --------------------------------------------------------------------

function drawEdges(parentGroup, node) {
  if (!node || !node.answers) return;

  node.answers.forEach(answer => {
    drawEdge(parentGroup, node, answer, 'question-to-answer');
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
    x1 = fromNode._x + QUESTION_NODE_WIDTH / 2;
    y1 = fromNode._y + QUESTION_NODE_HEIGHT;
    x2 = toNode._x  + ANSWER_NODE_WIDTH / 2;
    y2 = toNode._y;
  } else {
    const toWidth = toNode.answers ? QUESTION_NODE_WIDTH : (toNode.pattern ? PATTERN_NODE_WIDTH : ANSWER_NODE_WIDTH);
    x1 = fromNode._x + ANSWER_NODE_WIDTH / 2;
    y1 = fromNode._y + ANSWER_NODE_HEIGHT;
    x2 = toNode._x  + toWidth / 2;
    y2 = toNode._y;
  }

  const controlY = (y1 + y2) / 2;

  const path = document.createElementNS(SVG_NS, 'path');
  path.setAttribute('d', `M${x1},${y1} C${x1},${controlY} ${x2},${controlY} ${x2},${y2}`);
  path.setAttribute('class', 'edge');

  const fromId = fromNode.id || fromNode._answerId;
  const toId   = toNode.id   || toNode._answerId;
  path.setAttribute('data-edge-id', `edge_${fromId}_${toId}`);

  parentGroup.appendChild(path);
}

// --- NODES --------------------------------------------------------------------

function drawNodes(parentGroup, node) {
  if (!node) return;

  if (node.pattern !== undefined) {
    drawPatternNode(parentGroup, node);
    return;
  }

  if (node.answers) {
    drawQuestionNode(parentGroup, node);
    node.answers.forEach(answer => {
      drawAnswerNode(parentGroup, answer);
      drawNodes(parentGroup, answer.next);
    });
  }
}

/**
 * Splits a long label into wrapped lines that fit within the given width.
 */
function wrapTextIntoLines(lines, nodeWidth) {
  const maxCharWidth = nodeWidth - 16;
  const result = [];

  lines.forEach(line => {
    const words = line.split(' ');
    let currentLine = '';

    words.forEach(word => {
      const candidate = currentLine ? `${currentLine} ${word}` : word;
      if (candidate.length * 7 > maxCharWidth && currentLine) {
        result.push(currentLine);
        currentLine = word;
      } else {
        currentLine = candidate;
      }
    });

    if (currentLine) result.push(currentLine);
  });

  return result;
}

function drawQuestionNode(parentGroup, node) {
  const group = document.createElementNS(SVG_NS, 'g');
  group.setAttribute('class', 'node-q');
  group.setAttribute('data-node-id', node.id);

  const rect = document.createElementNS(SVG_NS, 'rect');
  rect.setAttribute('x',      node._x);
  rect.setAttribute('y',      node._y);
  rect.setAttribute('width',  QUESTION_NODE_WIDTH);
  rect.setAttribute('height', QUESTION_NODE_HEIGHT);
  rect.setAttribute('rx', 8);
  group.appendChild(rect);

  const LINE_HEIGHT = 15;
  const wrappedLines = wrapTextIntoLines([node.question], QUESTION_NODE_WIDTH);
  const startY = node._y + QUESTION_NODE_HEIGHT / 2 - (wrappedLines.length * LINE_HEIGHT) / 2 + 10;

  wrappedLines.forEach((line, index) => {
    const textEl = document.createElementNS(SVG_NS, 'text');
    textEl.setAttribute('x', node._x + QUESTION_NODE_WIDTH / 2);
    textEl.setAttribute('y', startY + index * LINE_HEIGHT);
    textEl.setAttribute('text-anchor', 'middle');
    textEl.textContent = line;
    group.appendChild(textEl);
  });

  parentGroup.appendChild(group);
}

function drawAnswerNode(parentGroup, answer) {
  const group = document.createElementNS(SVG_NS, 'g');
  group.setAttribute('class', 'node-a');
  group.setAttribute('data-node-id', answer._answerId);

  const rect = document.createElementNS(SVG_NS, 'rect');
  rect.setAttribute('x',      answer._x);
  rect.setAttribute('y',      answer._y);
  rect.setAttribute('width',  ANSWER_NODE_WIDTH);
  rect.setAttribute('height', ANSWER_NODE_HEIGHT);
  rect.setAttribute('rx', 20);
  group.appendChild(rect);

  const textEl = document.createElementNS(SVG_NS, 'text');
  textEl.setAttribute('x', answer._x + ANSWER_NODE_WIDTH / 2);
  textEl.setAttribute('y', answer._y + ANSWER_NODE_HEIGHT / 2+7);
  textEl.setAttribute('text-anchor', 'middle');
  textEl.textContent = answer.answer;
  group.appendChild(textEl);

  parentGroup.appendChild(group);
}

function drawPatternNode(parentGroup, node) {
  const group = document.createElementNS(SVG_NS, 'g');
  group.setAttribute('class', 'node-p');
  group.setAttribute('data-node-id', node.id);

  const rect = document.createElementNS(SVG_NS, 'rect');
  rect.setAttribute('x',      node._x);
  rect.setAttribute('y',      node._y);
  rect.setAttribute('width',  PATTERN_NODE_WIDTH);
  rect.setAttribute('height', PATTERN_NODE_HEIGHT);
  rect.setAttribute('rx', 8);
  group.appendChild(rect);

  // Small "PATTERN" category label above the content
  const categoryLabel = document.createElementNS(SVG_NS, 'text');
  categoryLabel.setAttribute('x', node._x + PATTERN_NODE_WIDTH / 2);
  categoryLabel.setAttribute('y', node._y + 18);
  categoryLabel.setAttribute('text-anchor', 'middle');
  categoryLabel.setAttribute('fill', '#607899');
  categoryLabel.setAttribute('font-size', '9');
  group.appendChild(categoryLabel);

  const LINE_HEIGHT = 15;
  const wrappedLines = wrapTextIntoLines([node.pattern], PATTERN_NODE_WIDTH);
  const startY = node._y + 32;

  wrappedLines.forEach((line, index) => {
    const textEl = document.createElementNS(SVG_NS, 'text');
    textEl.setAttribute('x', node._x + PATTERN_NODE_WIDTH / 2);
    textEl.setAttribute('y', startY + index * LINE_HEIGHT);
    textEl.setAttribute('text-anchor', 'middle');
    textEl.textContent = line;
    group.appendChild(textEl);
  });

  parentGroup.appendChild(group);
}

// --- TRACE HIGHLIGHTING -------------------------------------------------------

/**
 * Fetches the trace for a given request ID and applies visual highlighting.
 * Passing null clears the current trace.
 */
async function applyTrace(requestId) {
  console.log(requestId);

  if (requestId === null) {
    applyTraceHighlighting(null);
    removeTraceInfoBlock();
    return;
  }

  const response = await fetch('/ai_addons/ui/api/pattern_prediction/trace', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ req_id: requestId }),
  });

  const traceData = await response.json();
  console.log(traceData);

  predictButton.disabled = traceData.pattern === "calculating";
  applyTraceHighlighting(traceData);
  renderTraceInfoBlock(traceData);
}

function removeTraceInfoBlock() {
  const existingBlock = document.getElementById('trace-info-block');
  if (existingBlock) existingBlock.remove();
}

/**
 * Creates or updates the floating info panel showing description and pattern
 * for the currently selected trace.
 */
function renderTraceInfoBlock(traceData) {
  let infoBlock = document.getElementById('trace-info-block');

  if (!infoBlock) {
    infoBlock = document.createElement('div');
    infoBlock.id        = 'trace-info-block';
    infoBlock.className = 'trace-info-block';

    const toggleButton = document.createElement('button');
    toggleButton.textContent = '−';
    toggleButton.className   = 'trace-toggle-btn';
    toggleButton.onclick = () => {
      const contentEl = infoBlock.querySelector('.trace-content');
      const isCollapsed = contentEl.style.display === 'none';
      contentEl.style.display   = isCollapsed ? 'block' : 'none';
      toggleButton.textContent  = isCollapsed ? '−' : '+';
      infoBlock.classList.toggle('minimized', !isCollapsed);
    };

    infoBlock.appendChild(toggleButton);

    const contentEl = document.createElement('div');
    contentEl.className = 'trace-content';
    infoBlock.appendChild(contentEl);

    document.getElementById('canvas-wrap').appendChild(infoBlock);
  }

  const contentEl = infoBlock.querySelector('.trace-content');
  const patternText = traceData.pattern && traceData.pattern !== "none"
    ? traceData.pattern
    : 'none';

  contentEl.innerHTML = `
    <strong>Description:</strong> ${traceData.desc || '-'}<br><br>
    <strong>Pattern:</strong> ${patternText}
  `;
}

/**
 * Applies or clears CSS highlight classes on SVG nodes and edges
 * based on the trace steps and their confidence scores.
 */
function applyTraceHighlighting(traceData) {
  if (!svgElement) return;

  // Clear all previous trace styling
  svgElement.querySelectorAll(
    '.trace-active, .trace-inactive, .trace-edge-active, .trace-edge-inactive'
  ).forEach(el => el.classList.remove(
    'trace-active', 'trace-inactive', 'trace-edge-active', 'trace-edge-inactive'
  ));

  // Remove old probability badges
  svgElement.querySelectorAll('.prob-badge').forEach(el => el.remove());

  if (!traceData || traceData.steps.length === 0) return;

  traceData.steps.forEach((step, stepIndex) => {
    const questionNodeId = step.nodeId;
    const questionEl = svgElement.querySelector(`[data-node-id="${questionNodeId}"]`);
    if (questionEl) questionEl.classList.add('trace-active');

    Object.entries(step.confidences || {}).forEach(([answerText, confidence]) => {
      const answerNode = Object.values(nodeRegistry).find(
        n => n._parentQuestionId === questionNodeId && n.answer === answerText
      );
      if (!answerNode) return;

      const answerEdgeFromId = answerNode.id || answerNode._answerId;
      const edgeQuestionToAnswer = svgElement.querySelector(
        `[data-edge-id="edge_${questionNodeId}_${answerEdgeFromId}"]`
      );
      const answerEl = svgElement.querySelector(`[data-node-id="${answerNode._answerId}"]`);

      // Draw a small confidence percentage badge above the answer bubble
      if (answerEl) {
        const badge = document.createElementNS(SVG_NS, 'g');
        badge.setAttribute('class', 'prob-badge');

        const textEl = document.createElementNS(SVG_NS, 'text');
        textEl.textContent = (confidence * 100).toFixed(0) + '%';
        textEl.setAttribute('text-anchor', 'middle');
        textEl.setAttribute('dominant-baseline', 'middle');
        badge.appendChild(textEl);

        const bgRect = document.createElementNS(SVG_NS, 'rect');
        bgRect.setAttribute('rx', 4);
        bgRect.setAttribute('ry', 4);
        badge.insertBefore(bgRect, textEl);

        svgElement.querySelector('g').appendChild(badge);

        const textBBox = textEl.getBBox();
        bgRect.setAttribute('width',  textBBox.width  + 8);
        bgRect.setAttribute('height', textBBox.height + 4);
        bgRect.setAttribute('x', -(textBBox.width  + 8) / 2);
        bgRect.setAttribute('y', -(textBBox.height + 4) / 2);

        const badgeX = answerNode._x + ANSWER_NODE_WIDTH / 2;
        const badgeY = answerNode._y - textBBox.height + 4;
        badge.setAttribute('transform', `translate(${badgeX}, ${badgeY})`);
      }

      // Highlight each edge and answer node based on whether it was taken
      const wasAnswerChosen = step.answer === answerText;

      if (wasAnswerChosen) {
        if (edgeQuestionToAnswer) edgeQuestionToAnswer.classList.add('trace-edge-active');
        if (answerEl) answerEl.classList.add('trace-active');

        const nextNodeId = traceData.steps[stepIndex + 1]?.nodeId;
        if (nextNodeId) {

          const answerEdgeFromId = answerNode.id || answerNode._answerId;
          const edgeAnswerToNext = svgElement.querySelector(
            `[data-edge-id="edge_${answerEdgeFromId}_${nextNodeId}"]`
          );
          if (edgeAnswerToNext) edgeAnswerToNext.classList.add('trace-edge-active');
        }
      } else {
        if (edgeQuestionToAnswer) edgeQuestionToAnswer.classList.add('trace-edge-inactive');
        if (answerEl) answerEl.classList.add('trace-inactive');
      }



    });
  });
}

// --- PAN / ZOOM ---------------------------------------------------------------

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

  const wrapper = document.getElementById('canvas-wrap');
  const viewportW = wrapper.clientWidth;
  const viewportH = wrapper.clientHeight;

  // Fit the tree into view on initial load
  zoomScale = Math.min(1, (viewportW - 80) / width, (viewportH - 80) / height);
  panX = (viewportW - width * zoomScale) / 2;
  panY = 30;
  applyCanvasTransform();

  // Mouse pan
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
  wrapper.addEventListener('mouseup',   () => { isPanning = false; wrapper.classList.remove('dragging'); });
  wrapper.addEventListener('mouseleave', () => { isPanning = false; wrapper.classList.remove('dragging'); });

  // Scroll to zoom (ignore scroll inside the info block)
  wrapper.addEventListener('wheel', e => {
    if (e.target.closest('.trace-info-block')) return;
    e.preventDefault();

    const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
    const bounds = wrapper.getBoundingClientRect();
    const mouseX = e.clientX - bounds.left;
    const mouseY = e.clientY - bounds.top;

    panX = mouseX - (mouseX - panX) * zoomFactor;
    panY = mouseY - (mouseY - panY) * zoomFactor;
    zoomScale = Math.max(0.1, Math.min(3, zoomScale * zoomFactor));

    applyCanvasTransform();
  }, { passive: false });

  // Touch pan & pinch-to-zoom
  let lastPinchDistance = null;

  wrapper.addEventListener('touchstart', e => {
    if (e.touches.length === 1) {
      isPanning    = true;
      panStartX    = e.touches[0].clientX - panX;
      panStartY    = e.touches[0].clientY - panY;
    }
    if (e.touches.length === 2) lastPinchDistance = null;
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
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (lastPinchDistance) {
        zoomScale = Math.max(0.1, Math.min(3, zoomScale * (dist / lastPinchDistance)));
        applyCanvasTransform();
      }
      lastPinchDistance = dist;
    }
  }, { passive: false });

  wrapper.addEventListener('touchend', () => {
    isPanning         = false;
    lastPinchDistance = null;
  });

  // Toolbar buttons
  document.getElementById('zoom-in').onclick    = () => { zoomScale = Math.min(3, zoomScale * 1.2); applyCanvasTransform(); };
  document.getElementById('zoom-out').onclick   = () => { zoomScale = Math.max(0.1, zoomScale / 1.2); applyCanvasTransform(); };
  document.getElementById('zoom-reset').onclick = resetZoom;
}

function resetZoom() {
  const wrapper = document.getElementById('canvas-wrap');
  if (!wrapper) return;
  const viewportW = wrapper.clientWidth;
  const viewportH = wrapper.clientHeight;
  zoomScale = Math.min(1, (viewportW - 80) / canvasWidth, (viewportH - 80) / canvasHeight);
  panX = (viewportW - canvasWidth * zoomScale) / 2;
  panY = 30;
  applyCanvasTransform();
}

// --- MINIMAP ------------------------------------------------------------------

const MINIMAP_WIDTH  = 160;
const MINIMAP_HEIGHT = 100;

function updateMinimap(treeWidth, treeHeight) {
  const minimapSvg = document.getElementById('minimap-svg');
  const scale = Math.min(MINIMAP_WIDTH / treeWidth, MINIMAP_HEIGHT / treeHeight) * 0.9;
  minimapSvg.innerHTML = '';

  const offsetX = (MINIMAP_WIDTH  - treeWidth  * scale) / 2;
  const offsetY = (MINIMAP_HEIGHT - treeHeight * scale) / 2;

  const group = document.createElementNS(SVG_NS, 'g');
  group.setAttribute('transform', `translate(${offsetX},${offsetY}) scale(${scale})`);

  Object.values(nodeRegistry).forEach(node => {
    if (node._x === undefined) return;

    const isQuestion = !!node.answers;
    const isPattern  = node.pattern !== undefined;
    const w = isPattern ? PATTERN_NODE_WIDTH  : (isQuestion ? QUESTION_NODE_WIDTH  : ANSWER_NODE_WIDTH);
    const h = isPattern ? PATTERN_NODE_HEIGHT : (isQuestion ? QUESTION_NODE_HEIGHT : ANSWER_NODE_HEIGHT);

    const rect = document.createElementNS(SVG_NS, 'rect');
    rect.setAttribute('x',       node._x);
    rect.setAttribute('y',       node._y);
    rect.setAttribute('width',   w);
    rect.setAttribute('height',  h);
    rect.setAttribute('rx',      4);
    rect.setAttribute('fill',    isPattern ? '#2b6cb0' : (isQuestion ? '#3a3a38' : '#1a3a2a'));
    rect.setAttribute('opacity', '0.8');
    group.appendChild(rect);
  });

  minimapSvg.appendChild(group);
  updateMinimapViewport();
}

function updateMinimapViewport() {
  const wrapper = document.getElementById('canvas-wrap');
  const mmScale = Math.min(MINIMAP_WIDTH / canvasWidth, MINIMAP_HEIGHT / canvasHeight) * 0.9;
  const offsetX = (MINIMAP_WIDTH  - canvasWidth  * mmScale) / 2;
  const offsetY = (MINIMAP_HEIGHT - canvasHeight * mmScale) / 2;

  const viewportW = wrapper.clientWidth;
  const viewportH = wrapper.clientHeight - 54;

  const vpX = (-panX / zoomScale) * mmScale + offsetX;
  const vpY = (-panY / zoomScale) * mmScale + offsetY;
  const vpW = (viewportW / zoomScale) * mmScale;
  const vpH = (viewportH / zoomScale) * mmScale;

  const viewport = document.getElementById('minimap-viewport');
  viewport.style.left   = Math.max(0, vpX) + 'px';
  viewport.style.top    = Math.max(0, vpY) + 'px';
  viewport.style.width  = Math.min(MINIMAP_WIDTH,  vpW) + 'px';
  viewport.style.height = Math.min(MINIMAP_HEIGHT, vpH) + 'px';
}

// --- TRACE SEARCH UI ----------------------------------------------------------

/**
 * Rebuilds the dropdown list of request IDs, filtered by the given search string.
 */
function buildRequestIdList(filter = '') {
  const listEl  = document.getElementById('trace-list');
  listEl.innerHTML = '';
  predictButton.disabled = true;

  const filterLower = filter.toLowerCase();

  requestIds
    .filter(id => id.toLowerCase().includes(filterLower))
    .forEach(id => {
      const item = document.createElement('div');
      item.className = 'trace-item' + (activeTrace === id ? ' active' : '');
      item.innerHTML = `<div class="trace-id">${id}</div>`;
      item.onclick   = () => {
        activeTrace = id;
        document.getElementById('trace-search').value = id;
        listEl.classList.remove('open');
        predictButton.disabled = false;
        applyTrace(id);
      };
      listEl.appendChild(item);
    });
}

// Clear input and rebuild list when the user focuses the search field
const searchInput = document.getElementById('trace-search');
searchInput.addEventListener('focus', () => {
  if (activeTrace) {
    searchInput.value = '';
    buildRequestIdList('');
    predictButton.disabled = true;
  }
});

searchInput.addEventListener('input', e => {
  buildRequestIdList(e.target.value);
  document.getElementById('trace-list').classList.add('open');
});

searchInput.addEventListener('focus', () => {
  buildRequestIdList(searchInput.value);
  document.getElementById('trace-list').classList.add('open');
});

// Close dropdown when clicking outside the search widget
document.addEventListener('click', e => {
  if (!document.getElementById('trace-dropdown').contains(e.target)) {
    document.getElementById('trace-list').classList.remove('open');
  }
});

// Clear the active trace and reset the search field
document.getElementById('clear-trace-btn').onclick = () => {
  activeTrace = null;
  searchInput.value = '';
  predictButton.disabled = true;
  applyTrace(null);
};

// --- TAB CHANGE LISTENER ------------------------------------------------------

// Reset zoom when the user switches back to this tab, so the tree is centered.
document.addEventListener("DOMContentLoaded", () => {
  const tabObserver = new MutationObserver(() => {
    const tabButton = document.querySelector(
      '[data-bs-toggle="tab"][data-bs-target="#tab-ai_addons_pattern_prediction"]'
    );
    if (tabButton && !tabButton.dataset.listenerSet) {
      tabButton.addEventListener("click", () => {
        if (typeof resetZoom === "function") setTimeout(resetZoom, 100);
      });
      tabButton.dataset.listenerSet = "true";
      tabObserver.disconnect();
    }
  });
  tabObserver.observe(document.body, { childList: true, subtree: true });
});

// --- INITIALISATION -----------------------------------------------------------

async function loadTreeData() {
  const [idsResponse, treeResponse] = await Promise.all([
    fetch("/ai_addons/ui/api/pattern_prediction/req_ids"),
    fetch("/ai_addons/ui/api/pattern_prediction/tree"),
  ]);

  requestIds = await idsResponse.json();
  treeData   = await treeResponse.json();

  console.log("Request IDs:", requestIds);
  console.log("Tree data:",   treeData);

  renderTree();
}

loadTreeData();