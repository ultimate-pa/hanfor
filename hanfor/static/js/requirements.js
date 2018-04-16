require('gasparesganga-jquery-loading-overlay');
require('bootstrap');
require('bootstrap-confirmation2');
require('datatables.net-bs4');
require('datatables.net-select');
require('jquery-ui/ui/widgets/autocomplete');
require('./bootstrap-tokenfield.js');

// Globals
let available_tags = ['', 'has_formalization'];
let available_status = ['', 'Todo', 'Review', 'Done'];
let available_types = [''];
let available_vars = [''];
let visible_columns = [true, true, true, true, true, true];
let search_tree = undefined;
let filter_tree = undefined;
let get_query = JSON.parse(search_query); // search_query is set in index.html
let type_inference_errors = [];

// Search query grammar declarations.
const operators = {":AND:": 1, ":OR:": 1};
const leftAssoc = {":AND:": 1, ":OR:": 1};
const rightAssoc = {};
const parantheses = {"(": 1, ")": 1};
const precedenceOf = {":AND:": 3, ":OR:": 2};

/**
 * SearchNode represents one node in a search expression used to filter the requirements table.
 */
class SearchNode {
    constructor(value) {
        this.left = false;
        this.value = value;
        this.right = false;
        this.col_target = -1;
        this.update_target();
    }

    update_target() {
        const col_string_index = this.value.indexOf(':COL_INDEX_');
        if (col_string_index >= 0) {
            const target_index = parseInt(this.value.substring(col_string_index + 11, col_string_index + 13));
            if (target_index >= 0) {
                this.value = this.value.substring(col_string_index + 14);
                this.col_target = target_index;
            }
        }
    }

    static is_search_string(token) {
        return !(token in parantheses || token in operators);
    }

    static to_string(tree) {
        let repr = '';
        if (tree.left !== false) {
            repr += SearchNode.to_string(tree.left) + ' ';
        }
        repr += tree.value;
        if (tree.right !== false) {
            repr += ' ' + SearchNode.to_string(tree.right);
        }
        return repr;
    }

    static peek(array) {
        return array[array.length - 1];
    }

    /**
     * Parses a search array to a binary search tree using shunting yard algorithm.
     * @param array
     * @returns {*}
     */
    static searchArrayToTree(array) {

        let output_tree_stack = [], op_stack = [];

        for (let i = 0, length = array.length; i < length;  i++) {
            const token = array[i]; // current token

            // If token is a search string, add it to the output_tree_stack as a singleton tree.
            if (SearchNode.is_search_string(token))
                output_tree_stack.push(new SearchNode(token));

            else if (token in operators) {
                // We encountered an operator.
                while (op_stack.length) {
                    // As long as there is an operator (prev_op) at the top of the op_stack
                    const prev_op = SearchNode.peek(op_stack);
                    if (prev_op in operators && (
                            // and token is left associative and precedence <= to that of prev_op,
                            (token in leftAssoc &&
                                (precedenceOf[token] <= precedenceOf[prev_op])) ||
                            // or token is right associative and its precedence < to that of prev_op,
                            (token in rightAssoc &&
                                (precedenceOf[token] < precedenceOf[prev_op]))
                        )) {
                        // Pop last two subtrees and make them children of a new subtree (with prev_op as root).
                        let right = output_tree_stack.pop(), left = output_tree_stack.pop();
                        let sub_tree = new SearchNode(op_stack.pop());
                        sub_tree.left = left;
                        sub_tree.right = right;
                        output_tree_stack.push(sub_tree);
                    } else {
                        break;
                    }
                }
                op_stack.push(token);
            }

            // If token is opening parenthesis, just push to the op_stack.
            else if (token === "(")
                op_stack.push(token);

            // If token is closing parenthesis:
            else if (token === ")") {

                let has_opening_match = false;

                // Search for opening paranthesis in op_stack.
                while (op_stack.length) {
                    const op = op_stack.pop();
                    if (op === "(") {
                        has_opening_match = true;
                        break;
                    } else {
                        // Until match pop operators off the op_stack and create a new subtree with operator as root.
                        let right = output_tree_stack.pop();
                        let left = output_tree_stack.pop();
                        let sub_tree = new SearchNode(op);
                        sub_tree.left = left;
                        sub_tree.right = right;
                        output_tree_stack.push(sub_tree);
                    }
                }
                if (!has_opening_match)
                    throw "Error: parentheses mismatch.";
            }
            else throw "Error: Token unknown: " + token;
        }

        // No more tokens in input but operator tokens in the op_stack:
        while (op_stack.length) {

            const op = op_stack.pop();

            if (op === "(" || op === ")")
                throw "Error: Parentheses mismatch.";

            // Create new subtree with op as root.
            let right = output_tree_stack.pop();
            let left = output_tree_stack.pop();
            let sub_tree = new SearchNode(op);
            sub_tree.left = left;
            sub_tree.right = right;
            output_tree_stack.push(sub_tree);
        }

        // The last remaining node should be the root of our complete search tree.
        return output_tree_stack[0];
    }

    /**
     * Splits a search query into array where each element is one token.
     * @param query
     * @param target_col optional target col to restrict the search on a specific col.
     * @returns {*|string[]}
     */
    static awesomeQuerySplitt0r(query, target_col=undefined) {
        // Split by :AND:
        let result = query.split(/(:OR:|:AND:|\(|\))/g);
        result = result.filter(String); // Remove empty elements.
        // If the resulting tree should be restricted to a col..
        if (target_col !== undefined) {
            for (let i = 0, length = result.length; i < length;  i++) {
                // Add :COL_INDEX_<target_col>: to each search string (not a operator or parenthesis).
                if (!(result[i] in operators || result[i] in parantheses)) {
                    result[i] = ':COL_INDEX_' + ("00" + target_col).slice(-2) + ':' + result[i];
                }
            }
        }
        return result;
    }

    /**
     * Create a Search Tree from search query.
     * @param query
     * @param target_col optional target col to restrict the search on a specific col.
     * @returns {*}
     */
    static fromQuery(query, target_col=undefined) {
        return SearchNode.searchArrayToTree(SearchNode.awesomeQuerySplitt0r(query, target_col));
    }

}

/**
 * Check is value is in string. Support `"` for exact and `""` padding for exclusive match.
 * @param value string to be converted to regex and matched agains string.
 * @param string
 * @returns {boolean}
 */
function check_value_in_string(value, string) {
    // We support value to be `
    //  * "<inner>"` for exact match.
    //  * ""<inner>"" for exclusive match.

    if (value.startsWith('""') && value.endsWith('""')) {
        value = '^\\s*' + value.substr(2, (value.length - 4)) + '\\s*$';
    } else {
        // replace " by \b to allow for exact matches.
        // In the input we escaped " by \" so we would like to apply (?<!\\)\"
        // since javascript does not allow negative look behinds we do
        // something like ([^\\])(\") and replace the 2. group by \b but keeping \" intact.
        value = value.replace(/([^\\])?\"/g, "$1\\b");
    }

    const regex = new RegExp(value, "i");
    return regex.test(string);

}

/**
 * Apply a search expression tree on row data.
 * @param tree
 * @param data
 * @returns {bool}
 */
function evaluateSearchExpressionTree(tree, data) {
    // Root node
    if (tree === undefined) {
        return true;
    }

    // Leaf node.
    if (tree.left === false && tree.right === false) {
        // First build the string to search.
        let string = '';
        // We have a specific target.
        if (tree.col_target !== -1) {
            string = data[tree.col_target];
        } else {
            // We search in all visible columns.
            for (let i = 0; i < visible_columns.length; i++) {
                if (visible_columns[i]) {
                    string += data[i] + ' ';
                }
            }
        }
        const not_index = tree.value.indexOf(':NOT:');
        if (not_index >= 0) { // Invert search on :NOT: keyword.
            return !check_value_in_string(tree.value.substring(not_index + 5), string);
        } else {
            return check_value_in_string(tree.value, string);
        }
    }

    // evaluate left tree
    let left_sub = evaluateSearchExpressionTree(tree.left, data);

    // evaluate right tree
    let right_sub = evaluateSearchExpressionTree(tree.right, data);

    // Apply operations
    if (tree.value === ':AND:') {
        return (left_sub && right_sub);
    }

    if (tree.value === ':OR:') {
        return (left_sub || right_sub);
    }
}


/**
 * Hanfor specific requirements table filtering.
 * In user search queries we use:
 * -> :OR: and :AND: to concatenate queries.
 * -> " to indicate the beginning or end of a search sequence.
 */
$.fn.dataTable.ext.search.push(
    function( settings, data, dataIndex ) {
        // data contains the row. data[0] is the content of the first column in the actual row.
        // Return true to include the row into the data. false to exclude.
        return evaluateSearchExpressionTree(search_tree, data) && evaluateSearchExpressionTree(filter_tree, data);
    }
);

/**
 * Update the search expression tree.
 */
function update_search_tree() {
    search_tree = SearchNode.fromQuery($('#search_bar').val().trim());
}

/**
 * Update the filter search tree used to filter the table by the values from the Filter tab.
 */
function update_filter_tree() {
    let search_array = [];
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
    search_array = add_query(search_array, $('#type-filter-input').val(), 4);
    search_array = add_query(search_array, $('#tag-filter-input').val(), 5);
    search_array = add_query(search_array, $('#status-filter-input').val(), 6);

    filter_tree = SearchNode.searchArrayToTree(search_array);
}


/**
 * Apply a URL search query to the requirements table.
 * @param requirements_table
 * @param get_query
 */
function process_url_query(requirements_table, get_query) {
    // Clear old search.
    requirements_table.search( '' ).columns().search( '' );
    // Apply search if we have one.
    if (get_query.q.length > 0) {
        requirements_table
            .columns( Number(get_query.col) )
            .search( '^' + get_query.q + '$', true, false);
    }
    // Draw the table.
    requirements_table.draw();
}

/**
 * Stores the active (in modal) requirement and updates the row in the requirements table.
 * @param {DataTable} requirements_table
 */
function store_requirement(requirements_table) {
    requirement_modal_content = $('.modal-content');
    requirement_modal_content.LoadingOverlay('show');

    req_id = $('#requirement_id').val();
    req_tags = $('#requirement_tag_field').val();
    req_status = $('#requirement_status').val();
    selected_scope = $('#requirement_scope').val();
    selected_pattern = $('#requirement_pattern').val();
    updated_formalization = $('#requirement_formalization_updated').val();
    associated_row_id = parseInt($('#modal_associated_row_index').val());

    // Fetch the formalizations
    let formalizations = {};
    $('.formalization_card').each(function ( index ) {
        // Scope and Pattern
        let formalization = {};
        formalization['id'] = $(this).attr('title');
        $( this ).find( 'select').each( function () {
            if ($( this ).hasClass('scope_selector')) {
                formalization['scope'] = $( this ).val();
            }
            if ($( this ).hasClass('pattern_selector')) {
                formalization['pattern'] = $( this ).val();
            }
        });

        // Expressions
        formalization['expression_mapping'] = {};
        $( this ).find( 'input' ).each(function () {
            formalization['expression_mapping'][$(this).attr('title')] = $(this).val();
        });

        formalizations[formalization['id']] = formalization;
    });

    // Store the requirement.
    $.post( "api/req/update",
        {
            id: req_id,
            update_formalization: updated_formalization,
            tags: req_tags,
            status: req_status,
            formalizations: JSON.stringify(formalizations)
        },
        // Update requirements table on success or show an error message.
        function( data ) {
            requirement_modal_content.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                requirements_table.row(associated_row_id).data(data).draw();
                $('#requirement_modal').modal('hide');
            }
    });
}

function apply_multi_edit(requirements_table) {
    let page = $('body');
    page.LoadingOverlay('show');
    let add_tag = $('#multi-add-tag-input').val().trim();
    let remove_tag = $('#multi-remove-tag-input').val().trim();
    let set_status = $('#multi-set-status-input').val().trim();
    let selected_ids = [];
    requirements_table.rows( {selected:true} ).every( function () {
        let d = this.data();
        selected_ids.push(d['id']);
    } );

    // Store the requirement.
    $.post( "api/req/multi_update",
        {
            add_tag: add_tag,
            remove_tag: remove_tag,
            set_status: set_status,
            selected_ids: JSON.stringify(selected_ids)
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
        $( this ).removeClass('type-error');
    });

    $('.formalization_card').each(function ( index ) {
        // Fetch attributes
        formalization_id = $(this).attr('title');
        selected_scope = $('#requirement_scope' + formalization_id).val();
        selected_pattern = $('#requirement_pattern' + formalization_id).val();
        header = $('#formalization_heading' + formalization_id);
        var_p = $('#requirement_var_group_p' + formalization_id);
        var_q = $('#requirement_var_group_q' + formalization_id);
        var_r = $('#requirement_var_group_r' + formalization_id);
        var_s = $('#requirement_var_group_s' + formalization_id);
        var_t = $('#requirement_var_group_t' + formalization_id);
        var_u = $('#requirement_var_group_u' + formalization_id);

        // Set the red boxes for type inference failed expressions.
        if (formalization_id in type_inference_errors) {
            for (let i = 0; i < type_inference_errors[formalization_id].length; i++) {
                window['var_' + type_inference_errors[formalization_id][i]].addClass('type-error');
                header.addClass('type-error-head');
            }
        } else {
            header.removeClass('type-error-head');
        }

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
        formalization_id = $(this).attr('title');

        formalization = '';
        selected_scope = $('#requirement_scope' + formalization_id).find('option:selected').text().replace(/\s\s+/g, ' ');
        selected_pattern = $('#requirement_pattern' + formalization_id).find('option:selected').text().replace(/\s\s+/g, ' ');

        if (selected_scope !== 'None' && selected_pattern !== 'None') {
            formalization = selected_scope + ', ' + selected_pattern + '.';
        }

        // Update formalization with variables.
        var_p = $('#formalization_var_p' + formalization_id).val();
        var_q = $('#formalization_var_q' + formalization_id).val();
        var_r = $('#formalization_var_r' + formalization_id).val();
        var_s = $('#formalization_var_s' + formalization_id).val();
        var_t = $('#formalization_var_t' + formalization_id).val();
        var_u = $('#formalization_var_u' + formalization_id).val();

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
    });
    $('#requirement_formalization_updated').val('true');
}

/**
 * Extract the last term in an expression string.
 * @param {string} term an expression.
 * @returns {string}
 */
function extractLast( term ) {
    last_term = term.split( / \s*/ ).pop();
    last_term = last_term.replace(/^[!\(\[\{]/g, '');
    return last_term;
}


function sort_pattern_by_guess(reset) {
    requirement_modal_content = $('.modal-content');
    requirement_modal_content.LoadingOverlay('show');
    req_id = $('#requirement_id').val();

    // Get predicted scope and pattern for the requirement.
    $.post( "api/req/predict_pattern",
        {
            id: req_id,
            reset: reset
        },
        function( data ) {
            requirement_modal_content.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                $('#requirement_scope').html(data['scopes']);
                $('#requirement_pattern').html(data['patterns']);
            }
    });
}


function add_formalization() {
    // Request a new Formalization. And add its edit elements to the modal.
    requirement_modal_content = $('.modal-content');
    requirement_modal_content.LoadingOverlay('show');

    req_id = $('#requirement_id').val();
    $.post( "api/req/new_formalization",
        {
            id: req_id
        },
        function( data ) {
            requirement_modal_content.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                $('#formalization_accordion').append(data['html']);
            }
    }).done(function () {
        update_vars();
        update_formalization();
        bind_expression_buttons();
        bind_var_autocomplete();
    });
}


function delete_formalization(formal_id) {
    requirement_modal_content = $('.modal-content');
    requirement_modal_content.LoadingOverlay('show');
    req_id = $('#requirement_id').val();
    $.post( "api/req/del_formalization",
        {
            requirement_id: req_id,
            formalization_id: formal_id
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
        bind_var_autocomplete();
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
        delete_formalization( $(this).attr('name') );
    });
}


/**
 * Bind autocomplete trigger to formalization input fields.
 * Implement autocomplete.
 *
 */
function bind_var_autocomplete() {
    $( ".reqirement-variable" )
        // don't navigate away from the field on tab when selecting an item
        .on( "keydown", function( event ) {
            if ( event.keyCode === $.ui.keyCode.TAB &&
                    $( this ).autocomplete( "instance" ).menu.active ) {
                event.preventDefault();
            }
        })
        .autocomplete({
            minLength: 0,
            source: function( request, response ) {
                // delegate back to autocomplete, but extract the last term
                response( $.ui.autocomplete.filter(
                available_vars, extractLast( request.term ) ) );
            },
            focus: function() {
                // prevent value inserted on focus
                return false;
            },
            select: function( event, ui ) {
                let terms = ( this.value.split(/ \s*/) );
                // remove the current input
                current_input = terms.pop();
                // If our input starts with one of [!, (, [, {]
                // we assume this should be in front of the input.
                selected_item = ui.item.value;
                const searchPattern = new RegExp(/^[!\(\[\{]/g);
                if (searchPattern.test(current_input)) {
                    selected_item = current_input.charAt(0) + selected_item;
                }
                // add the selected item
                terms.push( selected_item );
                // add placeholder to get the space at the end
                terms.push( "" );
                this.value = terms.join( " " );
                return false;
            }
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

        // Get row data
        let data = requirements_table.row($(event.target).parent()).data();
        let row_id = requirements_table.row($(event.target).parent()).index();

        // Prepare requirement Modal
        requirement_modal_content = $('.modal-content');
        $('#requirement_modal').modal('show');
        requirement_modal_content.LoadingOverlay('show');
        $('#formalization_accordion').html('');

        // Set available tags.
        $('#requirement_tag_field').data('bs.tokenfield').$input.autocomplete({source: available_tags});

        // Get the requirement data and set the modal.
        requirement = $.get( "api/req/get", { id: data['id']}, function (data) {
            // Meta information
            $('#requirement_id').val(data.id);
            $('#requirement_formalization_updated').val('false');
            $('#modal_associated_row_index').val(row_id);
            available_vars = data.available_vars;
            type_inference_errors = data.type_inference_errors;
            // Visible information
            $('#requirement_modal_title').html(data.id + ': ' + data.type);
            $('#description_textarea').text(data.desc);

            // Parse the formalizations
            $('#formalization_accordion').html(data.formalizations_html);

            $('#requirement_scope').val(data.scope);
            $('#requirement_pattern').val(data.pattern);

            // Set the tags
            $('#requirement_tag_field').tokenfield('setTokens', data.tags);
            $('#requirement_status').val(data.status);

            // Set csv_data
            csv_row_content = $('#csv_content_accordion');
            csv_row_content.html('');
            csv_row_content.collapse('hide');
            let csv_data = data.csv_data;
            for(const key in csv_data){
                if (csv_data.hasOwnProperty(key)){
                    const value = csv_data[key];
                    csv_row_content.append('<p><strong>' + key + ':</strong>' + value + '</p>');
                }
            }
            if (data.success === false) {
                alert('Could Not load the Requirement: ' + data.errormsg);
            }
        } ).done(function () {
            // Update visible Vars.
            update_vars();
            // Handle autocompletion for variables.
            bind_var_autocomplete();
            // Update available vars based on the selection of requirement and pattern.
            bind_expression_buttons();
            requirement_modal_content.LoadingOverlay('hide', true);
        });
    } );
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
    $.each(requirements_table.columns().visible(), function(key, value) {
        if(value === false){
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
 * Bind the requirements table manipulators to the table.
 * Initialize manipulators behaviour.
 * @param requirements_table The requirements table
 */
function init_datatable_manipulators(requirements_table) {
    // Headers extension: Add index to address in search.
    requirements_table.columns().every( function ( index ) {
        if (index > 0) requirements_table.column( index ).header().append(' (' + index + ')');
    } );

    // Save button
    $('#save_requirement_modal').click(function () {
        store_requirement(requirements_table);
    });

    // Table Search related stuff.
    // Bind big custom searchbar to search the table.
    $('#search_bar').keypress(function(e) {
        if(e.which === 13) { // Search on enter.
            update_search_tree();
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
        .on('focus', function() { $(this).keydown(); })
        .on('keypress', function (e) {
            if (e.which === 13) { // Search on Enter.
                update_filter_tree();
                requirements_table.draw();
            }
        });

    $('#table-filter-toggle').click(function () {
        $('#tag-filter-input').autocomplete({source: available_tags});
        $('#type-filter-input').autocomplete({source: available_types});
    });

    // Clear all applied searches.
    $('.clear-all-filters').click(function () {
        $('#status-filter-input').val('').effect("highlight", {color: 'green'}, 500);
        $('#tag-filter-input').val('').effect("highlight", {color: 'green'}, 500);
        $('#type-filter-input').val('').effect("highlight", {color: 'green'}, 500);
        $('#search_bar').val('').effect("highlight", {color: 'green'}, 500);
        search_tree = undefined;
        filter_tree = undefined;
        requirements_table.search( '' ).columns().search( '' ).draw();
    });

    // Listen for tool section triggers.
    $('#gen-req-from-selection').click(function () {
        req_ids = [];
        requirements_table.rows( {search:'applied'} ).every( function () {
            let d = this.data();
            req_ids.push(d['id']);
         } );
        $('#selected_requirement_ids').val(JSON.stringify(req_ids));
        $('#generate_req_form').submit();
    });

    $('#gen-csv-from-selection').click(function () {
        req_ids = [];
        requirements_table.rows( {search:'applied'} ).every( function () {
            let d = this.data();
            req_ids.push(d['id']);
         } );
        $('#selected_csv_requirement_ids').val(JSON.stringify(req_ids));
        $('#generate_csv_form').submit();
    });

    // Sort the pattern and scope by guess (toggle on/off).
    $('#sort_by_guess').click(function () {
        if ($( this ).hasClass("btn-secondary")) { // sort by guesss.
            sort_pattern_by_guess();
            $( this ).removeClass("btn-secondary").addClass("btn-success").text("On");
        } else { // Back to normal sorting.
            $( this ).removeClass("btn-success").addClass("btn-secondary").text("Off");
            sort_pattern_by_guess(reset=true);
        }
    });

    // Column toggling
    $('.colum-toggle-button').on( 'click', function (e) {
        e.preventDefault();

        // Get the column API object
        let column = requirements_table.column($(this).attr('data-column'));

        // Toggle the visibility
        state = column.visible( ! column.visible() );
        update_visible_columns_information();
    } );
    $('.reset-colum-toggle').on('click', function (e) {
        e.preventDefault();
        requirements_table.columns( '.default-col' ).visible( true );
        requirements_table.columns( '.extra-col' ).visible( false );
        update_visible_columns_information();
    });
    update_visible_columns_information();

    // Select rows
    $('.select-all-button').on('click', function (e) {
        // Toggle selection on
        if ($( this ).hasClass('btn-secondary')) {
            requirements_table.rows( {page:'current'} ).select();
        }
        else { // Toggle selection off
            requirements_table.rows( {page:'current'} ).deselect();
        }
        // Toggle button state.
        $('.select-all-button').toggleClass('btn-secondary btn-primary');
    });

    // Toggle "Select all rows to `off` on user specific selection."
    requirements_table.on( 'user-select', function ( ) {
        let select_buttons = $('.select-all-button');
        select_buttons.removeClass('btn-primary');
        select_buttons.addClass('btn-secondary ');
    });

    // Bind autocomplete for "edit-selected" inputs
    $('#multi-add-tag-input, #multi-remove-tag-input').autocomplete({
        minLength: 0,
        source: available_tags,
        delay: 100
    }).on('focus', function() { $(this).keydown(); }).val('');

    $('#multi-set-status-input').autocomplete({
        minLength: 0,
        source: available_status,
        delay: 100
    }).on('focus', function() { $(this).keydown(); }).val('');

    $('.apply-multi-edit').click(function () {
        apply_multi_edit(requirements_table);
    });
}

/**
 * Fetch requirements from hanfor api and build the requirements table.
 * Apply search queries to table
 * Bind button/links to events.
 * @param columnDefs predefined columDefs (https://datatables.net/reference/option/columnDefs)
 */
function init_datatable(columnDefs) {
    requirements_table = $('#requirements_table').DataTable({
        "language": {
          "emptyTable": "Loading data."
        },
        "paging": true,
        "stateSave": true,
        "select": {
            style:    'os',
            selector: 'td:first-child'
        },
        "pageLength": 50,
        "lengthMenu": [[10, 50, 100, 500, -1], [10, 50, 100, 500, "All"]],
        "dom": 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        "ajax": "api/req/gets",
        "deferRender": true,
        "columnDefs": columnDefs,
        "createdRow": function( row, data, dataIndex ) {
            if (data['type'] === 'Heading') {
                $(row).addClass( 'bg-primary' );
            }
            if (data['type'] === 'Information') {
                $(row).addClass( 'table-info' );
            }
            if (data['type'] === 'Requirement') {
                $(row).addClass( 'table-warning' );
            }
            if (data['type'] === 'not set') {
                $(row).addClass( 'table-light');
            }
        },
        initComplete : function() {
            $('#search_bar').val('');
            bind_requirement_id_to_modals(requirements_table);
            init_datatable_manipulators(requirements_table);
            // Process URL search query.
            process_url_query(requirements_table, get_query);
        }
    });
}


/**
 * Load requirements datatable definitions. Trigger build of a fresh requirement datatable.
 */
function load_datatable(){
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
            "render": function (data, type, row, meta) {
                result = '<a href="#">' + data + '</a>';
                return result;
            }
        },
        {
            "targets": [3],
            "data": "desc"
        },
        {
            "targets": [4],
            "data": "type",
            "render": function (data, type, row, meta) {
                if (available_types.indexOf(data) <= -1) {
                    available_types.push(data);
                }
                return data;
            }
        },
        {
            "targets": [5],
            "data": "tags",
            "render": function (data, type, row, meta) {
                result = '';
                $(data).each(function (id, tag) {
                    if (tag.length > 0) {
                        result += '<span class="badge badge-info">' + tag + '</span></br>';
                        // Add tag to available tags
                        if (available_tags.indexOf(tag) <= -1) {
                            available_tags.push(tag);
                        }
                    }
                });
                if (row.formal.length > 0) {
                    result += '<span class="badge badge-success">has_formalization</span></br>';
                }
                return result;
            }

        },
        {
            "targets": [6],
            "data": "status",
            "render": function (data, type, row, meta) {
                result = '<span class="badge badge-info">' + data + '</span></br>';
                return result;
            }
        }
    ];
    // Load generic colums.
    genericColums = $.get( "api/table/colum_defs", '', function (data) {
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
 * Initialize the requirement modal behaviour.
 */
function init_modal() {
    // Initialize tag autocomplete filed in the requirements modal.
    $('#requirement_tag_field').tokenfield({
      autocomplete: {
        source: available_tags,
        delay: 100
      },
      showAutocompleteOnFocus: true
    });

    // Clear the Modal after closing modal.
    $('#requirement_modal').on('hidden.bs.modal', function (e) {
        $('#requirement_tag_field').val('');
        $('#requirement_tag_field-tokenfield').val('');
    });

    // Listener for adding new formalizations.
    $('#add_formalization').click(function () {
        add_formalization();
    });

    // Initialize variables.
    update_vars();
}

/**
 * Start the app.
 */
$(document).ready(function() {
    load_datatable();
    init_modal();
});