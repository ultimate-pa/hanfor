require('gasparesganga-jquery-loading-overlay');
require('bootstrap');
require('bootstrap-confirmation2');
require('datatables.net-bs4');
require('datatables.net-select');
require('jquery-ui/ui/widgets/autocomplete');
require('./bootstrap-tokenfield.js');

// Globals
let available_types = ['CONST'];
let var_search_string = sessionStorage.getItem('var_search_string');
let type_inference_errors = [];

/**
 * Store the currently active (in the modal) variable.
 * @param variables_table
 */
function store_variable(variables_table) {
    let var_modal_content = $('.modal-content');
    var_modal_content.LoadingOverlay('show');

    // Get data.
    const var_name = $('#variable_name').val();
    const var_name_old = $('#variable_name_old').val();
    const var_type = $('#variable_type').val();
    const var_type_old = $('#variable_type_old').val();
    const associated_row_id = parseInt($('#modal_associated_row_index').val());
    const occurrences = $('#occurences').val();
    const const_val = $('#variable_value').val();
    const const_val_old = $('#variable_value_old').val();
    const updated_constraints = $('#variable_constraint_updated').val();

    // Fetch the constraints
    let constraints = {};
    $('.formalization_card').each(function ( index ) {
        // Scope and Pattern
        let constraint = {};
        constraint['id'] = $(this).attr('title');
        $( this ).find( 'select').each( function () {
            if ($( this ).hasClass('scope_selector')) {
                constraint['scope'] = $( this ).val();
            }
            if ($( this ).hasClass('pattern_selector')) {
                constraint['pattern'] = $( this ).val();
            }
        });

        // Expressions
        constraint['expression_mapping'] = {};
        $( this ).find( "textarea.reqirement-variable" ).each(function () {
            if ($(this).attr('title') !== '')
            constraint['expression_mapping'][$(this).attr('title')] = $(this).val();
        });

        constraints[constraint['id']] = constraint;
    });

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
            occurrences: occurrences,
            constraints: JSON.stringify(constraints),
            updated_constraints: updated_constraints
        },
        // Update var table on success or show an error message.
        function( data ) {
            var_modal_content.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                if (data.rebuild_table) {
                    location.reload();
                } else {
                    variables_table.row(associated_row_id).data(data.data).draw();
                    $('#variable_modal').modal('hide');
                }
            }
    });
}


/**
 * Import variable collection set in the import modal.
 */
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


/**
 * Open modal for the user to trigger variable import.
 * @param sess_name
 * @param sess_revision
 */
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


/**
 * Apply multi edit on selected variables.
 * @param variables_table
 * @param del
 */
function apply_multi_edit(variables_table, del=false) {
    let page = $('body');
    page.LoadingOverlay('show');
    let change_type = $('#multi-change-type-input').val().trim();
    let selected_vars = [];
    variables_table.rows( {selected:true} ).every( function () {
        let d = this.data();
        selected_vars.push(d['name']);
    } );

    // Update selected vars.
    $.post( "api/var/multi_update",
        {
            change_type: change_type,
            selected_vars: JSON.stringify(selected_vars),
            del: del
        },
        // Update requirements table on success or show an error message.
        function( data ) {
            page.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                location.reload();
            }
    });
}


/**
 * Enable/disable the active variables (P, Q, R, ...) in the requirement modal based on scope and pattern.
 */
function update_vars() {
    $('.requirement_var_group').each(function () {
        $( this ).hide();
    });

    $('.formalization_card').each(function ( index ) {
        // Fetch attributes
        const formalization_id = $(this).attr('title');
        const selected_scope = $('#requirement_scope' + formalization_id).val();
        const selected_pattern = $('#requirement_pattern' + formalization_id).val();
        let var_p = $('#requirement_var_group_p' + formalization_id);
        let var_q = $('#requirement_var_group_q' + formalization_id);
        let var_r = $('#requirement_var_group_r' + formalization_id);
        let var_s = $('#requirement_var_group_s' + formalization_id);
        let var_t = $('#requirement_var_group_t' + formalization_id);
        let var_u = $('#requirement_var_group_u' + formalization_id);

        switch(selected_scope) {
            case 'BEFORE':
            case 'AFTER':
                var_p.show();
                break;
            case 'BETWEEN':
            case 'AFTER_UNTIL':
                var_p.show();
                var_q.show();
                break;
            default:
                break;
        }

        switch(selected_pattern) {
            case 'Absence':
            case 'Universality':
            case 'Existence':
            case 'BoundedExistence':
                var_r.show();
                break;
            case 'Invariant':
            case 'Precedence':
            case 'Response':
            case 'MinDuration':
            case 'MaxDuration':
            case 'BoundedRecurrence':
                var_r.show();
                var_s.show();
                break;
            case 'PrecedenceChain1-2':
            case 'PrecedenceChain2-1':
            case 'ResponseChain1-2':
            case 'ResponseChain2-1':
            case 'BoundedResponse':
            case 'BoundedInvariance':
            case 'TimeConstrainedInvariant':
                var_r.show();
                var_s.show();
                var_t.show();
                break;
            case 'ConstrainedChain':
            case 'TimeConstrainedMinDuration':
            case 'ConstrainedTimedExistence':
                var_r.show();
                var_s.show();
                var_t.show();
                var_u.show();
                break;
            case 'NotFormalizable':
                var_p.hide();
                var_q.hide();
                break;
            default:
                break;
        }
    });
}


/**
 * Updates the formalization textarea based on the selected scope and expressions in P, Q, R, S, T.
 */
function update_formalization() {
    $('.formalization_card').each(function ( index ) {
        // Fetch attributes
        const formalization_id = $(this).attr('title');

        let formalization = '';
        const selected_scope = $('#requirement_scope' + formalization_id).find('option:selected').text().replace(/\s\s+/g, ' ');
        const selected_pattern = $('#requirement_pattern' + formalization_id).find('option:selected').text().replace(/\s\s+/g, ' ');

        if (selected_scope !== 'None' && selected_pattern !== 'None') {
            formalization = selected_scope + ', ' + selected_pattern + '.';
        }

        // Update formalization with variables.
        let var_p = $('#formalization_var_p' + formalization_id).val();
        let var_q = $('#formalization_var_q' + formalization_id).val();
        let var_r = $('#formalization_var_r' + formalization_id).val();
        let var_s = $('#formalization_var_s' + formalization_id).val();
        let var_t = $('#formalization_var_t' + formalization_id).val();
        let var_u = $('#formalization_var_u' + formalization_id).val();

        if (var_p.length > 0) {
            formalization = formalization.replace(/{P}/g, var_p);
        }
        if (var_q.length > 0) {
            formalization = formalization.replace(/{Q}/g, var_q);
        }
        if (var_r.length > 0) {
            formalization = formalization.replace(/{R}/g, var_r);
        }
        if (var_s.length > 0) {
            formalization = formalization.replace(/{S}/g, var_s);
        }
        if (var_t.length > 0) {
            formalization = formalization.replace(/{T}/g, var_t);
        }
        if (var_u.length > 0) {
            formalization = formalization.replace(/{U}/g, var_u);
        }

        $('#current_formalization_textarea' + formalization_id).val(formalization);

        // Update visual representation of type inference errors.
        let header = $('#formalization_heading' + formalization_id);
        if (formalization_id in type_inference_errors) {
            for (let i = 0; i < type_inference_errors[formalization_id].length; i++) {
                $('#formalization_var_' + type_inference_errors[formalization_id][i] + formalization_id)
                    .addClass('type-error');
                header.addClass('type-error-head');
            }
        } else {
            header.removeClass('type-error-head');
        }
    });
    $('#variable_constraint_updated').val('true');
}


function delete_constraint(constraint_id) {
    let requirement_modal_content = $('.modal-content');
    requirement_modal_content.LoadingOverlay('show');
    const var_name = $('#variable_name').val();
    $.post( "api/var/del_constraint",
        {
            name: var_name,
            constraint_id: constraint_id
        },
        function( data ) {
            requirement_modal_content.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                $('#formalization_accordion').html(data['html']);
            }
    }).done(function () {
        update_vars();
        update_formalization();
        bind_expression_buttons();
    });
}


function bind_expression_buttons() {
    $('.formalization_selector').change(function () {
        update_vars();
        update_formalization();
    });
    $('.reqirement-variable, .req_var_type').change(function () {
        update_formalization();
    });
    $('.delete_formalization').confirmation({
      rootSelector: '.delete_formalization'
    }).click(function () {
        delete_constraint( $(this).attr('name') );
    });
}


function add_constraint() {
    // Request a new Constraint/Formalization. And add its edit elements to the modal.
    let var_modal_content = $('.modal-content');
    var_modal_content.LoadingOverlay('show');

    // Get data.
    const var_name = $('#variable_name').val();
    const associated_row_id = parseInt($('#modal_associated_row_index').val());

    // Store the variable.
    $.post( "api/var/new_constraint",
        {
            name: var_name
        },
        // Update var table on success or show an error message.
        function( data ) {
            var_modal_content.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                $('#formalization_accordion').html(data['html']);
            }
    }).done(function () {
        update_vars();
        update_formalization();
        bind_expression_buttons();
    });
}


function get_variable_constraints_html(var_name) {
    $.post( "api/var/get_constraints_html",
        {
            name: var_name
        },
        function( data ) {
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                type_inference_errors = data.type_inference_errors;
                $('#formalization_accordion').html(data['html']);
            }
    }).done(function () {
        update_vars();
        update_formalization();
        bind_expression_buttons();
    });
}


function is_constraint_link(name) {
    const regex = /^(Constraint_)(.*)(_[0-9]+$)/gm;
    let result = null;
    let match = regex.exec(name);

    if (match !== null) {
      result = match[2];
    }

    return result
}

/**
 * Find the datatable row index for a variable by its name.
 * @param {number} name the requirement id.
 * @returns {number} row_index the datatables row index.
 */
function get_rowidx_by_var_name(name) {
    let variables_table = $('#variables_table').DataTable();
    let result = -1;
    let filteredData = variables_table
        .column( 1 )
        .data()
        .filter( function ( value, index ) {
            if (value === name) {
                result = index;
                return true;
            }
            return false;
        } );

    return result;
}

function load_variable(row_idx) {
    // Get row data
    let data = $('#variables_table').DataTable().row(row_idx).data();

    // Prepare requirement Modal
    let var_modal_content = $('.modal-content');
    $('#variable_value_form_group').hide();
    $('#variable_modal').modal('show');

    // Meta information
    $('#modal_associated_row_index').val(row_idx);
    $('#variable_name_old').val(data.name);
    $('#variable_type_old').val(data.type);
    $('#occurences').val(data.used_by);

    // Visible information
    $('#variable_modal_title').html('Variable: ' + data.name);
    $('#variable_name').val(data.name);

    let type_input = $('#variable_type');
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

    // Load constraints
    get_variable_constraints_html(data.name);

    var_modal_content.LoadingOverlay('hide');
}

$(document).ready(function() {
    // Prepare and load the variables table.
    let variables_table = $('#variables_table').DataTable({
        "paging": true,
        "stateSave": true,
        "select": {
            style:    'os',
            selector: 'td:first-child'
        },
        "pageLength": 50,
        "responsive": true,
        "lengthMenu": [[10, 50, 100, 500, -1], [10, 50, 100, 500, "All"]],
        "dom": 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        "ajax": "api/var/gets",
        "deferRender": true,
        "columns": [
            {
                "orderable": false,
                "className": 'select-checkbox',
                "targets": [0],
                "data": null,
                "defaultContent": ""
            },
            {
                "data": "name",
                "targets": [1],
                "render": function ( data, type, row, meta ) {
                    result = '<a class="modal-opener" href="#">' + data + '</span></br>';
                    return result;
                }
            },
            {
                "data": "type",
                "targets": [2],
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
                "targets": [3],
                "render": function ( data, type, row, meta ) {
                    let result = '';
                    if ($.inArray('Type_inference_error', row.tags) > -1) {
                        result += '<span class="badge badge-danger">' +
                                    '<a href="#" class="variable_link" ' +
                                    'data-name="' + row.name + '" >Has type inference error</a>' +
                                    '</span> ';
                    }
                    $(data).each(function (id, name) {
                        if (name.length > 0) {
                            let constraint_parent = is_constraint_link(name);
                            if (constraint_parent !== null) {
                                result += '<span class="badge badge-success">' +
                                    '<a href="#" class="variable_link" ' +
                                    'data-name="' + constraint_parent + '" >' + name + '</a>' +
                                    '</span> ';
                            } else {
                                let search_query = '?command=search&col=2&q=' + name;
                                result += '<span class="badge badge-info">' +
                                '<a href="./' + search_query + '" target="_blank">' + name + '</a>' +
                                '</span> ';
                            }
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
                "targets": [4],
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
            $('.variable_link').click(function (event) {
                event.preventDefault();
                load_variable(get_rowidx_by_var_name($(this).data('name')));
            });
        }
    });
    variables_table.column(3).visible(true);
    variables_table.column(4).visible(false);

    // Bind big custom searchbar to search the table.
    $('#search_bar').keyup(function(){
      variables_table.search($(this).val()).draw();
      sessionStorage.setItem('var_search_string', $(this).val());
    });

    // Add listener for variable link to modal.
    $('#variables_table').find('tbody').on('click', 'a.modal-opener', function (event) {
        // prevent body to be scrolled to the top.
        event.preventDefault();
        let row_idx = variables_table.row($(event.target).parent()).index();
        load_variable(row_idx);
    });

    // Store changes on variable on save.
    $('#save_variable_modal').click(function () {
        store_variable(variables_table);
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

    // Multiselect.
    // Select single rows
    $('.select-all-button').on('click', function (e) {
        // Toggle selection on
        if ($( this ).hasClass('btn-secondary')) {
            variables_table.rows( {page:'current'} ).select();
        }
        else { // Toggle selection off
            variables_table.rows( {page:'current'} ).deselect();
        }
        // Toggle button state.
        $('.select-all-button').toggleClass('btn-secondary btn-primary');
    });

    // Toggle "Select all rows to `off` on user specific selection."
    variables_table.on( 'user-select', function ( ) {
        let select_buttons = $('.select-all-button');
        select_buttons.removeClass('btn-primary');
        select_buttons.addClass('btn-secondary ');
    });

    // Bind autocomplete for "edit-selected" types
    $('#multi-change-type-input').autocomplete({
        minLength: 0,
        source: available_types,
        delay: 100
    }).on('focus', function() { $(this).keydown(); }).val('');

    $('.apply-multi-edit').click(function () {
        apply_multi_edit(variables_table);
    });

    // Multi Delete variables.
    $('.delete_button').confirmation({
        rootSelector: '.delete_button'
    }).click(function () {
        apply_multi_edit(variables_table, del=true);
    });

    // Add new Constraint
    $('#add_constraint').click(function () {
        add_constraint();
    });
} );
