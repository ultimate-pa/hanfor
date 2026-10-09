import ApiClient from "./api/ApiClient.js"
import { AVAILABLE_VARIABLE_TYPES, VARIABLE_NAME_RE } from "./available-variable-types.js"
import TemplateRenderer from "./template/TemplateRenderer.js"
import TrackedStore from "./store/TrackedStore.js"
import { FORMALIZATION_TYPE, read_formalization_card, update_previews, update_var_groups } from "./formalizations/formalization-card.js"
import { bind_card_events, patch_edited_cards, show_save_errors } from "./formalizations/card-accordion.js"
require('gasparesganga-jquery-loading-overlay');
const {Modal, Toast} = require("bootstrap");

require('datatables.net-bs5');
require('datatables.net-select');
require("datatables.net-colresize-unofficial")
require("datatables.net-colresize-unofficial/jquery.dataTables.colResize.css")
require('jquery-ui/ui/widgets/autocomplete');
require('./bootstrap-tokenfield.js');
require('jquery-ui/ui/effects/effect-highlight');
require('awesomplete');
require('awesomplete/awesomplete.css');
//require('datatables.net-colreorderwithresize-npm');
require('datatables.net-colreorder-bs5');
require('./bootstrap-confirm-button');

let utils = require('./hanfor-utils');

// Globals
const api = new ApiClient()
const renderer = new TemplateRenderer({baseUrl: "/static/templates/formalizations"})
renderer.registerType("formalization", {
    ...FORMALIZATION_TYPE,
    defaults: {...FORMALIZATION_TYPE.defaults, variable_constraint: true},
})
const store = new TrackedStore()
store.registerType("constraint", {
    readDOM(id) {
        const $item = $(`#formalization_accordion > .accordion-item[data-id="${id}"]`)
        return $item.length ? {temp_id: String(id), ...read_formalization_card($item)} : null
    },
    persistCreate: (vid, drafts) => api.createVariableConstraints(vid, drafts),
    persistDelete: (vid, cid) => api.deleteVariableConstraint(vid, cid),
})
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
let type_inference_errors = {};
const {SearchNode} = require('./datatables-advanced-search.js');
let search_tree = undefined;
let visible_columns = [true, true, true, true, true];
let get_query = JSON.parse(search_query); // search_query is set in layout.html
const {sendTelemetry} = require('../../telemetry/static/telemetry')

/**
 * Apply search tree on datatables data.
 * @param data
 * @returns {bool|XPathResult}
 */
function evaluate_search(data) {
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

function validateNameInput($input) {
    const val = $input.val().trim();
    if (val && !VARIABLE_NAME_RE.test(val)) {
        $input.addClass("is-invalid");
        return false;
    }
    $input.removeClass("is-invalid");
    return true;
}

function validateTypeInput($input) {
    const val = $input.val();
    if (val && !AVAILABLE_VARIABLE_TYPES.includes(val)) {
        $input.addClass("is-invalid");
        return false;
    }
    $input.removeClass("is-invalid");
    return true;
}

/**
 * Store the currently active (in the modal) variable.
 * @param variables_table
 */
function store_variable(variables_table) {
    if (!validateNameInput($('#variable_name'))) return;
    if (!validateTypeInput($('#variable_type'))) return;

    let var_modal_content = $('.modal-content');
    var_modal_content.LoadingOverlay('show');

    // Get data.
    const var_name = $('#variable_name').val();
    const var_name_old = $('#variable_name_old').val();
    const var_type = $('#variable_type').val();
    const associated_row_id = parseInt($('#modal_associated_row_index').val());
    const const_val = $('#variable_value').val();
    const belongs_to_enum = $('#belongs_to_enum').val();

    const vid = $('#variable_id').val();
    const $accordion = $('#formalization_accordion');
    const edited_constraints = $accordion.children('.accordion-item.draft').toArray()
        .map(item => [String($(item).data('id')), read_formalization_card($(item))])
        .filter(([id]) => !store.isCreated('constraint', id));
    const constraints_changed = edited_constraints.length > 0 || !store.hasNoDrafts('constraint');

    // Process enumerators in case we have an enum
    let enumerators = [];
    if ((var_type === 'ENUM_INT') || (var_type === 'ENUM_REAL')) {
        // Fetch enumerators.
        $('.enumerator-input').each(function () {
            let enum_name = $(this).find('.enum_name_input').val();
            let enum_value = $(this).find('.enum_value_input').val();
            enumerators.push([enum_name, enum_value]);
        });
    }

    // TODO use variable UUID
    sendTelemetry("variables", var_name_old, "save")

    // Store the constraints, then the variable.
    $.when(
        store.commitDeletes(vid, 'constraint'),
        store.commitCreated(vid, 'constraint'),
    ).then(() =>
        patch_edited_cards($accordion, edited_constraints, (id, entry) =>
            api.patchVariableConstraint(vid, store.resolveId(id), entry)),
    ).then(() =>
        api.patchVariable(vid, {
            name: var_name,
            type: var_type,
            const_val: const_val,
            enumerators: enumerators,
            belongs_to_enum: belongs_to_enum
        }),
    ).done(function (data) {
        let modal = $('#variable_modal')
        modal.data('unsaved_changes', false);
        if (data.rebuild_table || constraints_changed) {
            Modal.getOrCreateInstance(modal).hide()
            $('#variables_table').DataTable().ajax.reload(null, false)
        } else {
            variables_table.row(associated_row_id).data(data.data).draw();
            Modal.getOrCreateInstance(modal).hide()
        }
    }).fail(function (err) {
        if (err?.responseJSON?.errors) {
            show_save_errors(renderer, $accordion, err.responseJSON.errors);
            return;
        }
        alert(err?.responseJSON?.errormsg || err?.statusText);
    }).always(function () {
        var_modal_content.LoadingOverlay('hide', true);
    });
}

/**
 * Apply multi edit on selected variables.
 * @param variables_table
 * @param del
 */
function apply_multi_edit(variables_table, del = false) {
    const change_type = $('#multi-change-type-input').val().trim();
    const selected = variables_table.rows({selected: true}).data().toArray();
    if (selected.length === 0) {
        alert('No variables selected.');
        return;
    }
    if (!del && !change_type) return;

    let page = $('body');
    page.LoadingOverlay('show');
    const requests = selected.map(variable =>
        del ? api.deleteVariable(variable.id) : api.patchVariable(variable.id, {type: change_type})
    );
    Promise.allSettled(requests).then(function (results) {
        const failed = results
            .map((result, i) => [result, selected[i]])
            .filter(([result]) => result.status === 'rejected')
            .map(([result, variable]) =>
                `${variable.name}: ${result.reason?.responseJSON?.errormsg || result.reason?.statusText}`);
        page.LoadingOverlay('hide', true);
        if (failed.length) alert(failed.join('\n'));
        location.reload();
    });
}

function refresh_cards() {
    const variable_names = $('#variables_table').DataTable().rows().data().toArray().map(variable => variable.name);
    const $accordion = $('#formalization_accordion');
    update_var_groups($accordion, type_inference_errors);
    update_previews($accordion, variable_names);
}

async function load_constraints(vid) {
    await renderer.ready();
    const constraints = await api.getVariableConstraints(vid);
    type_inference_errors = Object.fromEntries(constraints
        .filter(constraint => constraint.type_inference_errors.length)
        .map(constraint => [constraint.id, constraint.type_inference_errors]));
    $('#formalization_accordion').html('')
        .append(constraints.map(constraint => renderer.build('formalization', constraint)));
    refresh_cards();
    $('#variable_modal').data('unsaved_changes', false);
}

function add_constraint() {
    const $card = renderer.build('formalization', {id: store.create('constraint')});
    $card.addClass('draft');
    $('#formalization_accordion').append($card);
    refresh_cards();
}

function delete_constraint(id, $card) {
    store.delete('constraint', id);
    $card.remove();
    refresh_cards();
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
        .row(function (idx, data) {
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

function show_belongs_to_enum_input(revert = false) {
    if (revert === true) {
        $('#variable_belongs_to_form_group').hide();
    } else {
        $('#variable_belongs_to_form_group').show();
    }
}

function show_enumerators_in_modal(revert = false) {
    if (revert === true) {
        $('.enum-controls').hide();
    } else {
        $('.enum-controls').show();
    }
}

function load_enumerators_to_modal(var_id, var_name) {
    api.getEnumerators(var_id).done(function (data) {
        // Remove prefix from Enumerators for display.
        $.each(data['enumerators'], function (index, item) {
            const stripped_name = item[0].substr(var_name.length + 1);
            add_enumerator_template(stripped_name, item[1], item[2]);
        })
    }).fail(function (err) {
        alert(err?.responseJSON?.errormsg || err?.statusText);
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
    // $('#variable_modal').modal('show');
    Modal.getOrCreateInstance(document.getElementById('variable_modal')).show();

    // Meta information
    $('#modal_associated_row_index').val(row_idx);
    $('#variable_id').val(data.id);
    $('#variable_name_old').val(data.name);

    // Visible information
    $('#variable_modal_title').html('Variable: ' + data.name);
    $('#variable_name').val(data.name);

    let type_input = $('#variable_type');
    let variable_value = $('#variable_value');
    let belongs_to_enum = $('#belongs_to_enum');
    let enumerators = $('#enumerators');

    type_input.val(data.type);
    variable_value.val('');
    belongs_to_enum.val('');
    enumerators.html('');

    if (data.type === 'CONST' || data.type === 'ENUMERATOR_INT' || data.type === 'ENUMERATOR_REAL') {
        show_variable_val_input();
        variable_value.val(data.const_val);
    }
    if (data.type === 'ENUMERATOR_INT' || data.type === 'ENUMERATOR_REAL') {
        show_belongs_to_enum_input();
        belongs_to_enum.val(data.belongs_to_enum);
    }
    if (data.type === 'ENUM_REAL' || data.type === 'ENUM_INT') {
        show_enumerators_in_modal();
        load_enumerators_to_modal(data.id, data.name);
    }

    type_input.autocomplete({
        minLength: 0,
        source: AVAILABLE_VARIABLE_TYPES
    }).on('focus', function () {
        $(this).keydown();
    });

    $('#variable-type-feedback').text("Supported: " + AVAILABLE_VARIABLE_TYPES.join(", "));
    validateNameInput($('#variable_name'));
    validateTypeInput($('#variable_type'));

    // Load constraints
    load_constraints(data.id).catch(err => alert(err?.responseJSON?.errormsg || err?.statusText || err));
    // TODO send variable UUID
    sendTelemetry("variables", data.name, "open")

    var_modal_content.LoadingOverlay('hide');
}

function add_variable_via_modal() {
    if (!validateNameInput($('#new_variable_name'))) return;
    const new_variable_name = $('#new_variable_name').val();
    const new_variable_type = $('#new_variable_type').val();
    const new_variable_value = $('#new_variable_const_value').val();
    api.createVariable({
        name: new_variable_name,
        type: new_variable_type,
        value: new_variable_value
    }).done(function () {
        location.reload();
        $('#new_variable_name').val("")
    }).fail(function (err) {
        alert(err?.responseJSON?.errormsg || err?.statusText);
    });
}

function add_enumerator_template(name, value, id = '') {
    const enumerator_template = `
        <div class="input-group enumerator-input">
            <span class="input-group-prepend input-group-text">Name</span>
            <input class="form-control enum_name_input" type="text" value="${name}">
            <span class="input-group-prepend input-group-text">Value</span>
            <input class="form-control enum_value_input" type="number" step="any" value="${value}">
            <buttton type="button" class="btn btn-danger input-group-append del_enum" data-id="${id}">Delete</buttton>
        </div>`;
    $('#enumerators').append(enumerator_template);
}

function delete_enumerator(enumerator_id, enum_dom) {
    let var_modal = $('#variable_modal');
    var_modal.LoadingOverlay('show');
    api.deleteVariable(enumerator_id).done(function () {
        enum_dom.remove();
    }).fail(function (err) {
        alert(err?.responseJSON?.errormsg || err?.statusText);
    }).always(function () {
        var_modal.LoadingOverlay('hide', true);
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
function has_smart_input_form(pasted_text) {
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
function get_smart_input_array(pasted_text) {
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
function update_new_var_const_value_input() {
    const current_type = $('#new_variable_type').val();
    let value_input = $('#new_variable_const_input');
    current_type === 'CONST' ? value_input.show() : value_input.hide();
}

$(document).ready(function () {
    init_modal()

    // Prepare and load the variables table.
    let variables_table = $('#variables_table').DataTable({
        "paging": true,
        "stateSave": true,
        "select": {
            style: 'os',
            selector: 'td:first-child'
        },
        "pageLength": 50,
        "responsive": true,
        "lengthMenu": [[10, 50, 100, 500, -1], [10, 50, 100, 500, "All"]],
        "dom": 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        "ajax": (data, callback) => api.getVariables().done(callback),
        "deferRender": true,
        colResize: {
          onResize: function () { throw new Error('Workaround: resizing works fine!'); },
        },
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
                "render": function (data) {
                    return '<a class="modal-opener" href="#">' + data + '</span></br>';
                }
            },
            {
                "data": "type",
                "targets": [2],
                "render": function (data, type, row) {
                    if (data !== null && data === 'CONST') {
                        data = data + ' (' + row['const_val'] + ')';
                    }
                    return data;
                }
            },
            {
                "data": "constraints",
                "targets": [3],
                "render": function (data) {
                    let result = '';

                    $(data).each(function (id, name) {
                        if (name.length > 0) {
                            result += name;
                        }
                    });
                    return result;
                }
            },
            {
                "data": "tags",
                "targets": [4],
                "render": function (data) {
                    let result = '';

                    $(data).each(function (id, name) {
                        if (name.length > 0) {
                            result += '<span class="badge bg-danger">' + name +
                                '</span>';
                        }
                    });
                    return result;
                }
            },
            {
                "data": "used_by",
                "targets": [5],
                "render": function (data, type, row) {
                    let result = '';
                    let search_all = '';
                    $(data).each(function (id, name) {
                        if (name.length > 0 && !is_constraint_link(name)) {
                            let search_query = '?command=search&col=2&q=%5C%22' + name + '%5C%22';
                            result += '<span class="badge bg-info">' +
                                '<a href="./' + search_query + '" target="_blank" class="link-light">' + name + '</a>' +
                                '</span> ';
                            if (search_all.length > 0) {
                                /* ToDo: Simplify search query */
                                search_all += '%3AOR%3A' + '%3ACOL_INDEX_02%3A' + '%5C%22' + name + '%5C%22';
                            } else {
                                search_all += search_query;
                            }
                        }
                    });
                    if (result.length < 1) {
                        result += '<span class="badge bg-warning">' +
                            'unused' +
                            '</span></br>';
                    } else {
                        if (data.length > 1) {
                            result += '<span class="badge bg-info">' +
                                '<a href="./' + search_all + '" target="_blank" class="link-light">Show all</a>' +
                                '</span> ';
                        }
                    }
                    return result;
                }

            },
            {
                "data": "script_results",
                "targets": [6],
                "render": function (data) {
                    return data;
                }
            },
            {
                "data": "used_by",
                "targets": [7],
                "visible": false,
                "searchable": false,
                "render": function (data) {
                    let result = '';
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
        infoCallback: function (settings, start, end, max, total) {
            let api = this.api();
            let pageInfo = api.page.info();

            $('#clear-all-filters-text').html("Showing " + total + "/" + pageInfo.recordsTotal + ". Clear all.");

            let result = "Showing " + start + " to " + end + " of " + total + " entries";
            result += " (filtered from " + pageInfo.recordsTotal + " total entries).";

            return result;
        },
        initComplete: function () {
            $('#search_bar').val(var_search_string);
            $('.variable_link').click(function (event) {
                event.preventDefault();
                load_variable(get_rowidx_by_var_name($(this).data('name')));
            });

            utils.process_url_query(get_query);
            update_search();

            // Enable Hanfor specific table filtering.
            $.fn.dataTable.ext.search.push(
                function (settings, data) {
                    // data contains the row. data[0] is the content of the first column in the actual row.
                    // Return true to include the row into the data. false to exclude.
                    return evaluate_search(data);
                }
            );

            this.api().draw();
        }
    });
    variables_table.column(6).visible(false);
    variables_table.column(7).visible(false);

    new $.fn.dataTable.ColReorder(variables_table, {});

    let search_bar = $('#search_bar');
    // Init search Bar Autocomplete
    new Awesomplete(search_bar[0], {
        filter: function (text, input) {
            let result = false;
            // If we have an uneven number of ":"
            // We check if we have a match in the input tail starting from the last ":"
            if ((input.split(":").length - 1) % 2 === 1) {
                result = Awesomplete.FILTER_CONTAINS(text, input.match(/[^:]*$/)[0]);
            }
            return result;
        },
        item: function (text, input) {
            // Match inside ":" enclosed item.
            return Awesomplete.ITEM(text, input.match(/(:)([\S]*$)/)[2]);
        },
        replace: function (text) {
            // Cut of the tail starting from the last ":" and replace by item text.
            const before = this.input.value.match(/(.*)(:(?!.*:).*$)/)[1];
            this.input.value = before + text;
        },
        list: search_autocomplete,
        minChars: 1,
        autoFirst: true
    });

    // Bind big custom searchbar to search the table.
    search_bar.keypress(function (e) {
        if (e.which === 13) { // Search on enter.
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

    $('#variable_name').on('input', function () {
        validateNameInput($(this));
    });

    $('#new_variable_name').on('input', function () {
        validateNameInput($(this));
    });

    $('#variable_type').on('keyup change autocompleteclose', function () {
        validateTypeInput($(this));
        if ($(this).val() === 'CONST') {
            show_variable_val_input();
        } else {
            show_variable_val_input(true);
        }
        if ($(this).val() === 'ENUMERATOR_INT' || $(this).val() === 'ENUMERATOR_REAL') {
            show_belongs_to_enum_input();
            show_variable_val_input();
        } else {
            show_belongs_to_enum_input(true)
        }
        if ($(this).val() === 'ENUM_INT' || $(this).val() === 'ENUM_REAL') {
            show_enumerators_in_modal();
        } else {
            show_enumerators_in_modal(true);
        }
    });

    // Multiselect.
    // Select single rows
    $('.select-all-button').on('click', function () {
        // Toggle selection on
        if ($(this).hasClass('btn-secondary')) {
            variables_table.rows({page: 'current'}).select();
        } else { // Toggle selection off
            variables_table.rows({page: 'current'}).deselect();
        }
        // Toggle button state.
        $('.select-all-button').toggleClass('btn-secondary btn-primary');
    });

    // Toggle "Select all rows to `off` on user specific selection."
    variables_table.on('user-select', function () {
        let select_buttons = $('.select-all-button');
        select_buttons.removeClass('btn-primary');
        select_buttons.addClass('btn-secondary ');
    });

    // Bind autocomplete for "edit-selected" types
    $('#multi-change-type-input').autocomplete({
        minLength: 0,
        source: AVAILABLE_VARIABLE_TYPES,
        delay: 100
    }).on('focus', function () {
        $(this).keydown();
    }).val('');

    $('.apply-multi-edit').click(function () {
        apply_multi_edit(variables_table);
    });

    // Multi Delete variables.
    // $('.delete_button').confirmation({
    //     rootSelector: '.delete_button'
    // }).click(function () {
    //     apply_multi_edit(variables_table, true);
    // });

    $('body').on('click', '.delete_button', function () {
        const element = $(this)

        if (element.data('html') === undefined) {
            element.outerWidth(element.outerWidth()).data('html', element.html()).html('Do it!')

            setTimeout(function () {
                element.html(element.data('html')).removeData('html').outerWidth('')
            }, 2000)
        } else {
            element.html(element.data('html')).removeData('html').outerWidth('')
            apply_multi_edit(variables_table, true)
        }
    })


    // Add new Constraint
    $('#add_constraint').click(function () {
        add_constraint();
    });
    bind_card_events('#formalization_accordion', {onChange: refresh_cards, onDelete: delete_constraint});

    // Add new variable via modal.
    $('#save_new_variable_modal').click(function () {
        add_variable_via_modal();
    });

    // Add new enumerator from emum modal
    $('#add_enumerator').click(function () {
        add_enumerator_template('')
    });

    // Delete enumerator via the enum modal.
    $('#enumerators').on('click', '.del_enum', function () {
        const enumerator_id = $(this).attr('data-id');
        let enum_dom = $(this).parent('.enumerator-input');
        if (enumerator_id.length === 0) {
            enum_dom.remove();
        } else {
            delete_enumerator(enumerator_id, enum_dom);
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

    // Clear all applied searches.
    $('.clear-all-filters').click(function () {
        $('#search_bar').val('').effect("highlight", {color: 'green'}, 500);
        update_search();
        variables_table.draw();
    });

    //$('#variable_new_vaiable_modal').on('show.bs.modal change', function () {
    //    update_new_var_const_value_input();
    //})
    $('#variable_new_vaiable_modal')[0].addEventListener('show.bs.modal', function () {
        update_new_var_const_value_input();
    });
    $('#new_variable_type').on('change', function () {
        update_new_var_const_value_input();
    });

    $('#import-variables-from-csv-input').change(async function () {
        const csv = await this.files[0].text();
        api.importVariables(csv)
            .done(() => location.reload())
            .fail(e => alert(e.responseJSON?.errormsg || e.statusText));
    })
});

function init_modal() {
    let modal = $('#variable_modal')

    modal[0].addEventListener('hide.bs.modal', function (event) {
        modal_closing_routine(event);
    })

    modal[0].addEventListener('hidden.bs.modal', function () {
        store.reset();
        document.querySelectorAll('#save_error_toasts .toast').forEach(el => Toast.getOrCreateInstance(el).hide());
    })

    $('#variable_name').change(function () {
        $('#variable_modal').data('unsaved_changes', true);
    })

    $('#variable_type').change(function () {
        $('#variable_modal').data('unsaved_changes', true);
    })

    $('#variable_value').change(function () {
        $('#variable_modal').data('unsaved_changes', true);
    })

    $('#belongs_to_enum').change(function () {
        $('#variable_modal').data('unsaved_changes', true);
    })
}

function modal_closing_routine(event) {
    const unsaved_changes = $('#variable_modal').data('unsaved_changes');
    if (unsaved_changes === true) {
        const force_close = confirm("You have unsaved changes, do you really want to close?");
        if (force_close !== true) {
            event.preventDefault();
        } else {
            sendTelemetry("variables", $('#variable_name_old').val(), "close_without_save")
        }
    } else {
        sendTelemetry("variables", $('#variable_name_old').val(), "close")
    }
}
