// Globals
var available_types = ['CONST'];

/**
 * Store the currently active (in the modal) variable.
 * @param variables_datatable
 */
function store_variable(variables_datatable) {
    variable_modal_content = $('.modal-content');
    variable_modal_content.LoadingOverlay('show');

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
            variable_modal_content.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                if (data.rebuild_table) {
                    location.reload();
                } else {
                    variables_datatable.row(associated_row_id).data(data.data).draw();
                    $('#variable_modal').modal('hide');
                }
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
    variables_datatable = variables_table.DataTable({
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
                            search_query = '?command=search&col=1&q=' + name;
                            result += '<span class="badge badge-info">' +
                                '<a href="' + base_url + search_query + '" target="_blank">' + name + '</a>' +
                                '</span></br>';
                        }
                    });
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
            $('#search_bar').val('');
        }
    });
    variables_datatable.column(3).visible(false);

    // Bind big custom searchbar to search the table.
    $('#search_bar').keyup(function(){
      variables_datatable.search($(this).val()).draw() ;
    });

    // Add listener for variable link to modal.
    variables_table.find('tbody').on('click', 'a.modal-opener', function (event) {
        // prevent body to be scrolled to the top.
        event.preventDefault();

        // Get row data
        var data = variables_datatable.row($(event.target).parent()).data();
        var row_id = variables_datatable.row($(event.target).parent()).index();

        // Prepare requirement Modal
        variable_modal_content = $('.modal-content');
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

        variable_modal_content.LoadingOverlay('hide');
    });

    // Store changes on variable on save.
    $('#save_variable_modal').click(function () {
        store_variable(variables_datatable);
    });

    $('#variable_type').on('keyup change autocompleteclose', function () {
        if ($( this ).val() === 'CONST') {
            variable_is_const();
        } else {
            variable_is_const(revert=true);
        }
    });
} );