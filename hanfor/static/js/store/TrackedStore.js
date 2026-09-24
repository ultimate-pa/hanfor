export default class TrackedStore {
  constructor() {
    this._created = new Map()
    this._deleted = new Map()
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

  delete(type, id) {
    id = String(id)
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
    if (type) {
      return this._getSet(this._created, type).size === 0 && this._getSet(this._deleted, type).size === 0
    }
    for (const [, set] of this._created) {
      if (set.size > 0) return false
    }
    for (const [, set] of this._deleted) {
      if (set.size > 0) return false
    }
    return true
  }

  commitDeletes(rid, type) {
    const config = this._types.get(type)
    if (!config?.persistDelete) return Promise.resolve()
    const requests = [...this._getSet(this._deleted, type)].map(id => config.persistDelete(rid, id))
    this._getSet(this._deleted, type).clear()
    return Promise.all(requests)
  }

  commitCreated(rid, type) {
    const config = this._types.get(type)
    if (!config?.readDOM || !config?.persistCreate) return Promise.resolve()
    const drafts = [...this._getSet(this._created, type)].map(id => config.readDOM(id)).filter(Boolean)
    this._getSet(this._created, type).clear()
    if (!drafts.length) return Promise.resolve()
    return Promise.resolve(config.persistCreate(rid, drafts)).then(response => {
      for (const [tmp, id] of Object.entries(response?.ids ?? {})) this._assigned.set(tmp, id)
    })
  }

  resolveKeys(byId) {
    return Object.fromEntries(Object.entries(byId).map(([id, value]) => [this._assigned.get(id) ?? id, value]))
  }

  reset() {
    this._created.clear()
    this._deleted.clear()
    this._assigned.clear()
    this._counter = 0
  }

  _getSet(map, type) {
    if (!map.has(type)) map.set(type, new Set())
    return map.get(type)
  }
}
