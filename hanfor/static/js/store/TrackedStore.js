const errorMessage = err => err?.responseJSON?.errormsg || err?.statusText || "Unknown error"

export default class TrackedStore {
  constructor() {
    this._created = new Map()
    this._deleted = new Map()
    this._edited = new Map()
    this._types = new Map()
    this._assigned = new Map()
    this._counter = 0
  }

  registerType(type, config) {
    this._types.set(type, config)
  }

  _generateId() {
    return `tmp-${++this._counter}`
  }

  create(type) {
    const id = this._generateId()
    this._getSet(this._created, type).add(id)
    return id
  }

  edit(type, id) {
    id = String(id)
    if (!this.isCreated(type, id)) {
      this._getSet(this._edited, type).add(id)
    }
  }

  delete(type, id) {
    this._getSet(this._edited, type).delete(String(id))
    id = String(this.resolveId(id))
    if (this._getSet(this._created, type).has(id)) {
      this._getSet(this._created, type).delete(id)
    } else {
      this._getSet(this._deleted, type).add(id)
    }
  }

  isCreated(type, id) {
    return this._getSet(this._created, type).has(String(id))
  }

  hasNoDrafts(type = null) {
    for (const map of [this._created, this._deleted, this._edited]) {
      for (const [mapType, set] of map) {
        if ((type === null || mapType === type) && set.size > 0) return false
      }
    }
    return true
  }

  /**
   * Sends all deletes, creates and patches of all types. Rejects with {responseJSON: {errors}},
   * keyed by the card id, if one or more requests fail. Failed changes stay drafts.
   */
  async commit(parentId) {
    const errors = {}
    const requests = []
    for (const [type, config] of this._types) {
      requests.push(this._commitDeletes(parentId, type, config, errors))
      requests.push(this._commitCreated(parentId, type, config, errors))
      requests.push(this._commitEdited(parentId, type, config, errors))
    }
    await Promise.all(requests)
    if (Object.keys(errors).length) {
      throw { responseJSON: { errors } }
    }
  }

  _commitDeletes(parentId, type, config, errors) {
    if (!config.persistDelete) return Promise.resolve()
    const deleted = this._getSet(this._deleted, type)
    const requests = []
    for (const id of deleted) {
      const request = Promise.resolve(config.persistDelete(parentId, id)).then(
        () => deleted.delete(id),
        err => {
          errors[id] = errorMessage(err)
        },
      )
      requests.push(request)
    }
    return Promise.all(requests)
  }

  _commitCreated(parentId, type, config, errors) {
    if (!config.readDOM || !config.persistCreate) return Promise.resolve()
    const created = this._getSet(this._created, type)
    const drafts = []
    for (const id of created) {
      const draft = config.readDOM(id)
      if (draft) drafts.push(draft)
    }
    if (!drafts.length) return Promise.resolve()
    const assign = ids => {
      for (const [tmp, id] of Object.entries(ids ?? {})) {
        this._assigned.set(tmp, id)
        created.delete(tmp)
      }
    }
    return Promise.resolve(config.persistCreate(parentId, drafts)).then(
      response => assign(response?.ids),
      err => {
        assign(err?.responseJSON?.ids)
        const draftErrors = err?.responseJSON?.errors ?? {}
        for (const draft of drafts) {
          if (created.has(draft.temp_id)) {
            errors[draft.temp_id] = draftErrors[draft.temp_id] ?? errorMessage(err)
          }
        }
      },
    )
  }

  _commitEdited(parentId, type, config, errors) {
    if (!config.readDOM || !config.persistPatch) return Promise.resolve()
    const edited = this._getSet(this._edited, type)
    const requests = []
    for (const id of edited) {
      const entry = config.readDOM(id)
      if (!entry) {
        edited.delete(id)
        continue
      }
      delete entry.temp_id
      const request = Promise.resolve(config.persistPatch(parentId, this.resolveId(id), entry)).then(
        () => edited.delete(id),
        err => {
          errors[id] = errorMessage(err)
        },
      )
      requests.push(request)
    }
    return Promise.all(requests)
  }

  resolveId(id) {
    return this._assigned.get(String(id)) ?? id
  }

  resolveKeys(byId) {
    return Object.fromEntries(Object.entries(byId).map(([id, value]) => [this.resolveId(id), value]))
  }

  reset() {
    this._created.clear()
    this._deleted.clear()
    this._edited.clear()
    this._assigned.clear()
    this._counter = 0
  }

  _getSet(map, type) {
    if (!map.has(type)) map.set(type, new Set())
    return map.get(type)
  }
}
