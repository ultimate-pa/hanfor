// Test scenario cards, shared by the requirement modal (scenarios of one requirement) and the test scenarios page
// (the global ones). The card is the `test_scenario` template in the accordion `container`, the timeline is
// `test-scenario-editor.js`, saving goes to /api/v1/test_scenarios.
//
// Card ids: a saved scenario is `ts-<id>`, a new one the temporary id of the TrackedStore (`tmp-<n>`), so they never
// collide with the ids of the formalizations in the same accordion.
import { initTimelineEditor } from "./test-scenario-editor.js"

export const TYPE = "test_scenario"

// how the last Ultimate result (`ultimate_result` of the API) is shown
const RESULT_STYLES = {
  passed: { alert: "success", badge: "bg-success", label: "passed" },
  failed: { alert: "danger", badge: "bg-danger", label: "failed" },
  not_analyzed: { alert: "secondary", badge: "bg-secondary", label: "not analyzed" },
  error: { alert: "warning", badge: "bg-warning text-dark", label: "error" },
}

/** View of `ultimate_result` for the template, null if there is none. */
export function resultView(scenario) {
  const result = scenario.ultimate_result
  if (!result || !result.status) return null
  const style = RESULT_STYLES[result.status] || RESULT_STYLES.error
  return { ...style, ...result, name: scenario.name }
}

const cardId = (scenarioId) => `ts-${scenarioId}`
const scenarioId = (id) => String(id).replace(/^ts-/, "")
const cardSelector = (id) => `.accordion-item[data-type="${TYPE}"][data-id="${id}"]`

/**
 * @param renderer TemplateRenderer
 * @param options.variables () => string[] names for the drop down
 * @param options.onChange () => void called after every edit
 */
export function registerTestScenarioType(renderer, options) {
  renderer.registerType(TYPE, {
    defaults: {
      formalization_type: TYPE,
      desired_behavior: true,
      name: "",
      description: "",
      lanes: [],
      steps: [],
    },
    template: "test_scenario",
    container: "container",
    contentSelector: ".accordion-collapse",
    afterRender: ($container, entry) => {
      const $item = $container.closest(".accordion-item")
      const $title = $item.find(".accordion-button")
      const markDirty = () => {
        $item.addClass("draft")
        options.onChange()
      }

      $item.find(".ts-behavior").val(String(entry.desired_behavior))
      const $titleName = $("<span>").text(entry.name || "New test scenario")
      $title.empty().append($titleName)
      if (entry.result) {
        $title.append($("<span>").addClass(`badge ${entry.result.badge} ms-2`).text(entry.result.label))
      }
      $item.on("input change", ".ts-name, .ts-description, .ts-behavior", markDirty)
      $item.on("input", ".ts-name", function () {
        $titleName.text($(this).val() || entry.name || "New test scenario")
      })

      initTimelineEditor($item, {
        lanes: entry.lanes,
        steps: entry.steps,
        variables: options.variables,
        onChange: markDirty,
      })
    },
  })
}

/** Card of a saved scenario, as returned by the API. */
export function buildSavedCard(renderer, scenario) {
  return renderer.build(TYPE, { ...scenario, id: cardId(scenario.id), result: resultView(scenario) })
}

/** Card of a new scenario, tracked by `store` until it is saved. */
export function buildNewCard(renderer, store) {
  return renderer.build(TYPE, { id: store.create(TYPE) }).addClass("draft")
}

/** What a card holds, in the shape the API takes. */
export function readTestScenario($item) {
  return {
    name: $item.find(".ts-name").val() || "",
    description: $item.find(".ts-description").val() || "",
    desired_behavior: $item.find(".ts-behavior").val() === "true",
    lanes: $item.data("lanes") || [],
    steps: $item.data("steps") || [],
  }
}

/** For `store.registerType(TYPE, ...)`: new cards are created, deleted ones removed when the store commits. */
export function storeConfig(api) {
  return {
    readDOM(id) {
      const $item = $(cardSelector(id))
      return $item.length ? { temp_id: String(id), ...readTestScenario($item) } : null
    },
    // `requirementId` "" = global
    persistCreate(requirementId, drafts) {
      const ids = {}
      const errors = {}
      const requests = drafts.map(({ temp_id, ...data }) =>
        api
          .createTestScenario({ ...data, requirement_id: requirementId })
          .then((response) => {
            ids[temp_id] = cardId(response.scenario.id)
          })
          .catch((err) => {
            errors[temp_id] = err?.responseJSON?.errormsg || err?.statusText
          }),
      )
      return Promise.all(requests).then(() => {
        if (Object.keys(errors).length) throw { responseJSON: { ids, errors } }
        return { ids }
      })
    },
    persistDelete: (requirementId, id) => api.deleteTestScenario(scenarioId(id)),
  }
}

/**
 * Save every change of the cards of type test_scenario: deleted ones, new ones and edited ones.
 * Rejects with `{responseJSON: {errors: {cardId: message}}}` if some could not be saved.
 */
export async function saveTestScenarios(api, store, requirementId) {
  await store.commitDeletes(requirementId, TYPE)

  const errors = {}
  try {
    await store.commitCreated(requirementId, TYPE)
  } catch (err) {
    Object.assign(errors, err?.responseJSON?.errors)
  }
  // created cards get their real id, so a later save changes them instead of creating them again
  $(`.accordion-item[data-type="${TYPE}"]`).each(function () {
    const id = String($(this).data("id"))
    const saved = String(store.resolveId(id))
    if (saved === id) return
    $(this).attr("data-id", saved).data("id", saved).removeClass("draft")
    $(this).find(".delete_test_scenario").attr("name", saved)
  })

  const edited = $(`.accordion-item.draft[data-type="${TYPE}"]`)
    .toArray()
    .map((item) => $(item))
    .filter(($item) => String($item.data("id")).startsWith("ts-"))
  const results = await Promise.allSettled(
    edited.map(($item) => api.updateTestScenario(scenarioId($item.data("id")), readTestScenario($item))),
  )
  results.forEach((result, i) => {
    const $item = edited[i]
    if (result.status === "fulfilled") {
      $item.removeClass("draft")
    } else {
      errors[$item.data("id")] = result.reason?.responseJSON?.errormsg || result.reason?.statusText
    }
  })

  if (Object.keys(errors).length) throw { responseJSON: { errors } }
}
