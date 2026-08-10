import Mustache from "mustache"

export default class TemplateRenderer {
  constructor({ baseUrl = "/static/templates", patternsUrl = "/api/v1/patterns" } = {}) {
    this.baseUrl = baseUrl
    this.patternsUrl = patternsUrl
    this._templates = new Map()
    this._loaded = new Map()
    this._patterns = null
    this.patternData = null
  }

  load(name) {
    if (!this._templates.has(name)) {
      const promise = fetch(`${this.baseUrl}/${name}.mustache`)
        .then(response => {
          if (!response.ok) {
            throw new Error(`Template '${name}' could not be loaded (${response.status}).`)
          }
          return response.text()
        })
        .then(text => {
          this._loaded.set(name, text)
          return text
        })
      this._templates.set(name, promise)
    }
    return this._templates.get(name)
  }

  getTemplate(name) {
    return this._loaded.get(name)
  }

  async render(name, data = {}) {
    const template = await this.load(name)
    return Mustache.render(template, data)
  }

  async patterns() {
    if (!this._patterns) {
      this._patterns = fetch(this.patternsUrl)
        .then(response => {
          if (!response.ok) {
            throw new Error(`Patterns could not be loaded (${response.status}).`)
          }
          return response.json()
        })
        .then(data => {
          this.patternData = {
            ...data,
            groups: Object.entries(data.groups).map(([group, patterns]) => ({ group, patterns })),
          }
          return this.patternData
        })
    }
    return this._patterns
  }

  ready(names = []) {
    const requests = names.map(name => this.load(name))
    requests.push(this.patterns())
    return Promise.all(requests)
  }
}
