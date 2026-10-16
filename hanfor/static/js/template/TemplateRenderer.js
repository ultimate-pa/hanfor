import Mustache from "mustache"

export default class TemplateRenderer {
  constructor({ baseUrl = "/static/templates", patternsUrl = "/api/v1/patterns" } = {}) {
    this.baseUrl = baseUrl
    this.patternsUrl = patternsUrl
    this._templates = new Map()
    this._loaded = new Map()
    this._patterns = null
    this.patternData = null
    this._types = new Map()
    this._ready = null
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

  registerType(type, config) {
    this._types.set(type, config)
  }

  ready() {
    if (!this._ready) {
      const names = new Set()
      this._types.forEach(config => {
        if (config.template) names.add(config.template)
        if (config.container) names.add(config.container)
        ;(config.requires || []).forEach(name => names.add(name))
      })
      this._ready = Promise.all([...names].map(name => this.load(name)), this.patterns())
    }
    return this._ready
  }

  build(type, entry) {
    const config = this._types.get(type)

    if (!config) {
      throw new Error(`Unknown type '${type}'. Register it via registerType().`)
    }

    const finalEntry = {
      ...(config.defaults || {}),
      ...entry,
    }

    if (config.withPatterns && this.patternData) {
      finalEntry.groups = this.patternData.groups
      finalEntry.scopes = this.patternData.scopes
    }

    let $el
    if (config.container) {
      const containerTemplate = this.getTemplate(config.container)
      const contentTemplate = this.getTemplate(config.template)
      if (!containerTemplate || !contentTemplate) {
        throw new Error(`Templates for type '${type}' are not loaded yet. Await renderer.ready() first.`)
      }
      $el = $(Mustache.render(containerTemplate, finalEntry))
      $el.find(config.contentSelector).append(Mustache.render(contentTemplate, finalEntry))
    } else {
      const template = this.getTemplate(config.template)
      if (!template) {
        throw new Error(`Template '${config.template}' is not loaded yet. Await renderer.ready() first.`)
      }
      $el = $(Mustache.render(template, finalEntry))
    }

    if (config.afterRender) {
      config.afterRender($el, finalEntry)
    }

    return $el
  }
}
