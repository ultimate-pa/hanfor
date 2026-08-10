import Mustache from "mustache"
import TemplateRenderer from "../template/TemplateRenderer.js"

export default class FormalizationRenderer {
  constructor() {
    this.templates = new TemplateRenderer({ baseUrl: "/static/templates/formalizations" })
    this.types = new Map()
    this._ready = null
  }

  registerType(type, config) {
    this.types.set(type, config)
  }

  ready() {
    if (!this._ready) {
      const names = new Set(["container"])
      this.types.forEach(config => {
        if (config.template) names.add(config.template)
      })
      names.add("enumerator")
      this._ready = this.templates.ready([...names])
    }
    return this._ready
  }

  build(type, entry) {
    const config = this.types.get(type)

    if (!config) {
      throw new Error(`Unknown formalization type of ${type}, supply the config defaults`)
    }

    const finalEntry = {
      ...(config.defaults || {}),
      ...entry,
    }

    const containerTemplate = this.templates.getTemplate("container")
    const contentTemplate = this.templates.getTemplate(config.template)
    if (!containerTemplate || !contentTemplate) {
      throw new Error(`Templates for type '${type}' are not loaded yet. Await renderer.ready() before building.`)
    }

    if (config.withPatterns && this.templates.patternData) {
      finalEntry.groups = this.templates.patternData.groups
      finalEntry.scopes = this.templates.patternData.scopes
    }

    const containerHtml = Mustache.render(containerTemplate, finalEntry)
    const contentHtml = Mustache.render(contentTemplate, finalEntry)

    const $container = $(containerHtml)

    $container.find(".accordion-collapse").append(contentHtml)

    if (config.afterRender) {
      config.afterRender($container, finalEntry)
    }

    return $container
  }
}
