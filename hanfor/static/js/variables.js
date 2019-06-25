require('gasparesganga-jquery-loading-overlay');
require('bootstrap');
require('bootstrap-confirmation2');
require('datatables.net-bs4');
require('datatables.net-select');
require('jquery-ui/ui/widgets/autocomplete');
require('./bootstrap-tokenfield.js');
require('jquery-ui/ui/effects/effect-highlight');
require('awesomplete');
require('awesomplete/awesomplete.css');

// Globals
let available_types = ['CONST', 'ENUM_INT', 'ENUM_REAL'];
let search_autocomplete = [
    ":AND:",
    ":OR:",
    ":NOT:",
    ":COL_INDEX_01:",
    ":COL_INDEX_02:",
    ":COL_INDEX_03:",
    ":COL_INDEX_04:"
];
let var_search_string = sessionStorage.getItem('var_search_string');
let type_inference_errors = [];
const { SearchNode } = require('./datatables-advanced-search.js');
let search_tree = undefined;
let visible_columns = [true, true, true, true, true];


/**
 * Apply search tree on datatables data.
 * @param data
 * @returns {bool|XPathResult}
 */
function evaluate_search(data){
    return search_tree.evaluate(data, visible_columns);
}

/**
 * Update the search expression tree.
 */
function update_search() {
    var_search_string = $('#search_bar').val().trim();
    sessionStorage.setItem('var_search_string', var_search_string);
    search_tree = SearchNode.fromQuery(var_search_string);
}

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
    const belongs_to_enum = $('#belongs_to_enum').val();
    const belongs_to_enum_old = $('#belongs_to_enum_old').val();

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

    // Process enumerators in case we have an enum
    let enumerators = [];
    if ((var_type === 'ENUM_INT') || (var_type === 'ENUM_REAL')) {
        // Fetch enumerators.
        $('.enumerator-input').each(function (index, elem) {
            let enum_name = $(this).find('.enum_name_input').val();
            let enum_value = $(this).find('.enum_value_input').val();
            enumerators.push([enum_name, enum_value]);
        });
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
            updated_constraints: updated_constraints,
            enumerators: JSON.stringify(enumerators),
            belongs_to_enum: belongs_to_enum,
            belongs_to_enum_old: belongs_to_enum_old
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
 * Start a new import session (redirect to the session on success).
 */
function start_import_session() {
    let variable_import_modal = $('#variable_import_modal');
    let sess_name = $('#variable_import_sess_name').val();
    let sess_revision = $('#variable_import_sess_revision').val();
    let import_option = $('#import_option').val();

    variable_import_modal.LoadingOverlay('show');

    $.post( "api/var/start_import_session",
        {
            sess_name: sess_name,
            sess_revision: sess_revision
        },
        function( data ) {
            variable_import_modal.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                window.location.href = base_url + "variable_import/" + data['session_id'];
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
function update_displayed_constraint_inputs() {
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
            case 'Toggle1':
                var_r.show();
                var_s.show();
                var_t.show();
                break;
            case 'ConstrainedChain':
            case 'TimeConstrainedMinDuration':
            case 'ConstrainedTimedExistence':
            case 'Toggle2':
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
        update_displayed_constraint_inputs();
        update_formalization();
        bind_expression_buttons();
    });
}


function bind_expression_buttons() {
    $('.formalization_selector').change(function () {
        update_displayed_constraint_inputs();
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
        update_displayed_constraint_inputs();
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
        update_displayed_constraint_inputs();
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
    variables_table
        .row( function ( idx, data, node ) {
            if (data.name === name) {
                result = idx;
            }
        });

    return result;
}


/**
 * Show / Hide Value CONST value input for variables.
 * @param revert
 */
function show_variable_val_input(revert) {
    if (revert === true) {
        $('#variable_value_form_group').hide();
    } else {
        $('#variable_value_form_group').show();
    }
}


function show_belongs_to_enum_input(revert=false) {
    if (revert === true) {
        $('#variable_belongs_to_form_group').hide();
    } else {
        $('#variable_belongs_to_form_group').show();
    }
}

function show_enumerators_in_modal(revert=false) {
    if (revert === true) {
        $('.enum-controls').hide();
    } else {
        $('.enum-controls').show();
    }
}


function load_enumerators_to_modal(var_name) {
    $.post( "api/var/get_enumerators",
        {
            name: var_name
        },
        function( data ) {
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                // Remove prefix from Enumerators for display.
                $.each(data['enumerators'], function (index, item) {
                    const stripped_name = item[0].substr(var_name.length + 1);
                    add_enumerator_template(stripped_name, item[1]);
                })
            }
    }).done(function () {
        update_displayed_constraint_inputs();
        update_formalization();
        bind_expression_buttons();
    });
}


function load_variable(row_idx) {
    // Get row data
    let data = $('#variables_table').DataTable().row(row_idx).data();

    // Prepare requirement Modal
    let var_modal_content = $('.modal-content');
    show_variable_val_input(true);
    show_enumerators_in_modal(true);
    show_belongs_to_enum_input(true);
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
    let variable_value = $('#variable_value');
    let variable_value_old = $('#variable_value_old');
    let belongs_to_enum = $('#belongs_to_enum');
    let belongs_to_enum_old = $('#belongs_to_enum_old');
    let enumerators = $('#enumerators');

    type_input.val(data.type);
    variable_value.val('');
    variable_value_old.val('');
    belongs_to_enum.val('');
    belongs_to_enum_old.val('');
    enumerators.html('');

    if (data.type === 'CONST' || data.type === 'ENUMERATOR_INT' || data.type === 'ENUMERATOR_REAL') {
        show_variable_val_input();
        variable_value.val(data.const_val);
        variable_value_old.val(data.const_val);
    }
    if (data.type === 'ENUMERATOR_INT' || data.type === 'ENUMERATOR_REAL') {
        show_belongs_to_enum_input();
        belongs_to_enum.val(data.belongs_to_enum);
        belongs_to_enum_old.val(data.belongs_to_enum);
    }
    if (data.type === 'ENUM_REAL' || data.type === 'ENUM_INT') {
        show_enumerators_in_modal();
        load_enumerators_to_modal(data.name);
    }

    type_input.autocomplete({
        minLength: 0,
        source: available_types
    }).on('focus', function() { $(this).keydown(); });

    // Load constraints
    get_variable_constraints_html(data.name);

    var_modal_content.LoadingOverlay('hide');
}


function add_variable_via_modal() {
    const new_variable_name = $('#new_variable_name').val();
    const new_variable_type = $('#new_variable_type').val();
    const new_variable_value = $('#new_variable_const_value').val();
    $.post( "api/var/add_new_variable",
    {
        name: new_variable_name,
        type: new_variable_type,
        value: new_variable_value
    },
    function( data ) {
        if (data['success'] === false) {
            alert(data['errormsg']);
        } else {
            location.reload();
        }
    });
}


function add_enumerator_template(name, value) {
    const enumerator_template = `
        <div class="input-group enumerator-input">
            <span class="input-group-addon">Name</span>
            <input class="form-control enum_name_input" type="text" value="${name}">
            <span class="input-group-addon">Value</span>
            <input class="form-control enum_value_input" type="number" step="any" value="${value}">
            <buttton type="button" class="btn btn-danger input-group-addon del_enum" data-name="${name}">Delete</buttton>
        </div>`;
    $('#enumerators').append(enumerator_template);
}


function delete_enumerator(enum_name, enumerator_name, enum_dom) {
    let var_modal = $('#variable_modal');
    var_modal.LoadingOverlay('show');
    $.post( "api/var/del_var",
    {
        name: enum_name + '_' + enumerator_name
    },
    function( data ) {
        var_modal.LoadingOverlay('hide', true);
        if (data['success'] === false) {
            alert(data['errormsg']);
        } else {
            enum_dom.remove();
        }
    });
}


/**
 * Test if pasted_text has the form:
 * foo<TAB>12
 * bar<TAB>42
 *
 * @param pasted_text
 * @returns {boolean}
 */
function has_smart_input_form(pasted_text){
    const array_of_lines = pasted_text.match(/[^\r\n]+/g);
    if (array_of_lines.length <= 0) {
        return false;
    }

    for (const line of array_of_lines) {
        const line_splits = line.match(/[^\t]+/g);
        if (line_splits.length !== 2) {
            return false;
        }
        if (isNaN(line_splits[1])) {
            return false;
        }
    }
    return true;
}


/**
 * Create a 2D array from input like
 *   foo<TAB>12
 *   bar<TAB>42
 *
 *  -> [[foo, 12], [bar, 42]]
 * @param pasted_text
 * @returns {Array}
 */
function get_smart_input_array(pasted_text){
    const array_of_lines = pasted_text.match(/[^\r\n]+/g);
    let result = [];
    for (const line of array_of_lines) {
        const line_splits = line.match(/[^\t]+/g);
        result.push([line_splits[0], line_splits[1]]);
    }
    return result;
}


/**
 * Show the value input for new consts if type CONST is selected.
 */
function update_new_var_const_value_input(){
    const current_type = $('#new_variable_type').val();
    let value_input = $('#new_variable_const_input');
    current_type === 'CONST' ? value_input.show() : value_input.hide();
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
                    let search_all = '';
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
                                let search_query = '?command=search&col=2&q=%5C%22' + name + '%5C%22';
                                result += '<span class="badge badge-info">' +
                                    '<a href="./' + search_query + '" target="_blank">' + name + '</a>' +
                                    '</span> ';
                                if (search_all.length > 0) {
                                    search_all += '%3AOR%3A%5C%22' + name + '%5C%22';
                                } else {
                                    search_all += '?command=search&col=2&q=%5C%22' + name + '%5C%22';
                                }
                            }
                        }
                    });
                    if (result.length < 1) {
                        result += '<span class="badge badge-warning">' +
                            '<a href="#">Not used</a>' +
                            '</span></br>';
                    } else {
                        if (data.length > 1) {
                            result += '<span class="badge badge-info" style="background-color: #4275d8">' +
                                '<a href="./' + search_all + '" target="_blank">Show all</a>' +
                                '</span> ';
                        }
                    }
                    return result;
                }

            },
            {
                "data": "script_results",
                "targets": [4],
                "render": function ( data, type, row, meta ) {
                    return data;
                }
            },
            {
                "data": "used_by",
                "targets": [5],
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
        infoCallback: function( settings, start, end, max, total, pre ) {
            var api = this.api();
            var pageInfo = api.page.info();

            $('#clear-all-filters-text').html("Showing " + total +"/"+ pageInfo.recordsTotal + ". Clear all.");

            let result = "Showing " + start + " to " + end + " of " + total + " entries";
            result += " (filtered from " + pageInfo.recordsTotal + " total entries).";

            return result;
        },
        initComplete : function() {
            $('#search_bar').val(var_search_string);
            $('.variable_link').click(function (event) {
                event.preventDefault();
                load_variable(get_rowidx_by_var_name($(this).data('name')));
            });

            update_search();

            // Enable Hanfor specific table filtering.
            $.fn.dataTable.ext.search.push(
                function( settings, data, dataIndex ) {
                    // data contains the row. data[0] is the content of the first column in the actual row.
                    // Return true to include the row into the data. false to exclude.
                    return evaluate_search(data);
                }
            );

            this.api().draw();
        }
    });
    variables_table.column(4).visible(true);
    variables_table.column(5).visible(false);

    let search_bar = $('#search_bar');
    // Init search Bar Autocomplete
    new Awesomplete(search_bar[0], {
            filter: function(text, input) {
                let result = false;
                // If we have an uneven number of ":"
                // We check if we have a match in the input tail starting from the last ":"
                if ((input.split(":").length-1)%2 === 1) {
                    result = Awesomplete.FILTER_CONTAINS(text, input.match(/[^:]*$/)[0]);
                }
		        return result;
		    },
            item: function(text, input) {
                // Match inside ":" enclosed item.
		        return Awesomplete.ITEM(text, input.match(/(:)([\S]*$)/)[2]);
	        },
            replace: function(text) {
                // Cut of the tail starting from the last ":" and replace by item text.
                const before = this.input.value.match(/(.*)(:(?!.*:).*$)/)[1];
		        this.input.value = before + text;
	        },
            list: search_autocomplete,
            minChars: 1,
            autoFirst: true
    });

    // Bind big custom searchbar to search the table.
    search_bar.keypress(function(e) {
        if(e.which === 13) { // Search on enter.
            update_search();
            variables_table.draw();
        }
    });

    // Add listener for variable link to modal.
    $('#variables_table  tbody').on('click', 'a.modal-opener', function (event) {
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
            show_variable_val_input();
        } else {
            show_variable_val_input(revert=true);
        }
        if ($( this ).val() === 'ENUMERATOR_INT' || $( this ).val() === 'ENUMERATOR_REAL') {
            show_belongs_to_enum_input();
            show_variable_val_input();
        } else {
            show_belongs_to_enum_input(true)
        }
        if ($( this ).val() === 'ENUM_INT' || $( this ).val() === 'ENUM_REAL' ) {
            show_enumerators_in_modal();
        } else {
            show_enumerators_in_modal(revert=true);
        }
    });

    // Add listener for importing variables from existing sessions/revisions
    $('.import_link').on('click', function () {
        const sess_name = $( this ).attr('data-name');
        const sess_revision = $( this ).attr('data-revision');

        open_import_modal(sess_name, sess_revision);
    });

    $('#start_variable_import_session').click(function ( e ) {
        start_import_session();
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

    // Add new variable via modal.
    $('#save_new_variable_modal').click(function () {
        add_variable_via_modal();
    });

    // Add new enumerator from emum modal
    $('#add_enumerator').click(function () {
        add_enumerator_template('');
    });

    // Delete enumerator via the enum modal.
    $('#enumerators').on('click', '.del_enum', function(e) {
        const enumerator_name = $(this).attr('data-name');
        const enum_name = $('#variable_name_old').val();
        let enum_dom = $(this).parent('.enumerator-input');
        if (enumerator_name.length === 0) {
            enum_dom.remove();
        } else {
            delete_enumerator(enum_name, enumerator_name, enum_dom);
        }
    }).on('paste', '.enum_name_input', function (e) {
        let pasted_text = e.originalEvent.clipboardData.getData('text');

        if (has_smart_input_form(pasted_text)) {
            console.log('has smart input form');
            const smart_input_array = get_smart_input_array(pasted_text);
            console.log(smart_input_array);
            for (const line of smart_input_array) {
                add_enumerator_template(line[0], line[1]);
            }
            e.preventDefault();
        }
    });

    $('#generate_req').click(function () {
        $('#generate_req_form').submit();
    });

    // Clear all applied searches.
    $('.clear-all-filters').click(function () {
        $('#search_bar').val('').effect("highlight", {color: 'green'}, 500);
        update_search();
        variables_table.draw();
    });

    $('#variable_new_vaiable_modal').on('show.bs.modal change', function (e) {
        update_new_var_const_value_input();
    })
} );
