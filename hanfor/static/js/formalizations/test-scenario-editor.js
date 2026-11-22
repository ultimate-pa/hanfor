// Timeline editor of a test scenario.
//
// One row per lane (a boolean expression, e.g. `var1` or `speed > 5`), one column per interval.
// A click on a cell cycles the lane through true, false and don't care.
//
// The state lives as jQuery data on the accordion item (read by readTestScenario in test-scenarios.js):
//   $item.data("lanes") -> ["var1", "speed > 5"]
//   $item.data("steps") -> [{ duration: 5, states: { var1: false, "speed > 5": true } }]
// A lane missing in `states` is "don't care".

const CELL = {
  true: { css: "bg-success-subtle", text: "1" },
  false: { css: "bg-danger-subtle", text: "0" },
  null: { css: "bg-body-secondary", text: "–" },
}

function stateOf(step, lane) {
  const value = step.states[lane]
  return value === true || value === false ? value : null
}

/**
 * @param $item accordion item of the scenario (contains `.ts-timeline`)
 * @param options.lanes initial lanes
 * @param options.steps initial steps `[{duration, states}]`
 * @param options.variables () => string[] names for the drop down
 * @param options.onChange () => void called after every edit
 */
export function initTimelineEditor($item, options) {
  const $root = $item.find(".ts-timeline")
  const listId = `ts-vars-${$item.data("id")}`
  const state = {
    lanes: [...options.lanes],
    steps: options.steps.map((s) => ({ duration: Number(s.duration), states: { ...s.states } })),
  }
  if (state.steps.length === 0) state.steps.push({ duration: 1, states: {} })

  const changed = () => {
    $item.data({ lanes: state.lanes, steps: state.steps })
    options.onChange()
    render()
  }

  function render() {
    const $table = $('<table class="table table-sm table-bordered align-middle text-center mb-2">')
    state.lanes.forEach((lane, laneIndex) => {
      const $row = $("<tr>").append(
        $('<th class="text-start font-monospace">').append(
          $("<span>").text(lane),
          $('<button type="button" class="btn-close btn-sm float-end ts-remove-lane" title="Remove lane">')
            .attr("data-lane", laneIndex),
        ),
      )
      state.steps.forEach((step, stepIndex) => {
        const cell = CELL[String(stateOf(step, lane))]
        $row.append(
          $('<td class="ts-cell" role="button" title="Click: true → false → don\'t care">')
            .addClass(cell.css)
            .attr({ "data-lane": laneIndex, "data-step": stepIndex })
            .text(cell.text),
        )
      })
      $table.append($row)
    })

    // last row: the duration of every interval
    const $durations = $("<tr>").append('<th class="text-start text-muted">Duration (s)</th>')
    state.steps.forEach((step, stepIndex) => {
      $durations.append(
        $("<td>").append(
          $('<div class="input-group input-group-sm" style="min-width: 7rem">').append(
            $('<input type="number" min="0" step="any" class="form-control ts-duration">')
              .val(step.duration)
              .attr("data-step", stepIndex),
            $('<button type="button" class="btn btn-outline-danger ts-remove-step" title="Remove interval">×</button>')
              .attr("data-step", stepIndex)
              .prop("disabled", state.steps.length <= 1),
          ),
        ),
      )
    })
    $durations.append('<td><button type="button" class="btn btn-sm btn-success ts-add-step">+ Interval</button></td>')
    $table.append($durations)

    const $datalist = $("<datalist>").attr("id", listId)
    options.variables().forEach((v) => $datalist.append($("<option>").attr("value", v)))
    const $addLane = $('<div class="input-group input-group-sm" style="max-width: 640px">').append(
      '<span class="input-group-text">Add lane</span>',
      $('<input type="text" class="form-control ts-lane-input" autocomplete="off">').attr({
        list: listId,
        placeholder: "A boolean variable or formula, e.g. speed > 5",
      }),
      '<button type="button" class="btn btn-success ts-add-lane">+</button>',
    )
    $root.empty().append($('<div class="table-responsive">').append($table), $addLane, $datalist)
  }

  const addLane = () => {
    const lane = $root.find(".ts-lane-input").val().trim()
    if (!lane || state.lanes.includes(lane)) return
    state.lanes.push(lane)
    changed()
    $root.find(".ts-lane-input").trigger("focus")
  }

  // handlers are bound once, `render` only replaces the content
  $root
    .on("click", ".ts-cell", function () {
      const lane = state.lanes[Number($(this).attr("data-lane"))]
      const step = state.steps[Number($(this).attr("data-step"))]
      const current = stateOf(step, lane)
      if (current === true) step.states[lane] = false
      else if (current === false) delete step.states[lane]
      else step.states[lane] = true
      changed()
    })
    .on("click", ".ts-remove-lane", function () {
      const [lane] = state.lanes.splice(Number($(this).attr("data-lane")), 1)
      state.steps.forEach((s) => delete s.states[lane])
      changed()
    })
    .on("change", ".ts-duration", function () {
      const step = state.steps[Number($(this).attr("data-step"))]
      const value = parseFloat($(this).val())
      if (Number.isFinite(value) && value > 0) {
        step.duration = value
        changed()
      } else {
        $(this).val(step.duration)
      }
    })
    .on("click", ".ts-remove-step", function () {
      state.steps.splice(Number($(this).attr("data-step")), 1)
      changed()
    })
    .on("click", ".ts-add-step", function () {
      // the new interval starts as a copy of the last one
      const last = state.steps[state.steps.length - 1]
      state.steps.push({ duration: last.duration, states: { ...last.states } })
      changed()
    })
    .on("click", ".ts-add-lane", addLane)
    .on("keydown", ".ts-lane-input", function (e) {
      if (e.key !== "Enter") return
      e.preventDefault()
      addLane()
    })

  $item.data({ lanes: state.lanes, steps: state.steps })
  render()
}
