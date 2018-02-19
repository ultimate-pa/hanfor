// Globals
var available_tags = ['', 'has_formalization'];
var available_status = ['', 'Todo', 'Review', 'Done'];
var available_types = [''];
var get_query = JSON.parse(search_query);

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
            .search( get_query.q );
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
}


$(document).ready(function() {
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
        "columns": [
            { "data": "pos"},
            {
                "data": "id",
                "render": function ( data, type, row, meta ) {
                    result = '<a href="#">' + data + '</a>';
                    return result;
                }
            },
            { "data": "desc" },
            {
                "data": "type",
                "render": function ( data, type, row, meta ) {
                    if (available_types.indexOf(data) <= -1) {
                        available_types.push(data);
                    }
                    return data;
                }
            },
            {
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
                "data": "status",
                "render": function ( data, type, row, meta ) {
                    result = '<span class="badge badge-info">' + data + '</span></br>';
                    return result;
                }
            },
            {
                "data": "formal",
                "visible": false,
                "searchable": false
            }
        ],
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
        }
    });

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
        } ).done(function () {
            // Update visible Vars.
            update_vars();
            // Handle autocompletion for variables.
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
                        data.available_vars, extractLast( request.term ) ) );
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
            // Update available vars based on the selection of requirement and pattern.
            bind_expression_buttons();
            requirement_modal_content.LoadingOverlay('hide', true);
        });
    } );

    // Initialize tag autocomplete filed in the requirements modal.
    $('#requirement_tag_field').tokenfield({
      autocomplete: {
        source: available_tags,
        delay: 100
      },
      showAutocompleteOnFocus: true
    });

    $('#save_requirement_modal').click(function () {
        store_requirement(requirements_table);
    });

    // Clear the Modal after closing modal.
    $('#requirement_modal').on('hidden.bs.modal', function (e) {
        $('#requirement_tag_field').val('');
        $('#requirement_tag_field-tokenfield').val('');
    });

    // Search related stuff.
    // Bind big custom searchbar to search the table.
    $('#search_bar').keyup(function(){
      requirements_table.search($(this).val()).draw() ;
    });

    // Set up the filters.
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

    $('#add_formalization').click(function () {
        add_formalization();
    });

    // Initialize modal.
    update_vars();

    // Process URL search query.
    process_url_query(requirements_table, get_query);
} );