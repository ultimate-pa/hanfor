// Globals
var available_tags = ['', 'has_formalization'];
var available_status = ['', 'Todo', 'Review', 'Done'];
var available_types = [''];
var available_vars = [''];
var visible_columns = [true, true, true, true, true, true];

var get_query = JSON.parse(search_query);

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

        // Get the search query.
        query = $('#search_bar').val().trim();
        // Shortcut for empty query.
        if (query.length === 0) {
            return true;
        }

        // If the search query is enclosed by ""<query"" the user would like to exclusively match cells with query.
        // No additional content should be in the cell. So query should match ^\s*<query>\s*$
        if (query.startsWith('""') && query.endsWith('""')) {
            query = '^\\s*' + query.substr(2, (query.length - 4)) + '\\s*$';
        }

        // Split by :OR:
        processed_query = '';
        or_parts = query.split(':OR:');

        for (var i = 0; i < or_parts.length; i++) {
            if (i > 0) {
                processed_query += '|('; // Concatenate by | to implement ":OR:" behaviour
            } else {
                processed_query += '(';
            }

            // Each :OR: part is allowed to contain :AND: parts.
            and_parts = or_parts[i].split(':AND:');
            for (var j = 0; j < and_parts.length; j++) {
                processed_query += "(?=.*";  // wrap ":AND:" into (?=.*<query>) to implement intersection behaviour.
                processed_query += and_parts[j].trim();
                processed_query += ")";
            }

            processed_query += ')';
        }


        // replace " by \b to allow for exact matches.
        // In the input we escaped " by \" so we would like to apply (?<!\\)\"
        // since javascript does not allow negative look behinds we do
        // something like ([^\\])(\") and replace the 2. group by \b but keeping \" intact.
        processed_query = processed_query.replace(/([^\\])\"/g, "$1\\b");
        // Search query to regex
        var query_re = new RegExp(processed_query, "i");

        // Loop through all colums and apply search for the visible ones.
        for (var i = 0; i < visible_columns.length; i++) {
            if (visible_columns[i]) { // col visible
                // Check if regex matches col.
                if (query_re.test(data[i])) {
                    return true;  // We return on the first match.
                }
            }
        }

        return false;
    }
);


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
    var formalizations = {};
    $('.formalization_card').each(function ( index ) {
        // Scope and Pattern
        var formalization = {};
        formalization['id'] = $(this).attr('title');
        $( this ).find( 'select').each( function () {
            if ($( this ).hasClass('scope_selector')) {
                formalization['scope'] = $( this ).val();
            }
            if ($( this ).hasClass('pattern_selector')) {
                formalization['pattern'] = $( this ).val();
            }
        });

        // Expresions
        formalization['expression_mapping'] = {};
        $( this ).find( 'input' ).each(function () {
            formalization['expression_mapping'][$(this).attr('title')] = $(this).val();
        });

        formalizations[formalization['id']] = formalization;
    });
    console.log(formalizations);

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

/**
 * Enable/disable the active variables (P, Q, R, ...) in the requirement modal based on scope and pattern.
 */
function update_vars() {
    $('.requirement_var_group').each(function () {
        $( this ).hide();
    });

    $('.formalization_card').each(function ( index ) {
        // Fetch attributes
        formalization_id = $(this).attr('title');
        selected_scope = $('#requirement_scope' + formalization_id).val();
        selected_pattern = $('#requirement_pattern' + formalization_id).val();
        var_p = $('#requirement_var_group_p' + formalization_id);
        var_q = $('#requirement_var_group_q' + formalization_id);
        var_r = $('#requirement_var_group_r' + formalization_id);
        var_s = $('#requirement_var_group_s' + formalization_id);
        var_t = $('#requirement_var_group_t' + formalization_id);
        var_u = $('#requirement_var_group_u' + formalization_id);

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
                var_r.show();
                var_s.show();
                var_t.show();
                break;
            case 'ConstrainedChain':
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
                var terms = ( this.value.split( / \s*/ ) );
                // remove the current input
                current_input = terms.pop();
                // If our input starts with one of [!, (, [, {]
                // we assume this should be in front of the input.
                selected_item = ui.item.value;
                var searchPattern = new RegExp(/^[!\(\[\{]/g);
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
        var data = requirements_table.row( $(event.target).parent() ).data();
        var row_id = requirements_table.row( $(event.target).parent() ).index();

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
            var csv_data = data.csv_data;
            for(var key in csv_data){
                if (csv_data.hasOwnProperty(key)){
                    var value = csv_data[key];
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
    var requirements_table = $('#requirements_table').DataTable();
    var new_visible_columns = [];
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
    // Save button
    $('#save_requirement_modal').click(function () {
        store_requirement(requirements_table);
    });

    // Table Search related stuff.
    // Bind big custom searchbar to search the table.
    $('#search_bar').keypress(function(e) {
        if(e.which === 13) { // Search on enter.
            requirements_table.draw();
        }
    });

    // Table filters.
    $('#type-filter-input').autocomplete({
    minLength: 0,
    source: available_types,
    delay: 100
    })
        .on('focus', function() { $(this).keydown(); })
        .on('autocompleteselect', function(event, ui){
            requirements_table.columns( 3 ).search( ui.item['value'] ).draw() ;
        })
        .on('keypress', function (e) {
            if (e.which === 13) { // Search on Enter.
                requirements_table.columns( 3 ).search( $( this ).val() ).draw() ;
            }
        });

    $('#status-filter-input').autocomplete({
        minLength: 0,
        source: available_status,
        delay: 100
    })
        .on('focus', function() { $(this).keydown(); })
        .on('autocompleteselect', function(event, ui){
            requirements_table.columns( 5 ).search( ui.item['value'] ).draw() ;
        })
        .on('keypress', function (e) {
            if (e.which === 13) { // Search on Enter.
                requirements_table.columns( 5 ).search( $( this ).val() ).draw() ;
            }
        });

    $('#tag-filter-input').autocomplete({
        minLength: 0,
        source: available_tags,
        delay: 100
    })
        .on('focus', function() { $(this).keydown(); })
        .on('autocompleteselect', function(event, ui){
            requirements_table.columns( 4 ).search( ui.item['value'] ).draw() ;
        })
        .on('keypress', function (e) {
            if (e.which === 13) { // Search on Enter.
                requirements_table.columns( 4 ).search( $( this ).val() ).draw() ;
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
        requirements_table.search( '' ).columns().search( '' ).draw();
    });

    // Listen for tool section triggers.
    $('#gen-req-from-selection').click(function () {
        req_ids = [];
        requirements_table.rows( {search:'applied'} ).every( function () {
           var d = this.data();
           req_ids.push(d['id']);
         } );
        $('#selected_requirement_ids').val(JSON.stringify(req_ids));
        $('#generate_req_form').submit();
    });

    $('#gen-csv-from-selection').click(function () {
        req_ids = [];
        requirements_table.rows( {search:'applied'} ).every( function () {
           var d = this.data();
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
        var column = requirements_table.column( $(this).attr('data-column') );

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
    var columnDefs = [
            {
                "targets": [0],
                "data": "pos"
            },
            {
                "targets": [1],
                "data": "id",
                "render": function ( data, type, row, meta ) {
                    result = '<a href="#">' + data + '</a>';
                    return result;
                }
            },
            {
                "targets": [2],
                "data": "desc"
            },
            {
                "targets": [3],
                "data": "type",
                "render": function ( data, type, row, meta ) {
                    if (available_types.indexOf(data) <= -1) {
                        available_types.push(data);
                    }
                    return data;
                }
            },
            {
                "targets": [4],
                "data": "tags",
                "render": function ( data, type, row, meta ) {
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
                "targets": [5],
                "data": "status",
                "render": function ( data, type, row, meta ) {
                    result = '<span class="badge badge-info">' + data + '</span></br>';
                    return result;
                }
            }
        ];
    // Load generic colums.
    genericColums = $.get( "api/table/colum_defs", '', function (data) {
        var dataLength = data['col_defs'].length;
        for (var i = 0; i < dataLength; i++) {
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