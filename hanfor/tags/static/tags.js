require("gasparesganga-jquery-loading-overlay")
const { Modal } = require("bootstrap")
require("datatables.net-bs5")
require("datatables.net-colreorder-bs5")
require("jquery-ui/ui/widgets/autocomplete")
require("../../static/js/bootstrap-tokenfield.js")
require("jquery-ui/ui/effects/effect-highlight")
require("awesomplete")
require("awesomplete/awesomplete.css")
require("../../static/js/bootstrap-confirm-button")

const autosize = require("autosize/dist/autosize")
const { SearchNode } = require("../../static/js/datatables-advanced-search.js")

const { sendTelemetry } = require("../../telemetry/static/telemetry")

const searchAutocomplete = [":AND:", ":OR:", ":NOT:", ":COL_INDEX_00:", ":COL_INDEX_01:", ":COL_INDEX_02:"]
const tagsSearchString = sessionStorage.getItem("tagsSearchString")
let search_tree = undefined

$(document).ajaxStart(function () {
  $.LoadingOverlay("show")
})

$(document).ajaxStop(function () {
  $.LoadingOverlay("hide")
})

// init page
$(function () {
  initModal()
  initDatatable()
  initSearch()
  initTabs()
})

function initModal() {
  let modal = $("#tag-modal")

  modal[0].addEventListener("shown.bs.modal", function () {
    // resize tag-description text input on modal.show
    autosize.update($("#tag-description"))
  })

  modal[0].addEventListener("hide.bs.modal", function (event) {
    // catch unsaved changes on close
    modalClosingRoutine(event)
  })

  $("#tag-name").on("change", function () {
    $("#tag-modal").data("unsavedChanges", true)
  })

  $("#tag-color").on("change", function () {
    $("#tag-modal").data("unsavedChanges", true)
  })

  $("#tag-internal").on("change", function () {
    $("#tag-modal").data("unsavedChanges", true)
  })

  let tagDescr = $("#tag-description")
  tagDescr.on("change", function () {
    $("#tag-modal").data("unsavedChanges", true)
  })
  autosize(tagDescr)

  $("#save-tag-modal").on("click", function () {
    modalSaveTag()
  })

  $(".delete-tag").bootstrapConfirmButton({
    onConfirm: function () {
      modalDeleteTag()
    },
  })
}

function initDatatable() {
  const tagsTable = $("#tags-table")
  const searchInput = $("#search_bar")

  // noinspection JSCheckFunctionSignatures
  const tagsDataTable = tagsTable.DataTable({
    paging: true,
    stateSave: true,
    pageLength: 50,
    responsive: true,
    lengthMenu: [
      [10, 50, 100, 500, -1],
      [10, 50, 100, 500, "All"],
    ],
    dom: 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
    ajax: {
      url: "api/v1/tags",
      dataSrc: "",
    },
    deferRender: true,
    colReorder: true,
    columns: dataTableColumns,
    initComplete: function () {
      searchInput.val(tagsSearchString)
      updateSearch((searchInput.val() || "").trim())

      // Enable Hanfor specific table filtering.
      $.fn.dataTable.ext.search.push(function (settings, data) {
        // data contains the row. data[0] is the content of the first column in the actual row.
        // Return true to include the row into the data. false to exclude.
        return evaluateSearch(data)
      })
      this.api().draw()
    },
  })

  // Add listener for tag link to modal.
  tagsTable.find("tbody").on("click", "a.modal-opener", function (event) {
    // prevent body to be scrolled to the top.
    event.preventDefault()

    // Get row data
    const data = tagsDataTable.row($(event.target).parent().parent()).data()

    const tagModal = $("#tag-modal")
    Modal.getOrCreateInstance(tagModal[0]).show()

    // Add uuid to modal
    $("#modal-uuid").val(data["uuid"])

    // Visible information
    $("#tag-modal-title").html("Tag: " + data.name)
    let nameInput = $("#tag-name")
    nameInput.val(data.name)
    nameInput.prop("disabled", !data.mutable)
    $("#tag-color").val(data.color)
    $("#tag-description").val(data.description)
    $("#tag-internal").prop("checked", data.internal)
    const deleteBtn = $(".delete-tag")
    deleteBtn.prop("disabled", !data.mutable)
    if (deleteBtn.data("html")) {
      deleteBtn.html(deleteBtn.data("html")).removeData("html")
    }
    tagModal.data("unsavedChanges", false)
    sendTelemetry("tag", data["uuid"], "open")
  })

  // Add listener to the internal checkbox
  tagsDataTable.on("click", ".internal-checkbox", function (event) {
    event.preventDefault()

    const checkbox = event.currentTarget
    const data = tagsDataTable.row(checkbox.parentNode).data()

    $.ajax({
      type: "PATCH",
      contentType: "application/json",
      url: `api/v1/tags/${data["uuid"]}`,
      data: JSON.stringify({
        internal: checkbox.checked,
      }),
    })
      .done(function () {
        tagsDataTable.ajax.reload(null, false)
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        alert(errorThrown + "\n\n" + jqXHR["responseText"])
      })
  })
}

function initSearch() {
  const tagsDataTable = $("#tags-table").DataTable()
  const searchInput = $("#search_bar")

  // Bind big custom searchbar to search the table.
  searchInput.on("keydown", function (e) {
    if (e.which === 13) {
      // Search on enter.
      updateSearch((searchInput.val() || "").trim())
      tagsDataTable.draw()
    }
  })

  new Awesomplete(searchInput[0], {
    filter: function (text, input) {
      let result = false
      // If we have an uneven number of ":"
      // We check if we have a match in the input tail starting from the last ":"
      if ((input.split(":").length - 1) % 2 === 1) {
        result = Awesomplete.FILTER_CONTAINS(text, input.match(/[^:]*$/)[0])
      }
      return result
    },
    item: function (text, input) {
      // Match inside ":" enclosed item.
      return Awesomplete.ITEM(text, input.match(/(:)(\S*$)/)[2])
    },
    replace: function (text) {
      // Cut of the tail starting from the last ":" and replace by item text.
      const before = this.input.value.match(/(.*)(:(?!.*:).*$)/)[1]
      this.input.value = before + text
    },
    list: searchAutocomplete,
    minChars: 1,
    autoFirst: true,
  })

  $(".clear-all-filters").on("click", function () {
    searchInput.val("").effect("highlight", { color: "green" }, 500)
    updateSearch((searchInput.val() || "").trim())
    tagsDataTable.draw()
  })
}

function initTabs() {
  $("#add-standard-tags").on("click", function () {
    $.ajax({
      type: "POST",
      url: "api/v1/tags/add_standard",
    })
      .done(function () {
        location.reload()
      })
      .fail(function (jqXHR, textStatus, errorThrown) {
        alert(errorThrown + "\n\n" + jqXHR["responseText"])
      })
  })
}

function modalClosingRoutine(event) {
  const unsavedChanges = $("#tag-modal").data("unsavedChanges")
  const uuid = $("#modal-uuid").val()
  if (unsavedChanges === true) {
    const forceClose = confirm("You have unsaved changes, do you really want to close?")
    if (forceClose !== true) {
      event.preventDefault()
    } else {
      sendTelemetry("tag", uuid, "close_without_save")
    }
  } else {
    sendTelemetry("tag", uuid, "close")
  }
}

/**
 * Update the search expression tree.
 */
function updateSearch(string) {
  sessionStorage.setItem("tagsSearchString", string)
  search_tree = SearchNode.fromQuery(string)
}

function evaluateSearch(data) {
  return search_tree.evaluate(data, [true, true, true])
}

function modalSaveTag() {
  // Get data.
  let uuid = $("#modal-uuid").val()
  let name = $("#tag-name").val()
  let color = $("#tag-color").val()
  let description = $("#tag-description").val()
  let internal = $("#tag-internal").prop("checked")

  sendTelemetry("tag", uuid, "save")

  $.ajax({
    type: "PUT",
    url: `api/v1/tags/${uuid}`,
    contentType: "application/json",
    data: JSON.stringify({
      name: name,
      color: color,
      description: description,
      internal: internal,
    }),
  })
    .done(function () {
      let modal = $("#tag-modal")
      modal.data("unsavedChanges", false)
      $("#tags-table").DataTable().ajax.reload(null, false)
      Modal.getOrCreateInstance(modal).hide()
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
      alert(errorThrown + "\n\n" + jqXHR["responseText"])
    })
}

function modalDeleteTag() {
  const uuid = $("#modal-uuid").val()
  sendTelemetry("tag", uuid, "delete")

  $.ajax({
    type: "DELETE",
    url: `api/v1/tags/${uuid}`,
  })
    .done(function () {
      let modal = $("#tag-modal")
      modal.data("unsavedChanges", false)
      $("#tags-table").DataTable().ajax.reload(null, false)
      Modal.getOrCreateInstance(modal).hide()
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
      alert(errorThrown + "\n\n" + jqXHR["responseText"])
    })
}

const dataTableColumns = [
  {
    data: "name",
    render: function (data, type, row) {
      return `<a class="modal-opener" href="#"><span class="badge" style="background-color: ${row.color}" >${data}</span></a>`
    },
  },
  {
    data: "description",
    render: function (data) {
      return `<div class="white-space-pre">${data}</div>`
    },
  },
  {
    data: "used_by",
    render: function (data, type, row) {
      let result = ""
      $(data).each(function (id, name) {
        if (name.length > 0) {
          const searchQuery = `?command=search&col=2&q=%5C%22${name}%5C%22`
          result += `<span class="badge bg-info"><a href="${base_url}${searchQuery}" target="_blank" class="link-light">${name}</a></span> `
        }
      })
      if (data.length > 1 && result.length > 0) {
        const searchQuery = `?command=search&col=5&q=%5C%22${row.name}%5C%22`
        result += `<span class="badge bg-info"><a href="${base_url}${searchQuery}" target="_blank" class="link-light">Show all</a></span> `
      }
      return result
    },
  },
  {
    data: "internal",
    render: function (data) {
      return `<input class="form-check-input internal-checkbox" type="checkbox" ${data ? "checked" : ""}>`
    },
  },
  {
    data: "used_by",
    visible: false,
    searchable: false,
    render: function (data) {
      return data.filter((e) => e && e !== "").join(", ")
    },
  },
]
