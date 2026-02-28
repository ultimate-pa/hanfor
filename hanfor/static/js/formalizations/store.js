export default class FormalizationStore {
  constructor() {
    this.created = new Set()
    this.deleted = new Set()
    this.nextId = null
  }

  initNextId(nextId) {
    this.nextId = nextId
  }

  generateId() {
    return this.nextId++
  }

  create() {
    const id = this.generateId()
    this.created.add(id)
    return id
  }

  delete(id) {
    id = Number(id)
    if (this.created.has(id)) {
      // just cancel here if it just has been created
      this.created.delete(id)
    } else {
      this.deleted.add(id)
    }
  }

  getFormalizationFromDOM(id) {
    const card = $(`.formalization_card[title="${id}"]`)
    if (!card.length) return {}
    const formalization = { id: id, expression_mapping: {} }

    // Scope and pattern
    card.find("select").each(function () {
      if ($(this).hasClass("scope_selector")) formalization.scope = $(this).val()
      if ($(this).hasClass("pattern_selector")) formalization.pattern = $(this).val()
    })
    // Expressions
    card.find("textarea.reqirement-variable").each(function () {
      const title = $(this).attr("title")
      if (title) formalization.expression_mapping[title] = $(this).val()
    })

    return formalization
  }

  commitDeletes(requirementId) {
    const requests = []
    for (const deletedId of this.deleted) {
      requests.push($.post(`/api/req/formalizations/${requirementId}/delete/${deletedId}`))
    }
    this.deleted.clear()
    return Promise.all(requests)
  }

  commitCreated(requirementId) {
    const requests = []
    this.created.forEach((id) => {
      const data = this.getFormalizationFromDOM(id)
      const req = $.post(`/api/req/formalizations/${requirementId}/new/formalization/${id}`, {
        id: requirementId,
        data: JSON.stringify(data),
      })
      requests.push(req)
    })
    this.created.clear()
    return Promise.all(requests)
  }
}
