require('gasparesganga-jquery-loading-overlay');
require('bootstrap');
require('bootstrap-confirmation2');
require('datatables.net-bs4');
require('datatables.net-select');
require('jquery-ui/ui/widgets/autocomplete');
require('./bootstrap-tokenfield.js');

let var_search_string = sessionStorage.getItem('var_search_string');

function set_var_view_modal_data(data) {

}

function load_var_view_modal(data, collection) {
    let var_view_modal = $('#variable_view_modal');
    $('#variable_view_modal_title').html('Name: <code>' + data.name + '</code>');
    let var_object;
    if (collection === 'source_link') {
        var_object = data.source;
    } else if (collection === 'target_link') {
        var_object = data.target;
    }
    let body_html = '<h5>Type</h5><code>' + var_object.type + '</code>';
    if (var_object.type === 'CONST') {
        body_html += '<h5>Const value</h5><code>' + var_object.const_val + '</code>'
    }
    $('#var_view_modal_body').html(body_html);
    var_view_modal.modal('show');
}

function modify_row_by_action(row, action, redraw = true) {
    let data = row.data();
    if (action === 'source') {
        if (typeof(data.source.name) !== 'undefined') {
            data.result = data.source;
            data.action = 'source';
        }
    } else if (action === 'target') {
        if (typeof(data.target.name) !== 'undefined') {
            data.result = data.target;
            data.action = 'target';
        }
    } else if (action === 'skip') {
        data.result = data.target;
        data.action =  (typeof(data.target.name) !== 'undefined' ? 'target' : 'skipped');
    }
    if (redraw) {
        row.data(data).draw('full-hold');
    }
}

function get_selected_vars(variables_table) {
    let selected_vars = [];
    variables_table.rows( {selected:true} ).every( function () {
        let d = this.data();
        selected_vars.push(d['name']);
    });
    return selected_vars;
}

function apply_multiselect_action(var_import_table, action) {
    var_import_table.rows( {selected:true} ).every( function () {
        modify_row_by_action(this, action);
    });
}

function store_changes(var_import_table) {
    // Fetch relevant changes
    let data = Object();
    var_import_table.rows( ).every( function () {
        let row = this.data();
        data[row.name] = {
            action: row.action,
            result: row.result
        };
    });
    data = JSON.stringify(data);

    // Send changes to backend.
    $.post( "api/" + session_id + "/store_table",
        {
            rows: data
        },
        // Update requirements table on success or show an error message.
        function( data ) {
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                location.reload();
            }
    });
}

function apply_tools_action(var_import_table, action) {
    if (action === 'store-changes') {
        store_changes(var_import_table);
    }
}

$(document).ready(function() {
    // Prepare and load the variables table.
    let var_import_table = $('#var_import_table').DataTable({
        "paging": true,
        "stateSave": true,
        "select": {
            style:    'os',
            selector: 'td:first-child'
        },
        "pageLength": 200,
        "responsive": true,
        "lengthMenu": [[10, 50, 100, 500, -1], [10, 50, 100, 500, "All"]],
        "dom": 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        "ajax": "api/" + session_id + "/get_table_data",
        "deferRender": true,
        "columns": [
            {
                // The mass selection column.
                "orderable": false,
                "className": 'select-checkbox',
                "targets": [0],
                "data": null,
                "defaultContent": ""
            },
            {
                // The actions column.
                "data": function ( row, type, val, meta ) {
                    return row;
                },
                "targets": [1],
                "orderable": false,
                "render": function ( data, type, row, meta ) {
                    let result = '<div class="btn-group" role="group" aria-label="Basic example">'
                        + '<button type="button" data-action="skip" class="skip-btn btn btn-secondary'
                        + (data.action === 'skipped' ? ' active' : '') + '">Skip</button>'
                        + '<button type="button" data-action="source" class="source-btn btn btn-secondary'
                        + (data.action === 'source' ? ' active' : '') + '">Source</button>'
                        + '<button type="button" data-action="target" class="target-btn btn btn-secondary'
                        + (data.action === 'target' ? ' active' : '') + '">Target</button>'
                        + '<button type="button" data-action="custom" class="custom-btn btn btn-secondary'
                        + (data.action === 'custom' ? ' active' : '') + '">Custom</button>'
                        + '</div>';
                    return result;
                }
            },
            {
                // The attributes column.
                "data": function ( row, type, val, meta ) {
                    return row;
                },
                "targets": [1],
                "render": function ( data, type, row, meta ) {
                    let result = ``;
                    if (typeof(data.source.name) !== 'undefined' && typeof(data.target.name) !== 'undefined') {
                        result += '<span class="badge badge-info">match_in_source_and_target</span>'
                        if (data.source.type !== data.target.type) {
                            result += '<span class="badge badge-info">unmatched_types</span>'
                        } else {
                            result += '<span class="badge badge-info">same_types</span>'
                        }
                    } else if (typeof(data.source.type) === 'undefined') {
                        result += '<span class="badge badge-info">no_match_in_source</span>'
                    } else if (typeof(data.target.name) === 'undefined') {
                        result += '<span class="badge badge-info">no_match_in_target</span>'
                    }
                    return result;
                }
            },
            {
                // The source column.
                "data": function ( row, type, val, meta ) {
                    return row.source;
                },
                "targets": [3],
                "render": function ( data, type, row, meta ) {
                    let result = '';
                    if (typeof(data.name) !== 'undefined') {
                        result = '<p class="source_link" style="cursor: pointer"><code>' +
                            data.name + '</code><span class="badge badge-info">' + data.type + '</span></p>';
                    } else {
                        result = 'No match.'
                    }
                    return result;
                }
            },
            {
                // The target column.
                "data": function ( row, type, val, meta ) {
                    return row.target;
                },
                "targets": [4],
                "order": 'asc',
                "render": function ( data, type, row, meta ) {
                    let result = '';
                    if (typeof(data.name) !== 'undefined') {
                        result = '<p class="target_link" style="cursor: pointer"><code>' +
                            data.name + '</code><span class="badge badge-info">' + data.type + '</span>';
                    } else {
                        result = 'No match.'
                    }
                    return result;
                }

            },
            {
                // The result column.
                "data": function ( row, type, val, meta ) {
                    return row.result;
                },
                "targets": [5],
                "render": function ( data, type, row, meta ) {
                    let result = '';
                    if (typeof(data.name) !== 'undefined') {
                        result = '<p class="result_link" style="cursor: pointer"><code>' +
                            data.name + '</code><span class="badge badge-info">' + data.type + '</span>';
                    } else {
                        result = 'Skipped.'
                    }
                    return result;
                }
            }
        ],
        initComplete : function() {
            $('#search_bar').val(var_search_string);
        }
    });

    // Bind big custom searchbar to search the table.
    $('#search_bar').keyup(function(){
      var_import_table.search($(this).val()).draw();
      sessionStorage.setItem('var_search_string', $(this).val());
    });


    let var_import_table_body = $('#var_import_table tbody');

    // Add listener for variable link to modal.
    var_import_table_body.on('click', '.source_link, .target_link', function (event) {
        // prevent body to be scrolled to the top.
        event.preventDefault();
        let data = var_import_table.row( $(this).parents('tr') ).data();
        load_var_view_modal(data, $(this)[0].className);
    });

    // Add listener for table row action buttons.
    var_import_table_body.on('click', '.target-btn, .source-btn, .skip-btn', function (event) {
        // prevent body to be scrolled to the top.
        event.preventDefault();
        let row = var_import_table.row( $(this).parents('tr') );
        console.log(row.data());
        let action = $(this).attr('data-action');
        modify_row_by_action(row, action);
    });

    // Multiselect. Select single rows.
    $('.select-all-button').on('click', function (e) {
        // Toggle selection on
        if ($( this ).hasClass('btn-secondary')) {
            var_import_table.rows( {page:'current'} ).select();
        }
        else { // Toggle selection off
            var_import_table.rows( {page:'current'} ).deselect();
        }
        // Toggle button state.
        $('.select-all-button').toggleClass('btn-secondary btn-primary');
    });

    // Multiselect action buttons
    $('.action-btn').click(function (e) {
        apply_multiselect_action(var_import_table, $(this).attr('data-action'));
    });

    // Tools Buttons
    $('.tools-btn').click(function (e) {
        let action = $(this).attr('data-action');
        apply_tools_action(var_import_table, action);
    });

    // Toggle "Select all rows to `off` on user specific selection."
    var_import_table.on( 'user-select', function ( ) {
        let select_buttons = $('.select-all-button');
        select_buttons.removeClass('btn-primary');
        select_buttons.addClass('btn-secondary ');
    });

} );