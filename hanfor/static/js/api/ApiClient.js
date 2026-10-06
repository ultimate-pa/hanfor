const url = (strings, ...values) => strings.reduce((out, part, i) => out + encodeURIComponent(values[i - 1]) + part)

export default class ApiClient {
  constructor(base = "/api/v1") {
    this.base = base
    this.onError = null
  }

  request(method, path, { json, form } = {}) {
    const options = { url: this.base + path, method }
    if (json !== undefined) Object.assign(options, { contentType: "application/json", data: JSON.stringify(json) })
    if (form !== undefined) options.data = form
    return $.ajax(options).fail(e => this.onError?.(e, method, path))
  }

  get(path) { return this.request("GET", path) }
  post(path, body) { return this.request("POST", path, body) }
  patch(path, body) { return this.request("PATCH", path, body) }
  put(path, body) { return this.request("PUT", path, body) }
  delete(path) { return this.request("DELETE", path) }

  // Specializied methods to eliminate duplicate code
  getRequirement(rid) { return this.get(url`/req/${rid}`) }
  getRequirements() { return this.get(`/req`) }
  getColumnDefs() { return this.get(`/req/column-defs`) }
  getFormalizations(rid) { return this.get(url`/req/${rid}/formalizations`) }
  getTags() { return this.get(`/tags`) }
  getVariables() { return this.get(`/variables`) }
  createVariable(fields) { return this.post(`/variables`, { json: fields }) }
  deleteVariable(name) { return this.delete(url`/variables/${name}`) }
  getEnumerators(name) { return this.get(url`/variables/${name}/enumerators`) }
  getGuesses(rid) { return this.get(url`/req/${rid}/guesses`) }

  patchFormalization(rid, fid, data) { return this.patch(url`/req/${rid}/formalizations/${fid}`, { form: { data: JSON.stringify(data) } }) }
  deleteFormalization(rid, fid) { return this.delete(url`/req/${rid}/formalizations/${fid}`) }

  createMany(rid, subtype, drafts) {
    return this.post(url`/req/${rid}/formalizations/${subtype}`, { form: { data: JSON.stringify(drafts) } })
  }

  addTag(rid, name) { return this.put(url`/req/${rid}/tags/${name}`) }
  removeTag(rid, name) { return this.delete(url`/req/${rid}/tags/${name}`) }

  patchRequirement(rid, fields) { return this.patch(url`/req/${rid}`, { json: fields }) }

  highlightDescription(rid, text) {
    return this.post(url`/req/${rid}/highlight-description`, { json: { description: text } })
  }

  addMultiTopGuess(data) { return this.post(`/req/multi_add_top_guess`, { form: data }) }
}
