export default class FormalizationStore {
  constructor() {
    this.created = new Map()
    this.deleted = new Map()
    this.nextId = null
  }

  initNextId(nextId) {
    this.nextId = nextId
  }

  generateId() {
    return this.nextId++
  }

  getSet(map, type) {
    if (!map.has(type)) {
      map.set(type, new Set())
    }
    return map.get(type)
  }

  create(type) {
    const id = this.generateId()
    this.getSet(this.created, type).add(id)
    return id
  }

  delete(type, id) {
    id = Number(id)
    console.log("DELETE called with:", id, typeof id)
    const createdSet = this.getSet(this.created, type)
    const deletedSet = this.getSet(this.deleted, type)
    console.log("createdSet BEFORE:", [...createdSet])
    if (createdSet.has(id)) {
      console.log("Removing from created")
      createdSet.delete(id)
    } else {
      console.log("Adding to deleted")
      deletedSet.add(id)
    }
    console.log("createdSet AFTER:", [...createdSet])
    console.log("deletedSet AFTER:", [...deletedSet])
  }

  isCreated(type, id) {
    return this.getSet(this.created, type).has(Number(id))
  }

  getFormalizationFromDOM(id) {
    const card = $(`.formalization_card[title="${id}"]`)
    if (!card.length) return {}

    const formalization = { id: id, expression_mapping: {} }

    card.find("select").each(function () {
      if ($(this).hasClass("scope_selector")) formalization.scope = $(this).val()
      if ($(this).hasClass("pattern_selector")) formalization.pattern = $(this).val()
    })

    card.find("textarea.reqirement-variable").each(function () {
      const title = $(this).attr("title")
      if (title) formalization.expression_mapping[title] = $(this).val()
    })

    return formalization
  }

  getVariableFromDOM(id) {
    const $card = $(`.accordion-item[data-id="${id}"][data-type="variable"]`)
    if (!$card.length) return {}

    const data = { id: id }

    const $nameInput = $card.find('input[aria-describedby="variable-name"]')
    data.name = $nameInput.val() || ""
    data.id = data.name
    data.temp_id = id
    const $typeInput = $card.find("input.variable-type")
    data.type = $typeInput.val() || ""
    const $variableValue = $card.find("input.variable-value")
    data.value = $variableValue.val() || ""

    return data
  }

  commitDeletes(requirementId, type) {
    const requests = []
    const deletedSet = this.getSet(this.deleted, type)
    console.log("Deleted set: ", deletedSet)

    deletedSet.forEach((id) => {
      requests.push(
        $.ajax({
          url: `/api/req/formalizations/${requirementId}/${id}`,
          type: "DELETE",
        }),
      )
    })
    deletedSet.clear()
    return Promise.all(requests)
  }

  commitCreated(requirementId) {
    const requests = []
    for (const [type, idSet] of this.created.entries()) {
      idSet.forEach((id) => {
        let data = {}
        let endpoint = ""
        if (type === "formalization") {
          data = this.getFormalizationFromDOM(id)
          endpoint = `/api/req/formalizations/${requirementId}/formalization/${id}`
        } else if (type === "variable") {
          data = this.getVariableFromDOM(id)
          endpoint = `/api/req/formalizations/${requirementId}/variable/${id}`
        }

        requests.push($.post(endpoint, { id: requirementId, data: JSON.stringify(data) }))
      })
    }
    this.created.clear()
    return Promise.all(requests)
  }
}
