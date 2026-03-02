import Mustache from "mustache"

// can be default due to only one instance exisiting each time and data not getting changed
export default class FormalizationRenderer {
  constructor() {
    this.containerTemplate = $("#formalization-container").html()
    this.types = new Map()
  }

  registerType(type, config) {
    this.types.set(type, config)
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

    const containerHtml = Mustache.render(this.containerTemplate, finalEntry)
    const contentTemplate = $(config.templateSelector).html()
    const contentHtml = Mustache.render(contentTemplate, finalEntry)

    const $container = $(containerHtml)

    $container.find(".accordion-collapse").append(contentHtml)

    if (config.afterRender) {
      config.afterRender($container, finalEntry)
    }

    return $container
  }
}
