export default class TrackedStore {
  constructor() {
    this._created = new Map()
    this._deleted = new Map()
    this._types = new Map()
    this._nextId = null
  }

  registerType(type, config) {
    this._types.set(type, config)
  }

  initNextId(nextId) {
    this._nextId = Number(nextId)
  }

  _generateId() {
    return Number(this._nextId++)
  }

  create(type) {
    const id = this._generateId()
    this._getSet(this._created, type).add(id)
    return id
  }

  delete(type, id) {
    id = Number(id)
    if (this._getSet(this._created, type).has(id)) {
      this._getSet(this._created, type).delete(id)
    } else {
      this._getSet(this._deleted, type).add(id)
    }
  }

  isCreated(type, id) {
    return this._getSet(this._created, type).has(Number(id))
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
    const requests = [...this._getSet(this._created, type)].map(id => {
      const data = config.readDOM(id)
      if (!data) {
        console.warn(`TrackedStore: readDOM for ${type}:${id} returned null`)
        return Promise.resolve()
      }
      return config.persistCreate(rid, data)
    })
    this._getSet(this._created, type).clear()
    return Promise.all(requests)
  }

  reset() {
    this._created.clear()
    this._deleted.clear()
    this._nextId = null
  }

  _getSet(map, type) {
    if (!map.has(type)) map.set(type, new Set())
    return map.get(type)
  }
}
