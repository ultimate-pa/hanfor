import ApiClient from "../api/ApiClient.js"
import TrackedStore from "../store/TrackedStore.js"
import { read_formalization_card } from "./formalization-card.js"

const api = new ApiClient()
const store = new TrackedStore()

store.registerType("formalization", {
  readDOM(id) {
    const card = $(`.formalization_card[title="${id}"]`)
    if (!card.length) return null
    return { temp_id: String(id), ...read_formalization_card(card) }
  },
  persistCreate: (rid, drafts) => api.createMany(rid, "formalization", drafts),
  persistDelete: (rid, id) => api.deleteFormalization(rid, id),
  persistPatch: (rid, id, entry) => api.patchFormalization(rid, id, entry),
})

store.registerType("variable", {
  readDOM(id) {
    const $card = $(`.accordion-item[data-id="${id}"][data-type="variable"]`)
    if (!$card.length) return null

    const data = { temp_id: String(id), enumerators: [] }

    const $nameInput = $card.find('input[aria-describedby="variable-name-feedback"]')
    data.name = $nameInput.val() || ""
    data.id = data.name

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
  declaresNames: true,
  persistCreate: (rid, drafts) => api.createMany(rid, "variable", drafts),
  persistDelete: (rid, id) => api.deleteFormalization(rid, id),
  persistPatch: (rid, id, entry) => api.patchFormalization(rid, id, entry),
})

export default store
