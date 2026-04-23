const GROUP_COLORS = [
  '#3b338f', '#0b937d', '#0b539a', '#985608',
  '#6e6e69', '#8f3518', '#832446', '#4a7a2e',
  '#6b2d8f', '#1a6b6b', '#8f6b00', '#2d4a8f',
];

// -- STYLE INJECTION -----------------------------------------------------------

function injectGroupStyles(groups) {
  document.getElementById('group-badge-styles')?.remove();

  const rules = groups.map((g, i) =>
    `.badge-${CSS.escape(g)} { background: ${GROUP_COLORS[i % GROUP_COLORS.length]}; }`
  ).join('\n');

  const style = document.createElement('style');
  style.id          = 'group-badge-styles';
  style.textContent = rules;
  document.head.appendChild(style);
}

// -- HELPERS -------------------------------------------------------------------

function taskRow(t) {
  return `
    <div class="task-row">
      <span class="task-fn">${t.function}</span>
      <span style="flex:1"></span>
      <span class="badge badge-${t.group}">${t.group}</span>
      <span class="badge badge-sc">${t.scheduling_class}</span>
      <span class="prio">p${t.priority}</span>
    </div>`;
}

// -- RENDER --------------------------------------------------------------------

function renderGroups(d, byGroup) {
  const container = document.getElementById('groups-row');

  d.groups.forEach(g => {
    const cnt  = byGroup[g];
    const idle = cnt.running === 0 && cnt.queued === 0;
    let card   = container.querySelector(`[data-group="${g}"]`);

    if (!card) {
      card = document.createElement('div');
      card.className    = 'group-card';
      card.dataset.group = g;
      card.innerHTML = `
        <span class="badge badge-${g}">${g}</span>
        <div class="group-counts"></div>
        <button class="stop-btn" onclick="stopGroup('${g}')">STOP</button>
      `;
      container.appendChild(card);
    }

    card.querySelector('.group-counts').textContent = `${cnt.running} aktiv · ${cnt.queued} in Queue`;
    card.querySelector('.stop-btn').disabled = idle;
  });
}

function render(d) {
  injectGroupStyles(d.groups);

  document.getElementById('m-active').textContent = d.active_count;
  document.getElementById('m-max').textContent    = d.max_threads;
  document.getElementById('m-queue').textContent  = d.queue_size;

  const freeEl = document.getElementById('m-free');
  freeEl.textContent = d.free_count;
  freeEl.className   = 'metric-value ' + (d.free_count === 0 ? 'bad' : d.free_count <= 2 ? 'warn' : 'ok');

  const pct = d.max_threads > 0 ? Math.round(d.active_count / d.max_threads * 100) : 0;
  const bar = document.getElementById('load-bar');
  bar.style.width = pct + '%';
  bar.className   = 'bar-fill' + (pct >= 90 ? ' danger' : pct >= 60 ? ' warn' : '');

  // Build per-group counts
  const byGroup = Object.fromEntries(d.groups.map(g => [g, { running: 0, queued: 0 }]));
  d.active_tasks.forEach(t  => { if (byGroup[t.group]) byGroup[t.group].running++; });
  d.queued_tasks.forEach(t  => { if (byGroup[t.group]) byGroup[t.group].queued++;  });

  renderGroups(d, byGroup);

  document.getElementById('running-list').innerHTML = d.active_tasks.length
    ? d.active_tasks.map(taskRow).join('')
    : '<div class="empty">No active tasks</div>';

  document.getElementById('queue-list').innerHTML = d.queued_tasks.length
    ? d.queued_tasks.map(taskRow).join('')
    : '<div class="empty">Queue is empty</div>';
}

// -- DATA ----------------------------------------------------------------------

function normalise(data) {
  data.active_count = data.active_tasks.length;
  data.free_count   = data.max_threads - data.active_count;
  data.queue_size   = data.queued_tasks.length;
  return data;
}

async function load() {
  try {
    const res = await fetch(`${window.baseUrl}/threading`);
    if (!res.ok) throw new Error(res.status);
    let json_res = await res.json()
    render(normalise(json_res));
    console.log(json_res);
  } catch {
    document.getElementById('last-update').textContent = 'Fehler beim Laden';
  }
}

// -- SOCKET SUBSCRIPTIONS --------------------------------------------------------------------

window.tabSubs.register('ai_addons_threading', [
  {
    event:   'socket_threading',
    handler: newData => {
      if (newData) render(normalise(newData)); },
  },
]);

window.tabSubs.onActivate('ai_addons_threading', load);

// -- ACTIONS -------------------------------------------------------------------

async function stopGroup(group) {
  window.showBanner(`try stopping: ${group}`, 'success', 'thread-info-banner');
  const res = await fetch(`${window.baseUrl}/threading/stop_group/${group}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(res.status);
  const data = await res.json();
  window.showBanner(data.info, 'success', 'thread-info-banner');
}


window.addDummyTask = async function () {
  try { await fetch('/threading/dummy_task', { method: 'POST' }); }
  catch { /* swallow */ }
};

window.stopGroup = stopGroup;