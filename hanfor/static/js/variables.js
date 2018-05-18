require('gasparesganga-jquery-loading-overlay');
require('bootstrap');
require('bootstrap-confirmation2');
require('datatables.net-bs4');
require('jquery-ui/ui/widgets/autocomplete');
require('./bootstrap-tokenfield.js');

let var_search_string = sessionStorage.getItem('var_search_string');

// Globals
var available_types = ['CONST'];

/**
 * Store the currently active (in the modal) variable.
 * @param variables_datatable
 */
function store_variable(variables_datatable) {
    tag_modal_content = $('.modal-content');
    tag_modal_content.LoadingOverlay('show');

    // Get data.
    var_name = $('#variable_name').val();
    var_name_old = $('#variable_name_old').val();
    var_type = $('#variable_type').val();
    var_type_old = $('#variable_type_old').val();
    associated_row_id = parseInt($('#modal_associated_row_index').val());
    occurences = $('#occurences').val();
    const_val = $('#variable_value').val();
    const_val_old = $('#variable_value_old').val();

    // Update available types.
    if (var_type !== null && available_types.indexOf(var_type) <= -1) {
        available_types.push(var_type);
    }

    // Store the variable.
    $.post( "api/var/update",
        {
            name: var_name,
            name_old: var_name_old,
            type: var_type,
            const_val: const_val,
            const_val_old: const_val_old,
            type_old: var_type_old,
            occurences: occurences
        },
        // Update var table on success or show an error message.
        function( data ) {
            tag_modal_content.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                if (data.rebuild_table) {
                    location.reload();
                } else {
                    tags_datatable.row(associated_row_id).data(data.data).draw();
                    $('#variable_modal').modal('hide');
                }
            }
    });
}


function import_variables() {
    let variable_import_modal = $('#variable_import_modal');
    let sess_name = $('#variable_import_sess_name').val();
    let sess_revision = $('#variable_import_sess_revision').val();
    let import_option = $('#import_option').val();

    variable_import_modal.LoadingOverlay('show');

    $.post( "api/var/var_import_collection",
        {
            sess_name: sess_name,
            sess_revision: sess_revision,
            import_option: import_option
        },
        function( data ) {
            variable_import_modal.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                variable_import_modal.modal('hide');
                location.reload();
            }
    });
}


function open_import_modal(sess_name, sess_revision) {
    // Prepare requirement Modal
    let variable_import_modal = $('#variable_import_modal');
    $('#variable_import_sess_name').val(sess_name);
    $('#variable_import_sess_revision').val(sess_revision);
    $('#variable_import_modal_title').html('Import from Session: ' + sess_name + ' at: ' + sess_revision);

    variable_import_modal.modal('show');

    // Load informations about selected var collection
    variable_import_modal.LoadingOverlay('show');
    $.post( "api/var/var_import_info",
        {
            sess_name: sess_name,
            sess_revision: sess_revision
        },
        function( data ) {
            variable_import_modal.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                $('#import_tot_number').html('Total:\t' + data['tot_vars'] + ' Variables.');
                $('#import_new_number').html('New:\t' + data['new_vars'] + ' Variables.');
            }
    });
}

/**
 * Show / Hide Value input for variables.
 * @param revert
 */
function variable_is_const(revert) {
    if (revert === true) {
        $('#variable_value_form_group').hide();
    } else {
        $('#variable_value_form_group').show();
    }
}

$(document).ready(function() {
    // Prepare and load the variables table.
    variables_table = $('#variables_table');
    tags_datatable = variables_table.DataTable({
        "paging": true,
        "stateSave": true,
        "pageLength": 50,
        "responsive": true,
        "lengthMenu": [[10, 50, 100, 500, -1], [10, 50, 100, 500, "All"]],
        "dom": 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        "ajax": "api/var/gets",
        "deferRender": true,
        "columns": [
            {
                "data": "name",
                "render": function ( data, type, row, meta ) {
                    result = '<a class="modal-opener" href="#">' + data + '</span></br>';
                    return result;
                }
            },
            {
                "data": "type",
                "render": function ( data, type, row, meta ) {
                    if (data !== null && available_types.indexOf(data) <= -1) {
                        available_types.push(data);
                    }
                    if (data !== null && data === 'CONST') {
                        data = data + ' (' + row['const_val'] + ')';
                    }
                    return data;
                }
            },
            {
                "data": "used_by",
                "render": function ( data, type, row, meta ) {
                    result = '';
                    $(data).each(function (id, name) {
                        if (name.length > 0) {
                            search_query = '?command=search&col=2&q=' + name;
                            result += '<span class="badge badge-info">' +
                                '<a href="' + base_url + search_query + '" target="_blank">' + name + '</a>' +
                                '</span>';
                        }
                    });
                    if (result.length < 1) {
                        result += '<span class="badge badge-warning">' +
                            '<a href="#">Not used</a>' +
                            '</span></br>';
                    }
                    return result;
                }

            },
            {
                "data": "used_by",
                "visible": false,
                "searchable": false,
                "render": function ( data, type, row, meta ) {
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
            }
        ],
        initComplete : function() {
            $('#search_bar').val(var_search_string);
        }
    });
    tags_datatable.column(3).visible(false);

    // Bind big custom searchbar to search the table.
    $('#search_bar').keyup(function(){
      tags_datatable.search($(this).val()).draw();
      sessionStorage.setItem('var_search_string', $(this).val());
    });

    // Add listener for variable link to modal.
    variables_table.find('tbody').on('click', 'a.modal-opener', function (event) {
        // prevent body to be scrolled to the top.
        event.preventDefault();

        // Get row data
        var data = tags_datatable.row($(event.target).parent()).data();
        var row_id = tags_datatable.row($(event.target).parent()).index();

        // Prepare requirement Modal
        tag_modal_content = $('.modal-content');
        $('#variable_value_form_group').hide();
        $('#variable_modal').modal('show');

        // Meta information
        $('#modal_associated_row_index').val(row_id);
        $('#variable_name_old').val(data.name);
        $('#variable_type_old').val(data.type);
        $('#occurences').val(data.used_by);

        // Visible information
        $('#variable_modal_title').html('Variable: ' + data.name);
        $('#variable_name').val(data.name);
        type_input = $('#variable_type');
        type_input.val(data.type);
        if (data.type === 'CONST') {
            variable_is_const();
            $('#variable_value').val(data.const_val);
            $('#variable_value_old').val(data.const_val);

        } else {
            $('#variable_value').val('');
            $('#variable_value_old').val('');
        }

        type_input.autocomplete({
            minLength: 0,
            source: available_types
        }).on('focus', function() { $(this).keydown(); });

        tag_modal_content.LoadingOverlay('hide');
    });

    // Store changes on variable on save.
    $('#save_variable_modal').click(function () {
        store_variable(tags_datatable);
    });

    $('#variable_type').on('keyup change autocompleteclose', function () {
        if ($( this ).val() === 'CONST') {
            variable_is_const();
        } else {
            variable_is_const(revert=true);
        }
    });

    // Add listener for importing variables from existing sessions/revisions
    $('.import_link').on('click', function () {
        const sess_name = $( this ).attr('data-name');
        const sess_revision = $( this ).attr('data-revision');

        open_import_modal(sess_name, sess_revision);
    });

    $('#save_variable_import_modal').click(function ( e ) {
        import_variables();
    });
} );