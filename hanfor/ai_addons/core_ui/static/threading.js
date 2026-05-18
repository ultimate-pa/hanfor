const GROUP_COLORS = [
  '#3b338f', '#0b937d', '#0b539a', '#985608',
  '#6e6e69', '#8f3518', '#832446', '#4a7a2e',
  '#6b2d8f', '#1a6b6b', '#8f6b00', '#2d4a8f',
];

const ADDON_NAME = 'threading';
const TAB_ID     = 'ai_addons_threading';


// --------------------------------------------------------------------------------
// SOCKET SUBSCRIPTIONS
// --------------------------------------------------------------------------------

window.tabSubs.register(TAB_ID, [
  {
    event:   'socket_threading',
    handler: newData => { if (newData) render(normalise(newData)); },
  },
]);

window.tabSubs.onActivate(TAB_ID, load);


// --------------------------------------------------------------------------------
// ACTIONS
// --------------------------------------------------------------------------------

async function stopGroup(group) {
  window.showBanner(`Trying to stop: ${group}`, 'info', 'thread-info-banner');
  const data = await window.post(ADDON_NAME, 'stop-group/' + group);
  window.showBanner(data.info, 'success', 'thread-info-banner');
}


// --------------------------------------------------------------------------------
// STYLES - inject only the coloured badge backgrounds for the groups, nothing structural
// --------------------------------------------------------------------------------

function injectGroupStyles(groups) {
  document.getElementById('group-badge-styles')?.remove();

  const css = groups
    .map((g, i) => `.badge-group-${CSS.escape(g)} { background-color: ${GROUP_COLORS[i % GROUP_COLORS.length]} !important; color: #fff !important; }`)
    .join('\n');

  const style       = document.createElement('style');
  style.id          = 'group-badge-styles';
  style.textContent = css;
  document.head.appendChild(style);
}


// --------------------------------------------------------------------------------
// HELPERS
// --------------------------------------------------------------------------------

async function cancelTask(taskId) {
  const data = await window.del(ADDON_NAME, 'task/' + taskId);
  window.showBanner(data.info, 'success', 'thread-info-banner');
}

function taskRow({ function: fn, group, scheduling_class, task_id, status, queued_at, started_at, info_text }) {
  const isCancelling = status === 'cancel requested';
  const ts = started_at ?? queued_at;

  return `
    <div class="d-flex align-items-center gap-2 px-3 py-2 border-bottom" style="font-size:12px; white-space:nowrap;">
      <span class="fw-medium flex-grow-1">${fn}() -|- ${info_text} -|- <span class="text-muted">${status}</span></span>
      <span class="badge badge-group-${group}">${group}</span>
      <span class="badge text-bg-secondary">${scheduling_class}</span>
      <span class="text-muted font-monospace" style="font-size:11px; min-width:48px; text-align:right;" data-since="${ts}">0s</span>
      <button
        class="btn btn-sm btn-outline-danger py-0 px-2${isCancelling ? ' disabled' : ''}"
        data-task-id="${task_id}"
        ${isCancelling ? 'disabled' : ''}
        style="font-size:11px; line-height:1.6;"
      >${isCancelling ? '…' : '✕'}</button>
    </div>`;
}

function formatElapsed(seconds) {
  if (seconds < 60)   return `${Math.floor(seconds)}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.floor(seconds % 60)}s`;
  return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
}

function tickElapsed() {
  const now = Date.now() / 1000;
  document.querySelectorAll('[data-since]').forEach(el => {
    el.textContent = formatElapsed(now - parseFloat(el.dataset.since));
  });
}

setInterval(tickElapsed, 1000);

function buildGroupCounts(groups, activeTasks, queuedTasks) {
  const counts = Object.fromEntries(groups.map(g => [g, { running: 0, queued: 0 }]));
  activeTasks.forEach(t => { if (counts[t.group]) counts[t.group].running++; });
  queuedTasks.forEach(t => { if (counts[t.group]) counts[t.group].queued++;  });
  return counts;
}


// --------------------------------------------------------------------------------
// RENDER
// --------------------------------------------------------------------------------

function renderMetrics({ active_count, max_threads, queue_size, free_count }) {
  document.getElementById('th-metric-active').textContent = active_count;
  document.getElementById('th-metric-max').textContent    = max_threads;
  document.getElementById('th-metric-queue').textContent  = queue_size;

  const freeEl = document.getElementById('th-metric-free');
  freeEl.textContent = free_count;
  freeEl.className = `fs-4 fw-semibold ${free_count === 0 ? 'text-danger' : free_count <= 2 ? 'text-warning' : 'text-success'}`;

  const pct = max_threads > 0 ? Math.round(active_count / max_threads * 100) : 0;
  const bar = document.getElementById('th-load-bar');
  bar.style.width = `${pct}%`;
  bar.className   = `progress-bar ${pct >= 90 ? 'bg-danger' : pct >= 60 ? 'bg-warning' : 'bg-success'}`;
}

function renderGroups(groups, counts) {
  const container = document.getElementById('th-groups-row');

  groups.forEach(g => {
    const { running, queued } = counts[g];
    const idle = running === 0 && queued === 0;

    let card = container.querySelector(`[data-group="${g}"]`);
    if (!card) {
      card = document.createElement('div');
      card.className     = 'd-flex align-items-center gap-2 border rounded px-3 py-2';
      card.style.fontSize = '12px';
      card.dataset.group  = g;
      card.innerHTML = `
        <span class="badge badge-group-${g}">${g}</span>
        <span class="text-muted" data-counts></span>
        <button class="btn btn-sm btn-outline-danger py-0 px-2" style="font-size:11px;">STOP</button>
      `;
      card.querySelector('button').addEventListener('click', () => stopGroup(g));
      container.appendChild(card);
    }

    card.querySelector('[data-counts]').textContent = `${running} running · ${queued} queued`;
    card.querySelector('button').disabled = idle;
  });
}

function renderTaskList(elementId, tasks) {
  const el = document.getElementById(elementId);
  el.innerHTML = tasks.length
    ? tasks.map(taskRow).join('')
    : `<p class="text-muted px-3 py-2 mb-0" style="font-size:12px;">${elementId === 'th-running-list' ? 'No active tasks.' : 'Queue is empty.'}</p>`;

  tickElapsed();

  el.querySelectorAll('button[data-task-id]').forEach(btn => {
    btn.addEventListener('click', () => cancelTask(btn.dataset.taskId));
  });
}

function render(data) {
  injectGroupStyles(data.groups);
  renderMetrics(data);

  const counts = buildGroupCounts(data.groups, data.active_tasks, data.queued_tasks);
  renderGroups(data.groups, counts);

  renderTaskList('th-running-list', data.active_tasks);
  renderTaskList('th-queue-list',   data.queued_tasks);
}


// --------------------------------------------------------------------------------
// DATA
// --------------------------------------------------------------------------------

function normalise(data) {
  return {
    ...data,
    active_count: data.active_tasks.length,
    free_count:   data.max_threads - data.active_tasks.length,
    queue_size:   data.queued_tasks.length,
  };
}

async function load() {
  const res = await window.get(ADDON_NAME, '');
  render(normalise(res));
}