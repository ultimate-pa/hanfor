const GROUP_COLORS = [
  '#3b338f',
  '#0b937d',
  '#0b539a',
  '#985608',
  '#6e6e69',
  '#8f3518',
  '#832446',
  '#4a7a2e',
  '#6b2d8f',
  '#1a6b6b',
  '#8f6b00',
  '#2d4a8f',
];

function injectGroupStyles(groups) {
  const existing = document.getElementById('group-badge-styles');
  if (existing) existing.remove();

  const rules = groups.map((g, i) => {
    const c = GROUP_COLORS[i % GROUP_COLORS.length];
    return `.badge-${CSS.escape(g)} { background: ${c}; }`;
  }).join('\n');

  const style = document.createElement('style');
  style.id = 'group-badge-styles';
  style.textContent = rules;
  document.head.appendChild(style);
}

// -- Helpers -------------------------------------------------------------------

function taskRow(t) {
  return `<div class="task-row">
    <span class="task-fn">${t.function}</span>
    <span style="flex:1"></span>
    <span class="badge badge-${t.group}">${t.group}</span>
    <span class="badge badge-sc">${t.scheduling_class}</span>
    <span class="prio">p${t.priority}</span>
  </div>`;
}

// -- Render --------------------------------------------------------------------
function render(d) {
  injectGroupStyles(d.groups);
  document.getElementById('m-active').textContent = d.active_count;
  document.getElementById('m-max').textContent = d.max_threads;
  document.getElementById('m-queue').textContent = d.queue_size;

  const freeEl = document.getElementById('m-free');
  freeEl.textContent = d.free_count;
  freeEl.className = 'metric-value ' + (d.free_count === 0 ? 'bad' : d.free_count <= 2 ? 'warn' : 'ok');

  const pct = d.max_threads > 0 ? Math.round(d.active_count / d.max_threads * 100) : 0;
  const bar = document.getElementById('load-bar');
  bar.style.width = pct + '%';
  bar.className = 'bar-fill' + (pct >= 90 ? ' danger' : pct >= 60 ? ' warn' : '');

  // groups
  const byGroup = {};
  d.groups.forEach(g => byGroup[g] = {running: 0, queued: 0});
  d.active_tasks.forEach(t => {
    if (byGroup[t.group]) byGroup[t.group].running++;
  });
  d.queued_tasks.forEach(t => {
    if (byGroup[t.group]) byGroup[t.group].queued++;
  });

  document.getElementById('groups-row').innerHTML = d.groups.map(g => {
    const cnt = byGroup[g];
    const idle = cnt.running === 0 && cnt.queued === 0;
    return `<div class="group-card">
      <span class="badge badge-${g}">${g}</span>
      <div class="group-counts">${cnt.running} aktiv &middot; ${cnt.queued} in Queue</div>
      <button class="stop-btn" ${idle ? 'disabled' : ''} onclick="stopGroup('${g}')">STOP</button>
    </div>`;
  }).join('');

  document.getElementById('running-list').innerHTML = d.active_tasks.length
      ? d.active_tasks.map(taskRow).join('')
      : '<div class="empty">No active Tasks</div>';

  document.getElementById('queue-list').innerHTML = d.queued_tasks.length
      ? d.queued_tasks.map(taskRow).join('')
      : '<div class="empty">Queue is empty</div>';
}

// -- Load ----------------------------------------------------------------------
async function load() {
  try {
    const res = await fetch("/ai_addons/ui/api/threading/initial");
    if (!res.ok) throw new Error(res.status);
    const d = await res.json();
    d.active_count = d.active_tasks.length;
    d.free_count   = d.max_threads - d.active_count;
    d.queue_size   = d.queued_tasks.length;
    render(d);
  } catch {
    document.getElementById('last-update').textContent = 'Fehler beim Laden';
  }
}

// -- Stop group ----------------------------------------------------------------
async function stopGroup(group) {
  try {
    const res = await fetch("/ai_addons/ui/api/threading/stop_group", {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ group }),
    });
    if (!res.ok) throw new Error(res.status);
    const d = await res.json();
    d.active_count = d.active_tasks.length;
    d.free_count   = d.max_threads - d.active_count;
    d.queue_size   = d.queued_tasks.length;
    render(d);
  } catch {
  }
}

window.addDummyTask = async function addDummyTask() {
  try {
    const res = await fetch("/ai_addons/ui/api/threading/dummy_task", { method: 'POST' });
    if (!res.ok) throw new Error(res.status);
    const d = await res.json();
    d.active_count = d.active_tasks.length;
    d.free_count   = d.max_threads - d.active_count;
    d.queue_size   = d.queued_tasks.length;
    render(d);
  } catch {
  }
}

load();

window.stopGroup = stopGroup;