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

    const createdSet = this.getSet(this.created, type)
    const deletedSet = this.getSet(this.deleted, type)

    if (createdSet.has(id)) {
      createdSet.delete(id)
    } else {
      deletedSet.add(id)
    }
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

  commitDeletes(requirementId, type) {
    const requests = []
    const deletedSet = this.getSet(this.deleted, type)

    deletedSet.forEach((id) => {
      requests.push($.post(`/api/req/formalizations/${requirementId}/delete/${id}`))
    })

    deletedSet.clear()
    return Promise.all(requests)
  }

  commitCreated(requirementId, type) {
    const requests = []
    const createdSet = this.getSet(this.created, type)

    createdSet.forEach((id) => {
      if (type === "formalization") {
        const data = this.getFormalizationFromDOM(id)
        const req = $.post(`/api/req/formalizations/${requirementId}/new/formalization/${id}`, {
          id: requirementId,
          data: JSON.stringify(data),
        })

        requests.push(req)
      }

      if (type === "variable") {
        const req = $.post(`/api/req/formalizations/${requirementId}/new/variable/${id}`)

        requests.push(req)
      }
    })

    createdSet.clear()
    return Promise.all(requests)
  }
}
