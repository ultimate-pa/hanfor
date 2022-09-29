require('gasparesganga-jquery-loading-overlay')
require('bootstrap')
require('datatables.net-bs5')
require('jquery-ui/ui/widgets/autocomplete')
require('jquery-ui/ui/effects/effect-highlight')
require('../../static/js/bootstrap-tokenfield.js')
require('awesomplete')
require('awesomplete/awesomplete.css')
require('datatables.net-colreorder-bs5')
require('../../static/js/bootstrap-confirm-button')

const autosize = require('autosize/dist/autosize')
const {SearchNode} = require('../../static/js/datatables-advanced-search.js')
const {Modal} = require('bootstrap')

const searchAutocomplete = [':AND:', ':OR:', ':NOT:', ':COL_INDEX_00:', ':COL_INDEX_01:', ':COL_INDEX_02:']
const tagsSearchString = sessionStorage.getItem('tagsSearchString')

$(document).ajaxStart(function () {
    $.LoadingOverlay('show')
})

$(document).ajaxStop(function () {
    $.LoadingOverlay('hide')
})

$(document).ready(function () {
    const searchInput = $('#search_bar')

    const tagsTable = $('#tags-table')
    const tagsDataTable = tagsTable.DataTable({
        paging: true,
        stateSave: true,
        pageLength: 50,
        responsive: true,
        lengthMenu: [[10, 50, 100, 500, -1], [10, 50, 100, 500, 'All']],
        dom: 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        ajax: {url: '/api/tags/', dataSrc: ''},
        deferRender: true,
        columns: dataTableColumns,
        initComplete: function () {
            searchInput.val(tagsSearchString)
            update_search(searchInput.val().trim())

            // Enable Hanfor specific table filtering.
            $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
                // data contains the row. data[0] is the content of the first column in the actual row.
                // Return true to include the row into the data. false to exclude.
                return evaluate_search(data)
            })
            this.api().draw()
        }
    })

    new $.fn.dataTable.ColReorder(tagsDataTable, {})

    // Bind big custom searchbar to search the table.
    searchInput.keypress(function (e) {
        if (e.which === 13) { // Search on enter.
            update_search(searchInput.val().trim())
            tagsDataTable.draw()
        }
    })

    new Awesomplete(searchInput[0], {
        filter: function (text, input) {
            let result = false
            // If we have an uneven number of ":"
            // We check if we have a match in the input tail starting from the last ":"
            if ((input.split(':').length - 1) % 2 === 1) {
                result = Awesomplete.FILTER_CONTAINS(text, input.match(/[^:]*$/)[0])
            }
            return result
        }, item: function (text, input) {
            // Match inside ":" enclosed item.
            return Awesomplete.ITEM(text, input.match(/(:)([\S]*$)/)[2])
        }, replace: function (text) {
            // Cut of the tail starting from the last ":" and replace by item text.
            const before = this.input.value.match(/(.*)(:(?!.*:).*$)/)[1]
            this.input.value = before + text
        }, list: searchAutocomplete, minChars: 1, autoFirst: true
    })

    // Add listener for tag link to modal.
    tagsTable.find('tbody').on('click', 'a.modal-opener', function (event) {
        // prevent body to be scrolled to the top.
        event.preventDefault()

        // Get row data
        let data = tagsDataTable.row($(event.target).parent()).data()
        let row_id = tagsDataTable.row($(event.target).parent()).index()

        Modal.getOrCreateInstance($('#tag-modal')).show()
        $('#modal-associated-row-index').val(row_id)

        // Meta information
        $('#tag-name-old').val(data.name)
        $('#occurences').val(data.used_by)

        // Visible information
        $('#tag-modal-title').html('Tag: ' + data.name)
        $('#tag-name').val(data.name)
        $('#tag-color').val(data.color)
        $('#tag-description').val(data.description)
        $('#tag-internal').prop('checked', data.internal)
    })

    // Store changes on tag on save.
    $('#save-tag-modal').click(function () {
        store_tag(tagsDataTable)
    })

    tagsDataTable.on('click', '.internal-checkbox', function (event) {
        event.preventDefault()

        let checkbox = event.currentTarget
        let data = tagsDataTable.row(checkbox.parentNode).data()

        $.ajax({
            type: 'POST',
            url: '/api/tags/update',
            data: {
                name: data.name,
                name_old: data.name,
                occurences: data.used_by,
                color: data.color,
                description: data.description,
                internal: checkbox.checked
            },
            success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                checkbox.checked = response.data.internal
                data.internal = response.data.internal
            }
        })
    })

    $('.delete-tag').bootstrapConfirmButton({
        onConfirm: function () {
            deleteTag()
        }
    })

    autosize($('#tag-description'))

    $('#tag-modal').on('shown.bs.modal', function (e) {
        autosize.update($('#tag-description'))
    })

    $('.clear-all-filters').click(function () {
        searchInput.val('').effect('highlight', {color: 'green'}, 500)
        update_search(searchInput.val().trim())
        tagsDataTable.draw()
    })

    $('#add-standard-tags').click(function () {
        $.ajax({
            type: 'POST', url: '/api/tags/add_standard',
        }).done(function (data) {
            location.reload()
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert(errorThrown + '\n\n' + jqXHR['responseText'])
        })
    })
})

/**
 * Update the search expression tree.
 */
function update_search(string) {
    sessionStorage.setItem('tagsSearchString', string)
    search_tree = SearchNode.fromQuery(string)
}


function evaluate_search(data) {
    return search_tree.evaluate(data, [true, true, true])
}


/**
 * Store the currently active (in the modal) tag.
 * @param tagsDataTable
 */
function store_tag(tagsDataTable) {
    // Get data.
    let name = $('#tag-name-old').val()
    let nameNew = $('#tag-name').val()
    let occurrences = $('#occurences').val().split(',')
    let color = $('#tag-color').val()
    let description = $('#tag-description').val()
    let internal = $('#tag-internal').prop('checked')

    $.ajax({
        type: 'PATCH', url: `/api/tags/${name}`, contentType: 'application/json',
        data: JSON.stringify({
            name_new: nameNew,
            occurrences: occurrences,
            color: color,
            description: description,
            internal: internal
        }),
    }).done(function (data) {
        location.reload()
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(errorThrown + '\n\n' + jqXHR['responseText'])
    })
}

function deleteTag() {
    const tagName = $('#tag-name').val()
    const occurrences = $('#occurences').val().split(',')

    $.ajax({
        type: 'DELETE', url: `/api/tags/${tagName}`, contentType: 'application/json',
        data: JSON.stringify({
            occurrences: occurrences
        }),
    }).done(function (data) {
        location.reload()
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(errorThrown + '\n\n' + jqXHR['responseText'])
    })
}

const dataTableColumns = [
    {
        data: 'name',
        render: function (data, type, row, meta) {
            return `<a class="modal-opener" href="#">${data}</a>`
        }
    }, {
        data: 'description',
        render: function (data, type, row, meta) {
            return `<div class="white-space-pre">${data}</div>`
        }
    }, {
        data: 'used_by',
        render: function (data, type, row, meta) {
            let result = ''
            $(data).each(function (id, name) {
                if (name.length > 0) {
                    const searchQuery = `?command=search&col=2&q=%5C%22${name}%5C%22`
                    result += `<span class="badge bg-info"><a href="/${searchQuery}" target="_blank" class="link-light">${name}</a></span> `
                }
            })
            if (data.length > 1 && result.length > 0) {
                const searchQuery = `?command=search&col=5&q=%5C%22${row.name}%5C%22`
                result += `<span class="badge bg-info"><a href="/${searchQuery}" target="_blank" class="link-light">Show all</a></span> `
            }
            return result
        }
    }, {
        data: 'internal',
        render: function (data, type, row, meta) {
            return `<input class="form-check-input internal-checkbox" type="checkbox" ${data ? 'checked' : ''}>`
        }
    }, {
        data: 'used_by',
        visible: false,
        searchable: false,
        render: function (data, type, row, meta) {
            return data.filter(e => e && e !== '').join(', ')
        }
    }
]