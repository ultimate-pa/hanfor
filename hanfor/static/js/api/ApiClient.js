export default class ApiClient {
  constructor(base = "/api/v1") {
    this.base = base
    this.onError = null
  }

  _onError(err, method, path) {
    if (this.onError) this.onError(err, method, path)
  }

  get(path) {
    return $.getJSON(this.base + path).fail(e => this._onError(e, "GET", path))
  }

  post(path, data) {
    return $.post(this.base + path, data).fail(e => this._onError(e, "POST", path))
  }

  // TODO: This should be discussed to either opt for form based or json based, then this can be eliminated
  // or the new default
  postJSON(path, data) {
    return $.ajax({
      url: this.base + path,
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(data),
    }).fail(e => this._onError(e, "POST", path))
  }

  patch(path, data) {
    return $.ajax({
      url: this.base + path,
      method: "PATCH",
      data,
    }).fail(e => this._onError(e, "PATCH", path))
  }

  delete(path) {
    return $.ajax({
      url: this.base + path,
      method: "DELETE",
    }).fail(e => this._onError(e, "DELETE", path))
  }

  // Specializied methods to eliminate duplicate code
  getRequirement(rid) { return this.get(`/req/${rid}`) }
  getRequirements() { return this.get(`/req`) }
  getColumnDefs() { return this.get(`/req/colum_defs`) }
  getFormalizations(rid) { return this.get(`/req/${rid}/formalizations`) }
  getTags() { return this.get(`/tags`) }
  getGuesses(rid) { return this.get(`/req/${rid}/guesses`) }

  deleteFormalization(rid, fid) { return this.delete(`/req/${rid}/formalizations/${fid}`) }

  createFormalization(rid, data) {
    return this.post(`/req/${rid}/formalizations/formalization/${data.id}`, {
      id: rid,
      data: JSON.stringify(data),
    })
  }

  createVariable(rid, data) {
    return this.post(`/req/${rid}/formalizations/variable/${data.id}`, {
      id: rid,
      data: JSON.stringify(data),
    })
  }

  addTag(rid, name) { return this.post(`/req/${rid}/tags/${encodeURIComponent(name)}`) }
  removeTag(rid, name) { return this.delete(`/req/${rid}/tags/${encodeURIComponent(name)}`) }
  setStatus(rid, status) { return this.patch(`/req/${rid}`, { status }) }

  patchRequirement(rid, formData) { return this.patch(`/req/${rid}`, formData) }

  highlightDescription(rid, text) {
    return this.postJSON(`/req/${rid}/highlight-description`, { description: text })
  }

  addFormalizationFromGuess(data) { return this.post(`/req/add_formalization_from_guess`, data) }
  addMultiTopGuess(data) { return this.post(`/req/multi_add_top_guess`, data) }
}
