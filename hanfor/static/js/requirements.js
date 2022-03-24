require('gasparesganga-jquery-loading-overlay');
require('bootstrap');
require('bootstrap-confirmation2');
require('datatables.net-bs4');
require('datatables.net-select-bs4');
require('jquery-ui/ui/widgets/autocomplete');
require('jquery-ui/ui/effects/effect-highlight');
require('./bootstrap-tokenfield.js');
require('awesomplete');
require('awesomplete/awesomplete.css');
require('datatables.net-colreorderwithresize-npm');


let utils = require('./hanfor-utils');
const autosize = require('autosize');

// Globals
const {SearchNode} = require('./datatables-advanced-search.js');
const {init_simulator_tab} = require("./simulator.js");
let Fuse = require('fuse.js');
let {Textcomplete, Textarea} = require('textcomplete');
let fuse = new Fuse([], {});

let available_tags = ['', 'has_formalization'];
let available_status = ['', 'Todo', 'Review', 'Done'];
let search_autocomplete = [
    ":AND:",
    ":OR:",
    ":NOT:",
    ":COL_INDEX_01:",
    ":COL_INDEX_02:",
    ":COL_INDEX_03:",
    ":COL_INDEX_04:",
    ":COL_INDEX_05:",
    ":COL_INDEX_06:",
    ":COL_INDEX_07:"
];
let available_types = [''];
let available_vars = [''];
let available_reports = [];
let available_search_strings = [''];
let visible_columns = [true, true, true, true, true, true];
let filter_search_array = [];
let get_query = JSON.parse(search_query); // search_query is set in layout.html
let tag_colors = {};
let type_inference_errors = [];
let req_search_string = sessionStorage.getItem('req_search_string');
let filter_status_string = sessionStorage.getItem('filter_status_string');
let filter_tag_string = sessionStorage.getItem('filter_tag_string');
let filter_type_string = sessionStorage.getItem('filter_type_string');
let search_tree = undefined;
let filter_tree = undefined;


/**
 * Update the search expression tree.
 */
function update_search() {
    req_search_string = $('#search_bar').val().trim();
    sessionStorage.setItem('req_search_string', req_search_string);
    search_tree = SearchNode.fromQuery(req_search_string);
}

/**
 * Update the filter search tree used to filter the table by the values from the Filter tab.
 */
function update_filter() {
    filter_search_array = [];

    function pad_with_parantheses(array) {
        return ["("].concat(array, [")"]);
    }

    function add_query(array, query, target) {
        if (query.length > 0) {
            if (array.length > 0) {
                array = array.concat([":AND:"]);
            }
            array = array.concat(pad_with_parantheses(SearchNode.awesomeQuerySplitt0r(query, target)));
        }
        return array
    }

    filter_status_string = $('#status-filter-input').val();
    filter_tag_string = $('#tag-filter-input').val();
    filter_type_string = $('#type-filter-input').val();

    sessionStorage.setItem('filter_status_string', filter_status_string);
    sessionStorage.setItem('filter_tag_string', filter_tag_string);
    sessionStorage.setItem('filter_type_string', filter_type_string);

    filter_search_array = add_query(filter_search_array, filter_type_string, 4);
    filter_search_array = add_query(filter_search_array, filter_tag_string, 5);
    filter_search_array = add_query(filter_search_array, filter_status_string, 6);

    filter_tree = SearchNode.searchArrayToTree(filter_search_array);
}


function evaluate_search(data) {
    return search_tree.evaluate(data, visible_columns) && filter_tree.evaluate(data, visible_columns);
}

/**
 * Stores the active (in modal) requirement and updates the row in the requirements table.
 * @param {DataTable} requirements_table
 */
function store_requirement(requirements_table) {
    let requirement_modal_content = $('.modal-content');
    requirement_modal_content.LoadingOverlay('show');

    const req_id = $('#requirement_id').val();
    const req_tags = $('#requirement_tag_field').val();
    const req_status = $('#requirement_status').val();
    const updated_formalization = $('#requirement_modal').data('updated_formalization');
    const associated_row_id = parseInt($('#modal_associated_row_index').val());

    // Fetch the formalizations
    let formalizations = {};
    $('.formalization_card').each(function () {
        // Scope and Pattern
        let formalization = {};
        formalization['id'] = $(this).attr('title');
        $(this).find('select').each(function () {
            if ($(this).hasClass('scope_selector')) {
                formalization['scope'] = $(this).val();
            }
            if ($(this).hasClass('pattern_selector')) {
                formalization['pattern'] = $(this).val();
            }
        });

        // Expressions
        formalization['expression_mapping'] = {};
        $(this).find("textarea.reqirement-variable").each(function () {
            if ($(this).attr('title') !== '')
                formalization['expression_mapping'][$(this).attr('title')] = $(this).val();
        });

        formalizations[formalization['id']] = formalization;
    });

    // Store the requirement.
    $.post("api/req/update",
        {
            id: req_id,
            row_idx: associated_row_id,
            update_formalization: updated_formalization,
            tags: req_tags,
            status: req_status,
            formalizations: JSON.stringify(formalizations)
        },
        // Update requirements table on success or show an error message.
        function (data) {
            requirement_modal_content.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                requirements_table.row(associated_row_id).data(data);
                $('#requirement_modal').data('unsaved_changes', false).modal('hide');
            }
        }).done(function () {
        update_logs();
    });
}


/***
 *
 * @param requirements_table
 * @returns {Array} User selected requirement ids.
 */
function get_selected_requirement_ids(requirements_table) {
    let selected_ids = [];
    requirements_table.rows({selected: true}).every(function () {
        let d = this.data();
        selected_ids.push(d['id']);
    });

    return selected_ids
}


function apply_multi_edit(requirements_table) {
    let page = $('body');
    page.LoadingOverlay('show');
    let add_tag = $('#multi-add-tag-input').val().trim();
    let remove_tag = $('#multi-remove-tag-input').val().trim();
    let set_status = $('#multi-set-status-input').val().trim();
    let selected_ids = get_selected_requirement_ids(requirements_table);

    $.post("api/req/multi_update",
        {
            add_tag: add_tag,
            remove_tag: remove_tag,
            set_status: set_status,
            selected_ids: JSON.stringify(selected_ids)
        },
        // Update requirements table on success or show an error message.
        function (data) {
            page.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                location.reload();
            }
        });
}


function add_top_guess_to_selected_requirements(requirements_table) {
    let page = $('body');
    page.LoadingOverlay('show');
    let selected_ids = get_selected_requirement_ids(requirements_table);
    let insert_mode = $('#top_guess_append_mode').val();

    $.post("api/req/multi_add_top_guess",
        {
            selected_ids: JSON.stringify(selected_ids),
            insert_mode: insert_mode
        },
        // Update requirements table on success or show an error message.
        function (data) {
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
        $(this).hide();
        $(this).removeClass('type-error');
    });

    $('.formalization_card').each(function () {
        // Fetch attributes
        const formalization_id = $(this).attr('title');
        const selected_scope = $('#requirement_scope' + formalization_id).val();
        const selected_pattern = $('#requirement_pattern' + formalization_id).val();
        let header = $('#formalization_heading' + formalization_id);
        let var_p = $('#requirement_var_group_p' + formalization_id);
        let var_q = $('#requirement_var_group_q' + formalization_id);
        let var_r = $('#requirement_var_group_r' + formalization_id);
        let var_s = $('#requirement_var_group_s' + formalization_id);
        let var_t = $('#requirement_var_group_t' + formalization_id);
        let var_u = $('#requirement_var_group_u' + formalization_id);
        let var_v = $('#requirement_var_group_v' + formalization_id);

        // Set the red boxes for type inference failed expressions.
        if (formalization_id in type_inference_errors) {
            for (let i = 0; i < type_inference_errors[formalization_id].length; i++) {
                $('#formalization_var_' + type_inference_errors[formalization_id][i] + formalization_id)
                    .addClass('type-error');
                header.addClass('type-error-head');
            }
        } else {
            header.removeClass('type-error-head');
        }

        switch (selected_scope) {
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

        Object.keys(_PATTERNS[selected_pattern]['env']).forEach(function (key) {
            switch (key) {
                case 'R': var_r.show(); break;
                case 'S': var_s.show(); break;
                case 'T': var_t.show(); break;
                case 'U': var_u.show(); break;
                case 'V': var_v.show(); break;
            }
        });
    });
}


/**
 * Replace variables in a formalization string by links to that variable.
 * Only if variable is available in the global "available_vars" array.
 * Example: foo || bar -> <a href ...>foo</a> || <a href ...>bar</a>
 * @param formal_string
 * @returns {string}
 */
function parse_vars_to_link(formal_string) {
    let result = '';

    // Split the formalization string on possible variable delimiters given by the boogie grammar.
    // We enclose the regular expression by /()/g to yield the delimiters itself: We want to keep them in the result.
    formal_string.split(/([\s&<>!()=:\[\]{}\-|+*,])/g).forEach(function (chunk) {
        if ( available_vars.includes(chunk) ) {
            let query = '?command=search&col=1&q=%5C%22' + chunk + '%5C%22';
            result += '<a href="./variables' + query + '" target="_blank"' +
                '  title="Go to declaration of ' + chunk + '" class="alert-link">' + chunk + '</a>';
        } else {
            // We need to escape potential HTML special chars to prevent a broken display.
            result += utils.escapeHtml(chunk);
        }
    });
    return result;
}


/**
 * Updates the formalization textarea based on the selected scope and expressions in P, Q, R, S, T, ... .
 */
function update_formalization() {
    $('.formalization_card').each(function () {
        // Fetch attributes
        const formalization_id = $(this).attr('title');

        let formalization = '';
        let formalization_textarea = $('#current_formalization_textarea' + formalization_id);
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
        let var_v = $('#formalization_var_v' + formalization_id).val();

        if (var_p.length > 0) {
            formalization = formalization.replace(/{P}/g, parse_vars_to_link(var_p));
        }
        if (var_q.length > 0) {
            formalization = formalization.replace(/{Q}/g, parse_vars_to_link(var_q));
        }
        if (var_r.length > 0) {
            formalization = formalization.replace(/{R}/g, parse_vars_to_link(var_r));
        }
        if (var_s.length > 0) {
            formalization = formalization.replace(/{S}/g, parse_vars_to_link(var_s));
        }
        if (var_t.length > 0) {
            formalization = formalization.replace(/{T}/g, parse_vars_to_link(var_t));
        }
        if (var_u.length > 0) {
            formalization = formalization.replace(/{U}/g, parse_vars_to_link(var_u));
        }
        if (var_v.length > 0) {
            formalization = formalization.replace(/{V}/g, parse_vars_to_link(var_v));
        }

        formalization_textarea.html(formalization);
        autosize.update(formalization_textarea);
    });
    $('#requirement_modal').data({
        'unsaved_changes': true,
        'updated_formalization': true
    });
}


function add_formalization() {
    // Request a new Formalization. And add its edit elements to the modal.
    let requirement_modal_content = $('.modal-content');
    requirement_modal_content.LoadingOverlay('show');

    const req_id = $('#requirement_id').val();
    $.post("api/req/new_formalization",
        {
            id: req_id
        },
        function (data) {
            requirement_modal_content.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                let formalization = $(data['html']);
                formalization.find('.reqirement-variable').each(function () {
                    add_var_autocomplete(this);
                });
                formalization.appendTo('#formalization_accordion');
            }
        }).done(function () {
        update_vars();
        update_formalization();
        update_logs();
    });
}


function add_formalization_from_guess(scope, pattern, mapping) {
    // Request a new Formalization. And add its edit elements to the modal.
    let requirement_modal_content = $('.modal-content');
    requirement_modal_content.LoadingOverlay('show');

    let requirement_id = $('#requirement_id').val();
    $.post("api/req/add_formalization_from_guess",
        {
            requirement_id: requirement_id,
            scope: scope,
            pattern: pattern,
            mapping: JSON.stringify(mapping)
        },
        function (data) {
            requirement_modal_content.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                $('#formalization_accordion').append(data['html']);
            }
        }).done(function () {
        update_vars();
        update_formalization();
        bind_var_autocomplete();
        update_logs();
    });
}


function delete_formalization(formal_id, card) {
    let requirement_modal_content = $('.modal-content');
    requirement_modal_content.LoadingOverlay('show');
    const req_id = $('#requirement_id').val();
    $.post("api/req/del_formalization",
        {
            requirement_id: req_id,
            formalization_id: formal_id
        },
        function (data) {
            requirement_modal_content.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                card.remove();
            }
        }).done(function () {
        update_vars();
        update_formalization();
        update_logs();
    });
}


/**
 * Reload fuse the fuzzy search provider used for autocomplete.
 * fuse will be reloaded with available_vars.
 */
function update_fuse() {
    let options = {
        shouldSort: true,
        threshold: 0.6,
        location: 0,
        distance: 100,
        maxPatternLength: 12,
        minMatchCharLength: 1,
        keys: undefined
    };

    fuse = new Fuse(available_vars, options);
}


/**
 * Search term in the fuse fuzzy search provider.
 * Fuse is initialized with the available_vars.
 * @param term
 */
function fuzzy_search(term) {
    return fuse.search(term);
}


/**
 * Adds the variable autocompletion to a textarea given by dom_obj.
 * @param dom_obj
 */
function add_var_autocomplete(dom_obj) {
    let editor = new Textarea(dom_obj);
    let textcomplete = new Textcomplete(editor, {
        dropdown: {
            maxCount: 10
        }
    });
    textcomplete.register([{
        match: /(^|\s|[!=&\|>]+)(\w+)$/,
        search: function (term, callback) {
            let include_elems = fuzzy_search(term);

            let result = [];
            for (let i = 0; i < Math.min(10, include_elems.length); i++) {
                result.push(available_vars[include_elems[i]]);
            }
            callback(result);
        },
        replace: function (value) {
            return '$1' + value + ' ';
        }
    }]);
    // Close dropdown if textarea is no longer focused.
    $(dom_obj).on('blur click', function (e) {
        textcomplete.dropdown.deactivate();
        e.preventDefault();
    })
}


/**
 * Bind autocomplete trigger to all formalization input textareas.
 *
 */
function bind_var_autocomplete() {
    $(".reqirement-variable").each(function () {
        add_var_autocomplete(this);
    });
}


function prevent_double_token_insert() {
    $('#requirement_tag_field').on('tokenfield:createtoken', function (event) {
        let existingTokens = $(this).tokenfield('getTokens');
        $.each(existingTokens, function (index, token) {
            if (token.value === event.attrs.value)
                event.preventDefault();
        });
    });
}


function load_requirement(row_idx) {
    if (row_idx === -1) {
        alert("Requirement not found.");
        return
    }

    // Get row data
    let data = $('#requirements_table').DataTable().row(row_idx).data();

    // Prepare requirement Modal
    let requirement_modal_content = $('.modal-content');
    $('#requirement_modal').modal('show');
    requirement_modal_content.LoadingOverlay('show');
    $('#formalization_accordion').html('');

    // Set available tags.
    $('#requirement_tag_field').data('bs.tokenfield').$input.autocomplete({source: available_tags});

    // Get the requirement data and set the modal.
    $.get("api/req/get", {id: data['id'], row_idx: row_idx}, function (data) {
        if (data.success === false) {
            alert('Could Not load the Requirement: ' + data.errormsg);
            return;
        }

        // Meta information
        $('#requirement_id').val(data.id);
        $('#modal_associated_row_index').val(row_idx);
        available_vars = data.available_vars;
        available_vars = available_vars.concat(data.additional_static_available_vars);
        type_inference_errors = data.type_inference_errors;
        update_fuse();

        // Visible information
        $('#requirement_modal_title').html(data.id + ': ' + data.type);
        $('#description_textarea').text(data.desc).change();
        $('#add_guess_description').text(data.desc).change();

        // Parse the formalizations
        $('#formalization_accordion').html(data.formalizations_html);

        $('#requirement_scope').val(data.scope);
        $('#requirement_pattern').val(data.pattern);

        // Set the tags
        $('#requirement_tag_field').tokenfield('setTokens', data.tags);
        $('#requirement_status').val(data.status);

        // Set csv_data
        let csv_row_content = $('#csv_content_accordion');
        csv_row_content.html('');
        csv_row_content.collapse('hide');
        let csv_data = data.csv_data;
        for (const key in csv_data) {
            if (csv_data.hasOwnProperty(key)) {
                const value = csv_data[key];
                csv_row_content.append('<p><strong>' + key + ':</strong>' + value + '</p>');
            }
        }

        // Set revision diff data.
        let revision_diff_link = $('#show_revision_diff');
        if ($.isEmptyObject(data.revision_diff)) {
            revision_diff_link.hide();
        } else {
            revision_diff_link.show();
        }

        let revision_diff_content = $('#revision_diff_accordion');
        revision_diff_content.html('');
        revision_diff_content.collapse('hide');
        let revision_diff = data.revision_diff;
        for (const key in revision_diff) {
            if (revision_diff.hasOwnProperty(key)) {
                const value = revision_diff[key];
                revision_diff_content.append('<p><strong>' + key + ':</strong><pre>' + value + '</pre></p>');
            }
        }

        // Set used variables data.
        let used_variables_accordion = $('#used_variables_accordion');
        used_variables_accordion.html('');
        used_variables_accordion.collapse('hide');
        data.vars.forEach(function (var_name) {
            let query = '?command=search&col=1&q=%5C%22' + var_name + '%5C%22';
            used_variables_accordion.append(
              '<span class="badge badge-info">' +
              '<a href="./variables' + query + '" target="_blank">' + var_name + '</a>' +
              '</span>&numsp;'
            );
        });

    }).done(function () {
        // Update visible Vars.
        update_vars();
        // Handle autocompletion for variables.
        bind_var_autocomplete();
        // Update available vars based on the selection of requirement and pattern.
        // Prevent inserting a token twice on enter
        prevent_double_token_insert();
        update_formalization();
        $('#requirement_modal').data({
            'unsaved_changes': false,
            'updated_formalization': false
        });
        requirement_modal_content.LoadingOverlay('hide', true);
    });
}

/**
 * Bind the Links to open a requirement modal.
 * Implement Behaviour:
 *  * Load and show requirement data
 * @param requirements_table
 */
function bind_requirement_id_to_modals(requirements_table) {
    // Add listener for clicks on the Rows.
    $('#requirements_table').find('tbody').on('click', 'a', function (event) {
        // prevent body to be scrolled to the top.
        event.preventDefault();
        let row_idx = requirements_table.row($(this).closest('tr')).index();
        load_requirement(row_idx);
    });
}


/**
 * Update the color of the column toggle buttons.
 * Column visible -> Button blue (btn-info).
 * Column not visible -> Button grey (btn-secondary).
 * Update visible_columns
 */
function update_visible_columns_information() {
    let requirements_table = $('#requirements_table').DataTable();
    let new_visible_columns = [];
    $.each(requirements_table.columns().visible(), function (key, value) {
        if (value === false) {
            $('#col_toggle_button_' + key).removeClass('btn-info').addClass('btn-secondary');
            new_visible_columns.push(false);
        } else {
            $('#col_toggle_button_' + key).removeClass('btn-secondary').addClass('btn-info');
            new_visible_columns.push(true);
        }
    });
    visible_columns = new_visible_columns;
}


/**
 * Clear all user input in filters and search bar. Reload the table.
 */
function clear_all_search_filter_inputs() {
    $('#status-filter-input').val('').effect("highlight", {color: 'green'}, 500);
    $('#tag-filter-input').val('').effect("highlight", {color: 'green'}, 500);
    $('#type-filter-input').val('').effect("highlight", {color: 'green'}, 500);
    $('#search_bar').val('').effect("highlight", {color: 'green'}, 500);
    update_filter();
    update_search();
}

/**
 * Bind the requirements table manipulators to the table.
 * Initialize manipulators behaviour.
 * @param requirements_table The requirements table
 */
function init_datatable_manipulators(requirements_table) {
    // Headers extension: Add index to address in search.
    requirements_table.columns().every(function (index) {
        if (index > 0) requirements_table.column(index).header().append(' (' + index + ')');
    });

    // Save button
    $('#save_requirement_modal').click(function () {
        store_requirement(requirements_table);
    });

    // Table Search related stuff.
    // Bind big custom searchbar to search the table.
    $('#search_bar').keypress(function (e) {
        if (e.which === 13) { // Search on enter.
            update_search();
            requirements_table.draw();
        }
    });

    // Table filters.
    $('#type-filter-input').autocomplete({
        minLength: 0,
        source: available_types,
        delay: 100
    });

    $('#status-filter-input').autocomplete({
        minLength: 0,
        source: available_status,
        delay: 100
    });

    $('#tag-filter-input').autocomplete({
        minLength: 0,
        source: available_tags,
        delay: 100
    });

    $('#tag-filter-input, #status-filter-input, #type-filter-input')
        .on('focus', function () {
            $(this).keydown();
        })
        .on('keypress', function (e) {
            if (e.which === 13) { // Search on Enter.
                update_filter();
                requirements_table.draw();
            }
        });

    $('#table-filter-toggle').click(function () {
        $('#tag-filter-input').autocomplete({source: available_tags});
        $('#type-filter-input').autocomplete({source: available_types});
    });

    // Clear all applied searches.
    $('.clear-all-filters').click(function () {
        clear_all_search_filter_inputs();
        requirements_table.draw();
    });

    // Listen for tool section triggers.
    $('#gen-req-from-selection').click(function () {
        let req_ids = [];
        requirements_table.rows({search: 'applied'}).every(function () {
            let d = this.data();
            req_ids.push(d['id']);
        });
        $('#selected_requirement_ids').val(JSON.stringify(req_ids));
        $('#generate_req_form').submit();
    });

    $('#gen-csv-from-selection').click(function () {
        let req_ids = [];
        requirements_table.rows({search: 'applied'}).every(function () {
            let d = this.data();
            req_ids.push(d['id']);
        });
        $('#selected_csv_requirement_ids').val(JSON.stringify(req_ids));
        $('#generate_csv_form').submit();
    });

    $('#gen-xls-from-selection').click(function () {
        let req_ids = [];
        requirements_table.rows({search: 'applied'}).every(function () {
            let d = this.data();
            req_ids.push(d['id']);
        });
        $('#selected_xls_requirement_ids').val(JSON.stringify(req_ids));
        $('#generate_xls_form').submit();
    });

    // Column toggling
    $('.colum-toggle-button').on('click', function (e) {
        e.preventDefault();

        // Get the column API object
        let column = requirements_table.column($(this).attr('data-column'));

        // Toggle the visibility
        column.visible(!column.visible());
        update_visible_columns_information();
    });

    $('.reset-colum-toggle').on('click', function (e) {
        e.preventDefault();
        requirements_table.columns('.default-col').visible(true);
        requirements_table.columns('.extra-col').visible(false);
        update_visible_columns_information();
    });
    update_visible_columns_information();

    // Select rows
    $('.select-all-button').on('click', function () {
        // Toggle selection on
        if ($(this).hasClass('btn-secondary')) {
            requirements_table.rows({page: 'current'}).select();
        } else { // Toggle selection off
            requirements_table.rows({page: 'current'}).deselect();
        }
        // Toggle button state.
        $('.select-all-button').toggleClass('btn-secondary btn-primary');
    });

    // Toggle "Select all rows to `off` on user specific selection."
    requirements_table.on('user-select', function () {
        let select_buttons = $('.select-all-button');
        select_buttons.removeClass('btn-primary');
        select_buttons.addClass('btn-secondary ');
    });

    // Bind autocomplete for "edit-selected" inputs
    $('#multi-add-tag-input, #multi-remove-tag-input').autocomplete({
        minLength: 0,
        source: available_tags,
        delay: 100
    }).on('focus', function () {
        $(this).keydown();
    }).val('');

    $('#multi-set-status-input').autocomplete({
        minLength: 0,
        source: available_status,
        delay: 100
    }).on('focus', function () {
        $(this).keydown();
    }).val('');

    $('.apply-multi-edit').click(function () {
        apply_multi_edit(requirements_table);
    });

    $('.add_top_guess_button').confirmation({
        rootSelector: '.add_top_guess_button'
    }).click(function () {
        add_top_guess_to_selected_requirements(requirements_table);
    });
}

/**
 * Fetch requirements from hanfor api and build the requirements table.
 * Apply search queries to table
 * Bind button/links to events.
 * @param columnDefs predefined columDefs (https://datatables.net/reference/option/columnDefs)
 */
function init_datatable(columnDefs) {
    let table = $('#requirements_table').DataTable({
        "language": {
            "emptyTable": "Loading data."
        },
        "paging": true,
        "stateSave": true,
        "select": {
            style: 'os',
            selector: 'td:first-child'
        },
        "order": [[ 1, "asc" ]],
        "pageLength": 50,
        "lengthMenu": [[10, 50, 100, 500, -1], [10, 50, 100, 500, "All"]],
        "dom": 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        "ajax": "api/req/gets",
        "deferRender": true,
        "columnDefs": columnDefs,
        "createdRow": function (row, data) {
            if (data['type'] === 'Heading') {
                $(row).addClass('bg-primary');
            }
            if (data['type'] === 'Information') {
                $(row).addClass('table-info');
            }
            if (data['type'] === 'Requirement') {
                $(row).addClass('table-warning');
            }
            if (data['type'] === 'not set') {
                $(row).addClass('table-light');
            }
        },
        "infoCallback": function (settings, start, end, max, total) {
            let api = this.api();
            let pageInfo = api.page.info();

            $('#clear-all-filters-text').html("Showing " + total + "/" + pageInfo.recordsTotal + ". Clear all.");

            let result = "Showing " + start + " to " + end + " of " + total + " entries";
            result += " (filtered from " + pageInfo.recordsTotal + " total entries).";

            return result;
        },
        "initComplete": function () {
            $('#search_bar').val(req_search_string);
            $('#type-filter-input').val(filter_type_string);
            $('#tag-filter-input').val(filter_tag_string);
            $('#status-filter-input').val(filter_status_string);

            let requirements_table = this.api();
            bind_requirement_id_to_modals(requirements_table);
            init_datatable_manipulators(requirements_table);

            utils.process_url_query(get_query);
            update_search();
            update_filter();

            // Enable Hanfor specific requirements table filtering.
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
    new $.fn.dataTable.ColReorder(table, {});
}


/**
 * Get the color for a tag
 */
function get_tag_color(tag_name) {
    return tag_colors.hasOwnProperty(tag_name) ? tag_colors[tag_name] : '#5bc0de';
}


/**
 * Load available guesses into the modal.
 */
function fetch_available_guesses() {
    let modal = $('#requirement_guess_modal');
    let available_guesses_cards = $('#available_guesses_cards');
    let modal_content = $('.modal-content');
    let requirement_id = $('#requirement_id').val();

    modal.modal({
        keyboard: false
    });
    modal.modal('show');
    modal_content.LoadingOverlay('show');
    available_guesses_cards.html('');

    function add_available_guess(guess) {
        let template = '<div class="card">' +
            '                    <div class="pl-1 pr-1">' +
            '                        <p>' +
            guess['string'] +
            '                        </p>' +
            '                    </div>' +
            '                    <button type="button" class="btn btn-success btn-sm add_guess"' +
            '                            title="Add formalization"' +
            '                            data-scope="' + guess['scope'] + '"' +
            '                            data-pattern="' + guess['pattern'] + '"' +
            '                            data-mapping=\'' + JSON.stringify(guess['mapping']) + '\'>' +
            '                        <strong>+ Add this formalization +</strong>' +
            '                    </button>' +
            '                </div>';
        available_guesses_cards.append(template);
    }

    $.post("api/req/get_available_guesses",
        {
            requirement_id: requirement_id
        },
        function (data) {
            if (data['success'] === false) {
                alert(data['errormsg'])
            } else {
                for (let i = 0; i < data['available_guesses'].length; i++) {
                    add_available_guess(data['available_guesses'][i]);
                }
            }
        }).done(function () {
        $('.add_guess').click(function () {
            add_formalization_from_guess($(this).data('scope'), $(this).data('pattern'), $(this).data('mapping'));
        });
        modal_content.LoadingOverlay('hide', true);
    });
}


/**
 * Load requirements datatable definitions. Trigger build of a fresh requirement datatable.
 */
function load_datatable() {
    // Initialize the Column defs.
    // First set the static colum definitions.
    let columnDefs = [
        {
            "orderable": false,
            "className": 'select-checkbox',
            "targets": [0],
            "data": null,
            "defaultContent": ""
        },
        {
            "targets": [1],
            "data": "pos"
        },
        {
            "targets": [2],
            "data": "id",
            "render": function (data) {
                return '<a href="#">' + utils.escapeHtml(data) + '</a>';
            }
        },
        {
            "targets": [3],
            "data": "desc",
            "render": function (data) {
                return '<div class="white-space-pre">' + utils.escapeHtml(data) + '</div>';
            }
        },
        {
            "targets": [4],
            "data": "type",
            "render": function (data) {
                if (available_types.indexOf(data) <= -1) {
                    available_types.push(data);
                }
                return utils.escapeHtml(data);
            }
        },
        {
            "targets": [5],
            "data": "tags",
            "render": function (data, type, row) {
                let result = '';
                $(data).each(function (id, tag) {
                    if (tag.length > 0) {
                        result += '<span class="badge" style="background-color: ' + get_tag_color(tag) + '">' +
                            utils.escapeHtml(tag) + '</span></br>';
                        // Add tag to available tags
                        if (available_tags.indexOf(tag) <= -1) {
                            available_tags.push(tag);
                        }
                    }
                });
                if (row.formal.length > 0) {
                    let tagged_formal = false;
                    let tagged_incomplete = false;

                    $.each(row.formal, function (index, formalization) {
                        if ((formalization.length > 0) && (formalization !== '// None, // not formalizable')
                        ) {
                            if (!tagged_formal) {
                                tagged_formal = true;
                                result += '<span class="badge badge-success">has_formalization</span></br>';
                            }
                        } else {
                            if (!tagged_incomplete) {
                                tagged_incomplete = true;
                                result += '<span class="badge badge-warning">incomplete_formalization</span></br>';
                            }
                        }
                    });
                }
                return result;
            }

        },
        {
            "targets": [6],
            "data": "status",
            "render": function (data) {
                return '<span class="badge badge-info">' + data + '</span></br>';
            }
        },
        {
            "targets": [7],
            "data": "formal",
            "render": function (data, type, row) {
                let result = '';
                if (row.formal.length > 0) {
                    $(data).each(function (id, formalization) {
                        if (formalization.length > 0) {
                            result += '<div class="white-space-pre">' + utils.escapeHtml(formalization) + '</div>';
                        }
                    });
                }
                return result;
            }
        }
    ];
    // Load generic colums.
    $.get("api/table/colum_defs", '', function (data) {
        const dataLength = data['col_defs'].length;
        for (let i = 0; i < dataLength; i++) {
            columnDefs.push(
                {
                    "targets": [parseInt(data['col_defs'][i]['target'])],
                    "data": data['col_defs'][i]['csv_name'],
                    "visible": false,
                    "searchable": true
                });
        }
    }).done(function () {
        init_datatable(columnDefs);
    });
}

/**
 * Handle requirement modal hiding event.
 * Prevent hiding on unsaved changes by asking user feedback (discard, save, back to edit).
 * @param event | the modal hiding event.
 */
function modal_closing_routine(event) {
    const unsaved_changes = $('#requirement_modal').data('unsaved_changes');
    if (unsaved_changes === true) {
        const force_close = confirm("You have unsaved changes, do you really want to close?");
        if (force_close !== true) {
            event.preventDefault();
        }
    }
}

/**
 * Initialize the requirement modal behaviour.
 */
function init_modal() {
    let requirement_modal = $('#requirement_modal');
    // Initialize tag autocomplete filed in the requirements modal.
    $('#requirement_tag_field')
        .tokenfield({
            autocomplete: {
                source: available_tags,
                delay: 100
            },
            showAutocompleteOnFocus: true
        })
        .change(function () {
            requirement_modal.data('unsaved_changes', true);
        });

    $('#requirement_status').change(function () {
        $('#requirement_modal').data('unsaved_changes', true);
    });

    requirement_modal.on('hide.bs.modal', function (event) {
        modal_closing_routine(event);
    });

    // Handle ESC key
    $(document).keyup(function (e) {
        // If modal is open and ESC pressed (ESC maps to keyCode "27")
        if ($('.modal:visible').length && e.keyCode === 27) {
            let focused_input = $('input[type=text], textarea, select').filter(":focus");
            // If no input elements in focus => Close modal.
            if (focused_input.length === 0) {
                // First hide the autoguess modal
                if ($('#requirement_guess_modal:visible').length) {
                    $('#requirement_guess_modal').modal('hide');
                } else {
                    $('#requirement_modal').modal('hide');
                }
            } else {
                // Defocus input elements.
                focused_input.each(function () {
                    $(this).blur();
                });
            }
        }
    });

    // Clear the Modal after closing modal.
    // In case of stacked modals and on modal closing:
    // Prevent removal of modal-open class from body if a modal remains. This will keep the scrollbar intact.
    requirement_modal.on('hidden.bs.modal', function () {
        $('#requirement_tag_field').val('');
        $('#requirement_tag_field-tokenfield').val('');
    });

    // Listener for adding new formalizations.
    $('#add_formalization').click(function () {
        add_formalization();
    });

    // Listener for adding new geussed formalizations.
    $('#add_gussed_formalization').click(function () {
        fetch_available_guesses();
    });

    $(".modal").on('hidden.bs.modal', function () {
        if ($('.modal:visible').length) {
            $('body').addClass('modal-open');
        } else {
            $('textarea').each(function () {
                autosize.destroy($(this));
            });
        }
    });

    $('#formalization_accordion').on('shown.bs.collapse', '.card', function () {
        $(this).find('textarea').each(function () {
            autosize($(this));
            autosize.update($(this));
        });
    });

    // Initialize variables.
    update_vars();
}


/**
 * Load the hanfor frontend meta settings.
 */
function load_meta_settings() {
    $.get("api/meta/get", '', function (data) {
        tag_colors = data['tag_colors'];
        available_search_strings = data['available_search_strings'];
        let search_bar = $("#search_bar");
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
    });
}


/**
 * Find the datatable row index for a requirement by its requirement id.
 * @param {number} rid the requirement id.
 * @returns {number} row_index the datatables row index.
 */
function get_rowidx_by_reqid(rid) {
    let requirement_table = $('#requirements_table').DataTable();
    let result = -1;
    requirement_table
        .column(2)
        .data()
        .filter(function (value, index) {
            if (String(value) === String(rid)) {
                result = index;
                return true;
            }
            return false;
        });
    return result;
}


/**
 * Refresh the hanfor frontend logs.
 */
function update_logs() {
    $.get("api/logs/get", '', function (data) {
        $('#log_textarea').html(data);
    }).done(function () {
        // Bind direct requirement links to load the modal.
        $('.req_direct_link').click(function () {
            load_requirement(get_rowidx_by_reqid($(this).data("rid")));
        });
        $('#log_textarea').scrollTop(100000);
    });
}


/**
 * Evaluate the report queries given by the report_query_textarea.
 * Paste the result into the report_results_textarea.
 * @TODO: the .draw() method is potentially overkill, since it will render the whole datatable.
 * So look into callstack and only apply necessary steps to evaluate the new search tree.
 * (.search() would not work since we use our own plugin to support the search expression parsing.)
 */
function evaluate_report() {
    let body = $('body');
    body.LoadingOverlay('show');
    const report_querys = $('#report_query_textarea').val().split('\n');
    let reqTable = $('#requirements_table').DataTable();
    let results = '';
    const regex = /^(:NAME:)(`(\w+)`)(.*)/;
    try {
        $.each(report_querys, function (id, report_query) {
            // Test if there is a named query.
            let match = regex.exec(report_query);
            if (match != null) {
                report_query = match[4];
                id = match[3];
            }
            search_tree = SearchNode.fromQuery(report_query);
            reqTable.draw();
            let result = reqTable.page.info();
            results += `"${id}":\t${result.recordsDisplay}\n`;
        });
        $('#report_results_textarea').val(results).change();
        update_search();
        reqTable.draw();
    } catch (err) {
        alert(err);
    }
    body.LoadingOverlay('hide', true);
}

function load_reports() {
    $.get("api/report/get", {},
        function (data) {
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                let result = '';
                available_reports = data.data;
                $.each(data.data, function (id, report) {
                    result += `<div class="card border-primary">
                              <div class="card-body">
                                <h5 class="card-title">${report.name}</h5>
                                <h6 class="card-subtitle mb-2 text-muted">Query</h6>
                                <p class="card-text report-results">${report.queries}</p>
                                <h6 class="card-subtitle mb-2 text-muted">Matches for queries</h6>
                                <p class="card-text report-results">${report.results}</p>
                                <a href="#" class="card-link open-report" data-id="${id}">
                                    Edit (reevaluate) Report.
                                </a>
                                <a href="#" class="card-link delete-report" data-id="${id}">Delete Report.</a>
                              </div>
                            </div>`;
                });
                $('#available_reports').html(result);
            }
        });
}

function save_report() {
    let body = $('body');
    body.LoadingOverlay('show');

    $.post("api/report/set",
        {
            report_querys: $('#report_query_textarea').val(),
            report_results: $('#report_results_textarea').val(),
            report_name: $('#report_name').val(),
            report_id: $('#save_report').attr('data-id')
        },
        function (data) {
            body.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            }
            load_reports();
        });
}

function delete_report(id) {
    $.ajax({
        type: "DELETE",
        url: "api/report/delete",
        data: {report_id: id},
        success: function (data) {
            if (data['success'] === false) {
                alert(data['errormsg']);
            }
            load_reports();
        }
    });
}

function open_report_modal(source = false) {
    let query_textarea = $('#report_query_textarea');
    let results_textarea = $('#report_results_textarea');
    let report_title = $('#report_modal_title');
    let report_name = $('#report_name');
    let queries = '';
    let results = '';
    let name = '';
    let report_id = -1;
    let report_modal = $('#report_modal');
    if (source !== false) {
        report_id = source.attr('data-id');
        queries = available_reports[report_id].queries;
        results = available_reports[report_id].results;
        name = available_reports[report_id].name;
    }
    query_textarea.val(queries).change();
    results_textarea.val(results).change();
    report_name.val(name).change();
    report_title.html(name);
    $('#save_report').attr('data-id', report_id);
    report_modal.modal('show');
}

/**
 * Listen on click events to add and eval a report.
 */
function init_report_generation() {
    $('#add-new-report').click(function () {
        open_report_modal();
    });
    $('#eval_report').click(function () {
        evaluate_report();
    });
    $('#save_report').click(function () {
        save_report();
    });
    let av_reports = $('#available_reports');
    av_reports.on('click', '.open-report', function () {
        open_report_modal($(this));
    });
    av_reports.on('click', '.delete-report', function () {
        delete_report($(this).attr('data-id'));
    });
    $('#report_name').change(function () {
        $('#report_modal_title').html($(this).val());
    });
    load_reports();
}


/**
 * Start the app.
 */
$(document).ready(function () {
    load_meta_settings();
    load_datatable();
    init_modal();
    update_logs();
    init_report_generation();
    init_simulator_tab();

    let body = $('body');
    // Bind formalization deletion.
    body.confirmation({
        rootSelector: '.delete_formalization',
        selector: '.delete_formalization',
        onConfirm: function () {
            delete_formalization($(this).attr('name'), $(this).closest('.card'));
        }
    });

    // Bind formalization update.
    body.on('change', '.formalization_selector, .reqirement-variable, .req_var_type', function () {
        update_formalization();
    });
    // Bind formalization variable update.
    body.on('change', '.formalization_selector', function () {
        update_vars();
    });
    body.on('shown.bs.modal', '#requirement_modal', function () {
        $(this).find('textarea').each(function () {
            autosize($(this));
            autosize.update($(this));
        });
    });
    body.on('change focus', 'textarea', function () {
        autosize($(this));
        autosize.update($(this));
    });
});
