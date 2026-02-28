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

  commitDeletes(requirementId) {
    const requests = []
    for (const deletedId of this.deleted) {
      requests.push($.post(`/api/req/formalizations/${requirementId}/delete/${deletedId}`))
    }
    this.deleted.clear()
    return Promise.all(requests)
  }
}
