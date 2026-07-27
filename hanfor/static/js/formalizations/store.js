import ApiClient from "../api/ApiClient.js"
import TrackedStore from "../store/TrackedStore.js"

const api = new ApiClient()
const store = new TrackedStore()

store.registerType("formalization", {
  readDOM(id) {
    const card = $(`.formalization_card[title="${id}"]`)
    if (!card.length) return null

    const data = { id: Number(id), expression_mapping: {} }

    card.find("select").each(function () {
      if ($(this).hasClass("scope_selector")) data.scope = $(this).val()
      if ($(this).hasClass("pattern_selector")) data.pattern = $(this).val()
    })

    data.is_constraint = card.find(".is-constraint-checkbox").is(":checked")

    card.find("textarea.reqirement-variable").each(function () {
      const title = $(this).attr("title")
      if (title) data.expression_mapping[title] = $(this).val()
    })

    return data
  },
  persistCreate: (rid, data) => api.createFormalization(rid, data),
  persistDelete: (rid, id) => api.deleteFormalization(rid, id),
})

store.registerType("variable", {
  readDOM(id) {
    const $card = $(`.accordion-item[data-id="${id}"][data-type="variable"]`)
    if (!$card.length) return null

    const data = { id: id, enumerators: [] }

    const $nameInput = $card.find('input[aria-describedby="variable-name-feedback"]')
    data.name = $nameInput.val() || ""
    data.id = data.name
    data.temp_id = Number(id)

    const $typeInput = $card.find("input.variable-type")
    data.type = $typeInput.val() || ""

    const $variableValue = $card.find("input.variable-value")
    data.value = $variableValue.val() || ""

    $card.find(".enum_name_input").each(function (i) {
      const enumName = $(this).val() || ""
      const enumValue = $card.find(".enum_value_input").eq(i).val() || ""
      data.enumerators.push([enumName, enumValue])
    })

    return data
  },
  persistCreate: (rid, data) => api.createVariable(rid, data),
  persistDelete: (rid, id) => api.deleteFormalization(rid, id),
})

export default store
