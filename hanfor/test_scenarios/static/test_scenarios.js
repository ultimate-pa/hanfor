// Page of the global test scenarios (they belong to no requirement).
// The same cards and the same saving as the test scenarios in the requirement modal, see test-scenarios.js.
import ApiClient from "../../static/js/api/ApiClient.js"
import TemplateRenderer from "../../static/js/template/TemplateRenderer.js"
import TrackedStore from "../../static/js/store/TrackedStore.js"
import {
  TYPE,
  buildNewCard,
  buildSavedCard,
  registerTestScenarioType,
  saveTestScenarios,
  storeConfig,
} from "../../static/js/formalizations/test-scenarios.js"

require("bootstrap") // the accordion (collapse) of the cards, the layout does not load it
require("../../static/js/bootstrap-confirm-button")

const GLOBAL = "" // requirement id of a global scenario

const api = new ApiClient()
const renderer = new TemplateRenderer({ baseUrl: "/static/templates/formalizations" })
const store = new TrackedStore()
store.registerType(TYPE, storeConfig(api))

let unsaved = false
let variables = []

registerTestScenarioType(renderer, {
  variables: () => variables,
  onChange: () => (unsaved = true),
})

function updateEmptyHint() {
  $("#no_test_scenarios").toggleClass("d-none", $("#test_scenario_accordion .accordion-item").length > 0)
}

function showErrors(errors) {
  const lines = Object.entries(errors).map(([id, message]) => {
    const $item = $(`#test_scenario_accordion .accordion-item[data-id="${id}"]`).addClass("border-danger")
    return $("<div>").text(`${$item.find(".accordion-button").text().trim() || id}: ${message}`)
  })
  $("#test_scenario_save_error").empty().append(lines).removeClass("d-none")
}

function load() {
  return $.when(api.getTestScenarios(GLOBAL), api.getTestScenarioVariables()).done(([tests], [vars]) => {
    variables = vars.variables
    store.reset()
    const $list = $("#test_scenario_accordion").empty()
    tests.scenarios.forEach((scenario) => $list.append(buildSavedCard(renderer, scenario)))
    unsaved = false
    updateEmptyHint()
  })
}

$(document).ready(async () => {
  await renderer.ready()
  load()

  $("#add_test_scenario").on("click", () => {
    const $card = buildNewCard(renderer, store)
    $("#test_scenario_accordion").append($card)
    $card.find(".accordion-button").trigger("click") // open it
    unsaved = true
    updateEmptyHint()
  })

  // same two-click delete as in the requirement modal ("Do it!"), saved with the next save
  $("body").bootstrapConfirmButton({
    selector: ".delete_test_scenario",
    onConfirm: function () {
      store.delete(TYPE, $(this).attr("name"))
      $(this).closest(".accordion-item").remove()
      unsaved = true
      updateEmptyHint()
    },
  })

  $("#save_test_scenarios").on("click", () => {
    $("#test_scenario_save_error").addClass("d-none")
    $("#test_scenario_accordion .accordion-item").removeClass("border-danger")
    saveTestScenarios(api, store, GLOBAL)
      .then(() => load())
      .catch((err) => showErrors(err?.responseJSON?.errors || { "": err?.statusText || "Save failed" }))
  })

  $("#test_scenario_import").on("click", () => {
    const file = $("#test_scenario_import_file")[0].files[0]
    if (!file) return
    if (unsaved && !confirm("Unsaved changes on this page are lost by the import. Continue?")) return
    const $report = $("#test_scenario_import_report").removeClass("d-none alert-success alert-warning alert-danger")
    api
      .importTestScenarios(file, $("#test_scenario_import_replace").is(":checked"))
      .done((report) => {
        const lines = [`Imported: ${report.imported.length} (${report.imported.join(", ") || "-"})`]
        if (report.skipped.length) lines.push(`Skipped, name exists already: ${report.skipped.join(", ")}`)
        lines.push(...report.errors)
        $report
          .addClass(report.errors.length ? "alert-warning" : "alert-success")
          .empty()
          .append(lines.map((line) => $("<div>").text(line)))
        $("#test_scenario_import_file").val("")
        load()
      })
      .fail((err) => $report.addClass("alert-danger").text(err?.responseJSON?.errormsg || err.statusText))
  })

  window.addEventListener("beforeunload", (e) => {
    if (unsaved) e.preventDefault()
  })
})
