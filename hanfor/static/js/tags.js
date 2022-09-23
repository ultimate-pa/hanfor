require('gasparesganga-jquery-loading-overlay');
require('bootstrap');
require('datatables.net-bs5');
require('jquery-ui/ui/widgets/autocomplete');
require('jquery-ui/ui/effects/effect-highlight');
require('./bootstrap-tokenfield.js');
require('awesomplete');
require('awesomplete/awesomplete.css');
require('datatables.net-colreorder-bs5');
require('./bootstrap-confirm-button');

const autosize = require('autosize/dist/autosize');
const {SearchNode} = require('./datatables-advanced-search.js');
const {Modal} = require("bootstrap");
let tag_search_string = sessionStorage.getItem('tag_search_string');
let search_autocomplete = [":AND:", ":OR:", ":NOT:", ":COL_INDEX_00:", ":COL_INDEX_01:", ":COL_INDEX_02:",];

$(document).ready(function () {
    // Prepare and load the tags table.
    let tagsTable = $('#tags-table');
    let tagsDataTable = tagsTable.DataTable({
        "paging": true,
        "stateSave": true,
        "pageLength": 50,
        "responsive": true,
        "lengthMenu": [[10, 50, 100, 500, -1], [10, 50, 100, 500, "All"]],
        "dom": 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        "ajax": "api/tag/gets",
        "deferRender": true,
        "columns": [{
            "data": "name",
            "render": function (data, type, row, meta) {
                result = '<a class="modal-opener" href="#">' + data + '</span></br>';
                return result;
            }
        }, {
            "data": "description",
            "render": function (data, type, row, meta) {
                result = '<div class="white-space-pre">' + data + '</div>';
                return result;
            }

        }, {
            "data": "used_by",
            "render": function (data, type, row, meta) {
                let result = '';
                $(data).each(function (id, name) {
                    if (name.length > 0) {
                        search_query = '?command=search&col=2&q=%5C%22' + name + '%5C%22';
                        result += '<span class="badge bg-info">' + '<a href="' + base_url + search_query + '" target="_blank" class="link-light">' + name + '</a>' + '</span> ';
                    }
                });
                if (data.length > 1 && result.length > 0) {
                    const search_all = '?command=search&col=5&q=%5C%22' + row.name + '%5C%22';
                    result += '<span class="badge bg-info" >' + '<a href="./' + search_all + '" target="_blank" class="link-light">Show all</a>' + '</span> ';
                }
                return result;
            }
        }, {
            "data": "internal",
            "render": function (data, type, row, meta) {
                result = '<input class="form-check-input internal-checkbox" type="checkbox" ' + (data ? 'checked' : '') + '>'
                return result;
            }
        }, {
            "data": "used_by", "visible": false, "searchable": false, "render": function (data, type, row, meta) {
                result = '';
                $(data).each(function (id, name) {
                    if (name.length > 0) {
                        if (result.length > 1) {
                            result += ', '
                        }
                        result += name;
                    }
                });
                return result;
            }
        },],
        initComplete: function () {
            $('#search_bar').val(tag_search_string);
            update_search();

            // Enable Hanfor specific table filtering.
            $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
                // data contains the row. data[0] is the content of the first column in the actual row.
                // Return true to include the row into the data. false to exclude.
                return evaluate_search(data);
            });
            this.api().draw();
        }
    });
    tagsDataTable.column(4).visible(false);
    new $.fn.dataTable.ColReorder(tagsDataTable, {});

    let search_bar = $("#search_bar");
    // Bind big custom searchbar to search the table.
    search_bar.keypress(function (e) {
        if (e.which === 13) { // Search on enter.
            update_search();
            tagsDataTable.draw();
        }
    });

    new Awesomplete(search_bar[0], {
        filter: function (text, input) {
            let result = false;
            // If we have an uneven number of ":"
            // We check if we have a match in the input tail starting from the last ":"
            if ((input.split(":").length - 1) % 2 === 1) {
                result = Awesomplete.FILTER_CONTAINS(text, input.match(/[^:]*$/)[0]);
            }
            return result;
        }, item: function (text, input) {
            // Match inside ":" enclosed item.
            return Awesomplete.ITEM(text, input.match(/(:)([\S]*$)/)[2]);
        }, replace: function (text) {
            // Cut of the tail starting from the last ":" and replace by item text.
            const before = this.input.value.match(/(.*)(:(?!.*:).*$)/)[1];
            this.input.value = before + text;
        }, list: search_autocomplete, minChars: 1, autoFirst: true
    });

    // Add listener for tag link to modal.
    tagsTable.find('tbody').on('click', 'a.modal-opener', function (event) {
        // prevent body to be scrolled to the top.
        event.preventDefault();

        // Get row data
        let data = tagsDataTable.row($(event.target).parent()).data();
        let row_id = tagsDataTable.row($(event.target).parent()).index();

        // Prepare tag modal
        let tag_modal_content = $('.modal-content');
        //$('#tag_modal').modal('show');
        Modal.getOrCreateInstance($('#tag_modal')).show();
        $('#modal_associated_row_index').val(row_id);

        // Meta information
        $('#tag_name_old').val(data.name);
        $('#occurences').val(data.used_by);

        // Visible information
        $('#tag_modal_title').html('Tag: ' + data.name);
        $('#tag_name').val(data.name);
        $('#tag_color').val(data.color);
        $('#tag-description').val(data.description);
        $('#tag_internal').prop("checked", data.internal);

        tag_modal_content.LoadingOverlay('hide');
    });

    // Store changes on tag on save.
    $('#save_tag_modal').click(function () {
        store_tag(tagsDataTable);
    });

    tagsDataTable.on('click', '.internal-checkbox', function (event) {
        event.preventDefault()

        let checkbox = event.currentTarget
        let data = tagsDataTable.row(checkbox.parentNode).data()

        $.ajax({
            type: 'POST',
            url: 'api/tag/update',
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

    // $('.delete_tag').confirmation({
    //     rootSelector: '.delete_tag'
    // }).click(function () {
    //     delete_tag($(this).attr('name'));
    // });

    $('.delete_tag').bootstrapConfirmButton({
        onConfirm: function () {
            delete_tag($(this).attr('name'))
        }
    })

    autosize($('#tag-description'));

    $('#tag_modal').on('shown.bs.modal', function (e) {
        autosize.update($('#tag-description'));
    });

    $('.clear-all-filters').click(function () {
        $('#search_bar').val('').effect("highlight", {color: 'green'}, 500);
        update_search();
        tagsDataTable.draw();
    });

    $('#add-standard-tags').click(function () {
        $.post("api/tag/add_standard",
            {},
            function (data) {
            location.reload();
                })
    });
});

/**
 * Update the search expression tree.
 */
function update_search() {
    tag_search_string = $('#search_bar').val().trim();
    sessionStorage.setItem('tag_search_string', tag_search_string);
    search_tree = SearchNode.fromQuery(tag_search_string);
}


function evaluate_search(data) {
    return search_tree.evaluate(data, [true, true, true]);
}


/**
 * Store the currently active (in the modal) tag.
 * @param tagsDataTable
 */
function store_tag(tagsDataTable) {
    let tag_modal_content = $('.modal-content');
    tag_modal_content.LoadingOverlay('show');

    // Get data.
    let tag_name = $('#tag_name').val();
    let tag_name_old = $('#tag_name_old').val();
    let occurences = $('#occurences').val();
    let tag_color = $('#tag_color').val();
    let associated_row_id = parseInt($('#modal_associated_row_index').val());
    let tag_description = $('#tag-description').val();
    let tag_internal = $('#tag_internal').prop("checked");

    // Store the tag.
    $.post("api/tag/update", {
            name: tag_name,
            name_old: tag_name_old,
            occurences: occurences,
            color: tag_color,
            description: tag_description,
            internal: tag_internal
        }, // Update tag table on success or show an error message.
        function (data) {
            tag_modal_content.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                if (data.rebuild_table) {
                    location.reload();
                } else {
                    tagsDataTable.row(associated_row_id).data(data.data).draw();
                    $('#tag_modal').modal('hide');
                }
            }
        });
}

function delete_tag(name) {
    let tag_modal_content = $('.modal-content');
    tag_modal_content.LoadingOverlay('show');

    let tag_name = $('#tag_name').val();
    let occurences = $('#occurences').val();
    $.ajax({
        type: "DELETE",
        url: "api/tag/del_tag",
        data: {name: tag_name, occurences: occurences},
        success: function (data) {
            tag_modal_content.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                if (data.rebuild_table) {
                    location.reload();
                } else {
                    tagsDataTable.row(associated_row_id).data(data.data).draw();
                    //$('#tag_modal').modal('hide');
                    Modal.getOrCreateInstance(document.getElementById('tag_modal')).hide();
                }
            }
        }
    });
}