/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./js/variable-import.js":
/*!*******************************!*\
  !*** ./js/variable-import.js ***!
  \*******************************/
/***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {

eval("/* provided dependency */ var $ = __webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\");\n__webpack_require__(/*! gasparesganga-jquery-loading-overlay */ \"./node_modules/gasparesganga-jquery-loading-overlay/src/loadingoverlay.js\");\n__webpack_require__(/*! bootstrap */ \"./node_modules/bootstrap/dist/js/bootstrap.esm.js\");\n__webpack_require__(/*! datatables.net-bs5 */ \"./node_modules/datatables.net-bs5/js/dataTables.bootstrap5.mjs\");\n__webpack_require__(/*! datatables.net-select */ \"./node_modules/datatables.net-select/js/dataTables.select.mjs\");\n__webpack_require__(/*! jquery-ui/ui/widgets/autocomplete */ \"./node_modules/jquery-ui/ui/widgets/autocomplete.js\");\n__webpack_require__(/*! jquery-ui/ui/effects/effect-highlight */ \"./node_modules/jquery-ui/ui/effects/effect-highlight.js\");\n__webpack_require__(/*! ./bootstrap-tokenfield.js */ \"./js/bootstrap-tokenfield.js\");\n//require('datatables.net-colreorderwithresize-npm');\n__webpack_require__(/*! datatables.net-colreorder-bs5 */ \"./node_modules/datatables.net-colreorder-bs5/js/colReorder.bootstrap5.mjs\");\n__webpack_require__(/*! ./bootstrap-confirm-button */ \"./js/bootstrap-confirm-button.js\");\n\n\n// Globals\nlet available_types = ['bool', 'int', 'real', 'unknown', 'CONST', 'ENUM', 'ENUMERATOR'];\nlet global_changes = false;\nconst { SearchNode } = __webpack_require__(/*! ./datatables-advanced-search.js */ \"./js/datatables-advanced-search.js\");\nlet var_import_search_string = sessionStorage.getItem('var_import_search_string');\nlet search_tree = undefined;\nlet visible_columns = [true, true, true, true, true, true];\n\n\n/**\n * Apply search tree on datatables data.\n * @param data\n * @returns {bool|XPathResult}\n */\nfunction evaluate_search(data){\n    return search_tree.evaluate(data, visible_columns);\n}\n\n/**\n * Update the search expression tree.\n */\nfunction update_search() {\n    var_import_search_string = $('#search_bar').val().trim();\n    sessionStorage.setItem('var_import_search_string', var_import_search_string);\n    search_tree = SearchNode.fromQuery(var_import_search_string);\n}\n\nfunction load_enumerators_to_modal(var_name, var_import_table) {\n    let enum_div = $('#enumerators');\n    enum_div.html('');\n    let enum_html = '';\n    var_import_table.rows( ).every( function () {\n        let data = this.data();\n        if ((var_name.length < data.name.length) && data.name.startsWith(var_name)) {\n            if (typeof(data.result.name) !== 'undefined') {\n                enum_html += '<p><code>' + data.name + '</code> : <code>' + data.result.const_val + '</code></p>';\n            }\n        }\n    });\n\n    enum_div.html(enum_html);\n}\n\n\nfunction load_constraints_to_container(data, var_object, constraints_container, type) {\n    function add_constraints(constraints, handles = false, type = 'none') {\n        let constraints_html = '';\n\n        for (var key in constraints) {\n            let constraint = constraints[key];\n            if (constraint.origin !== type) {\n                continue;\n            }\n            if (handles) {\n                let text = '';\n                let css_class = '';\n                if (constraint.to_result) {\n                    text = 'Included in result (click to toggle).';\n                    css_class = 'btn-success';\n                } else {\n                    text = 'Not Included in result (click to toggle).';\n                    css_class = 'btn-secondary'\n                }\n                constraints_html += '<div class=\"constraint-element\">'\n                constraints_html += '<button type=\"button\" ' +\n                    'data-type=\"' + type + '\" ' +\n                    'data-constrid=\"' + constraint.id + '\" ' +\n                    'class=\"btn ' + css_class + ' btn-sm constraint-handle\">' +\n                    text +\n                    '</button>';\n                constraints_html += '<pre>' + constraint.constraint + '</pre>';\n                constraints_html += '</div>';\n            } else {\n                constraints_html += '<pre>' + constraint.constraint + '</pre>';\n            }\n        }\n        return constraints_html;\n    }\n\n    let constraints_list_dom = $('#constraints_list');\n    let constraints_html = '';\n    if (type === 'result') {\n        if ((typeof(data.target.constraints) !== 'undefined') && (data.target.constraints.length > 0)) {\n            constraints_html += '<h6>From Target</h6>';\n            constraints_html += add_constraints(data.available_constraints, true, 'target');\n        }\n        if ((typeof(data.source.constraints) !== 'undefined') && (data.source.constraints.length > 0)) {\n            constraints_html += '<h6>From Source</h6>';\n            constraints_html += add_constraints(data.available_constraints, true, 'source');\n        }\n    } else {\n        constraints_html += add_constraints(data.available_constraints, false, type);\n    }\n    constraints_list_dom.html(constraints_html);\n    constraints_container.show();\n}\n\n\nfunction load_modal(data, var_import_table, type) {\n    let var_view_modal = $('#variable_modal');\n    let var_value_form = $('#variable_value_form_group');\n    let enum_controls = $('.enum-controls');\n    let constraints_container = $('#constraints_container');\n    let var_object = Object();\n    let type_input = $('#variable_type');\n    let variable_value = $('#variable_value');\n    let save_variable_modal = $('#save_variable_modal');\n    let title = '';\n\n    type_input.prop('disabled', true);\n    variable_value.prop('disabled', true);\n    save_variable_modal.hide();\n    global_changes = false;\n\n    if (type === 'source') {\n        var_object = data.source;\n        title = 'Source Variable:';\n    } else if (type === 'target') {\n        var_object = data.target;\n        title = 'Target Variable:';\n    } else if (type === 'result') {\n        title = 'Resulting Variable:';\n        var_object = data.result;\n        type_input.prop('disabled', false);\n        variable_value.prop('disabled', false);\n        save_variable_modal.show();\n    }\n\n    type_input.autocomplete({\n        minLength: 0,\n        source: available_types\n    }).on('focus', function() { $(this).keydown(); });\n\n    // Prepare modal\n    $('#variable_modal_title').html(title + ' <code>' + data.name + '</code>');\n    save_variable_modal.attr('data-name', data.name);\n    type_input.val(var_object.type);\n    var_value_form.hide();\n    enum_controls.hide();\n    constraints_container.hide();\n\n\n    if (var_object.type === 'CONST' || var_object.type === 'ENUMERATOR') {\n        var_value_form.show();\n        variable_value.val(var_object.const_val);\n        //variable_value_old.val(var_object.const_val);\n    } else if (var_object.type === 'ENUM') {\n        enum_controls.show();\n        $('#enumerators').html('');\n        load_enumerators_to_modal(var_object.name, var_import_table);\n    }\n\n    load_constraints_to_container(data, var_object, constraints_container, type);\n\n    // Bind constraint handles\n    $('.constraint-handle').click(function () {\n        global_changes = true;\n        let constraint_id = $(this).attr('data-constrid');\n        let constraint = $(this).closest('div').find( \"pre\" );\n        let row = var_import_table.row('#' + data.name);\n        let row_data = row.data();\n\n        constraint.effect(\"highlight\", {color: 'green'}, 800);\n        $(this).toggleClass(\"btn-success\");\n        $(this).toggleClass(\"btn-secondary\");\n\n        if ($(this).hasClass(\"btn-success\")) {\n            $(this).html('Included in result (click to toggle).');\n            row_data.available_constraints[constraint_id].to_result = true;\n        } else {\n            $(this).html('Not Included in result (click to toggle).');\n            row_data.available_constraints[constraint_id].to_result = false;\n        }\n        row.data(row_data);\n    });\n\n    // $('#var_view_modal_body').html(body_html);\n    var_view_modal.modal('show');\n}\n\n\nfunction redraw_table(var_import_table) {\n    var_import_table.draw('full-hold');\n}\n\n\nfunction modify_row_by_action(row, action, redraw = true, store = true) {\n    let data = row.data();\n    if ((action === 'source') && (data.action !== 'source')) {\n        if (typeof(data.source.name) !== 'undefined') {\n            data.result = data.source;\n            data.action = 'source';\n        }\n    } else if ((action === 'target') && (data.action !== 'target')) {\n        if (typeof(data.target.name) !== 'undefined') {\n            data.result = data.target;\n            data.action = 'target';\n        }\n    } else if (action === 'skip') {\n        data.result = data.target;\n        data.action =  (typeof(data.target.name) !== 'undefined' ? 'target' : 'skipped');\n    }\n\n    for (var key in data.available_constraints) {\n        let constraint = data.available_constraints[key];\n        data.available_constraints[key].to_result = constraint.origin === action;\n    }\n\n    if (redraw) {\n        row.data(data).draw('full-hold');\n    } else {\n        row.data(data);\n    }\n    if (store) {\n        store_changes(data);\n    }\n}\n\n\nfunction get_selected_vars(variables_table) {\n    let selected_vars = [];\n    variables_table.rows( {selected:true} ).every( function () {\n        let d = this.data();\n        selected_vars.push(d['name']);\n    });\n    return selected_vars;\n}\n\n\nfunction apply_multiselect_action(var_import_table, action) {\n    var_import_table.rows( {selected:true} ).every( function () {\n        modify_row_by_action(this, action, false, false);\n    });\n    // redraw_table(var_import_table);\n    store_changes();\n}\n\n\nfunction store_modal(var_table, target_row) {\n    let var_view_modal = $('#variable_modal');\n    let type_by_modal = $('#variable_type').val();\n    let value_by_modal = $('#variable_value').val();\n    let table_data = target_row.data();\n    // First check if we have changes.\n    let changes = false;\n    if (table_data.result.type !== type_by_modal) {\n        changes = true;\n        table_data.result.type = type_by_modal;\n    }\n    if ((table_data.result.type === 'CONST' || table_data.result.type === 'ENUMERATOR') &&\n        (table_data.result.const_val !== value_by_modal)) {\n        changes = true;\n        table_data.result.const_val = value_by_modal;\n    }\n    if (changes || global_changes) {\n        table_data.action = 'custom';\n        // Sync with backend.\n        var_view_modal.LoadingOverlay('show');\n        $.post( \"api/\" + session_id + \"/store_variable\",\n            {\n                row: JSON.stringify(table_data)\n            },\n            // Update var table on success or show an error message.\n            function( data ) {\n                var_view_modal.LoadingOverlay('hide', true);\n                if (data['success'] === false) {\n                    alert(data['errormsg']);\n                } else {\n                    target_row.data(table_data).draw('full-hold');\n                    var_view_modal.modal('hide');\n                    $(target_row.node()).effect(\"highlight\", {color: 'green'}, 800);\n                }\n        });\n    } else {\n        var_view_modal.modal('hide');\n    }\n}\n\n\nfunction store_changes(data = false) {\n    let body = $('body');\n    body.LoadingOverlay('show');\n\n    // Fetch relevant changes\n    let rows = Object();\n    if (!data) {\n        $( '#var_import_table' ).DataTable().rows( {selected:true} ).every( function () {\n            let row = this.data();\n            rows[row.name] = {\n                action: row.action\n            };\n        });\n    } else {\n        rows[data.name] = {\n            action: data.action\n        }\n    }\n\n    rows = JSON.stringify(rows);\n\n    // Send changes to backend.\n    $.post( \"api/\" + session_id + \"/store_table\",\n        {\n            rows: rows\n        },\n        // Update requirements table on success or show an error message.\n        function( data ) {\n            body.LoadingOverlay('hide', true);\n            if (data['success'] === false) {\n                alert(data['errormsg']);\n            }\n    });\n}\n\n\nfunction apply_import(var_import_table) {\n    let body = $('body');\n    body.LoadingOverlay('show');\n\n    // Send changes to backend.\n    $.post( \"api/\" + session_id + \"/apply_import\",\n        {},\n        // Update requirements table on success or show an error message.\n        function( data ) {\n            body.LoadingOverlay('hide', true);\n            if (data['success'] === false) {\n                alert(data['errormsg']);\n            } else {\n                alert('Imported result variables.');\n            }\n    });\n}\n\n\nfunction delete_this_session() {\n    let body = $('body');\n    body.LoadingOverlay('show');\n\n    $.post( \"api/\" + session_id + \"/delete_me\",\n        {\n            id: session_id\n        },\n        // Hop to Hanfor root after successful deletion.\n        function( data ) {\n            body.LoadingOverlay('hide', true);\n            if (data['success'] === false) {\n                alert(data['errormsg']);\n            } else {\n                window.location.href = base_url + \"variables\";\n            }\n    });\n}\n\n\nfunction apply_tools_action(var_import_table, action) {\n    if (action === 'apply-import') {\n        apply_import(var_import_table);\n    }\n    if (action === 'delete-session') {\n        delete_this_session();\n    }\n}\n\n\n$(document).ready(function() {\n    // Prepare and load the variables table.\n    let var_import_table = $('#var_import_table').DataTable({\n        \"paging\": true,\n        \"stateSave\": true,\n        \"select\": {\n            style:    'os',\n            selector: 'td:first-child'\n        },\n        \"pageLength\": 200,\n        \"responsive\": true,\n        \"lengthMenu\": [[10, 50, 100, 500, -1], [10, 50, 100, 500, \"All\"]],\n        \"dom\": 'rt<\"container\"<\"row\"<\"col-md-6\"li><\"col-md-6\"p>>>',\n        \"ajax\": \"api/\" + session_id + \"/get_table_data\",\n        \"deferRender\": true,\n        \"rowId\": 'name',\n        \"columns\": [\n            {\n                // The mass selection column.\n                \"orderable\": false,\n                \"className\": 'select-checkbox',\n                \"targets\": [0],\n                \"data\": null,\n                \"defaultContent\": \"\"\n            },\n            {\n                // The actions column.\n                \"data\": function ( row, type, val, meta ) {\n                    return row;\n                },\n                \"targets\": [1],\n                \"orderable\": false,\n                \"render\": function ( data, type, row, meta ) {\n                    let result = '<div class=\"btn-group\" role=\"group\" aria-label=\"Basic example\">'\n                        + '<button type=\"button\" data-action=\"skip\" class=\"skip-btn btn btn-secondary'\n                        + (data.action === 'skipped' ? ' active' : '') + '\">Skip</button>'\n                        + '<button type=\"button\" data-action=\"source\" class=\"source-btn btn btn-secondary'\n                        + (data.action === 'source' ? ' active' : '') + '\">Source</button>'\n                        + '<button type=\"button\" data-action=\"target\" class=\"target-btn btn btn-secondary'\n                        + (data.action === 'target' ? ' active' : '') + '\">Target</button>'\n                        + '<button type=\"button\" data-action=\"custom\" class=\"custom-btn btn btn-secondary'\n                        + (data.action === 'custom' ? ' active' : '') + '\">Custom</button>'\n                        + '</div>';\n                    return result;\n                }\n            },\n            {\n                // The attributes column.\n                \"data\": function ( row, type, val, meta ) {\n                    return row;\n                },\n                \"targets\": [1],\n                \"render\": function ( data, type, row, meta ) {\n                    let result = ``;\n                    const has_source = typeof(data.source.name) !== 'undefined';\n                    const has_target = typeof(data.target.name) !== 'undefined';\n\n                    if (has_source && has_target) {\n                        result += '<span class=\"badge bg-info\">match_in_source_and_target</span>'\n                        if (data.source.type !== data.target.type) {\n                            result += '<span class=\"badge bg-info\">unmatched_types</span>'\n                        } else {\n                            result += '<span class=\"badge bg-info\">same_types</span>'\n                        }\n                    } else {\n                        if (!has_source) {\n                            result += '<span class=\"badge bg-info\">no_match_in_source</span>'\n                        }\n                        if (!has_target) {\n                            result += '<span class=\"badge bg-info\">no_match_in_target</span>'\n                        }\n                    }\n                    if (has_source && data.source.constraints.length > 0) {\n                        result += '<span class=\"badge bg-info\">source_has_constraints</span>'\n                    }\n                    if (has_target && data.target.constraints.length > 0) {\n                        result += '<span class=\"badge bg-info\">target_has_constraints</span>'\n                    }\n                    return result;\n                }\n            },\n            {\n                // The source column.\n                \"data\": function ( row, type, val, meta ) {\n                    return row.source;\n                },\n                \"targets\": [3],\n                \"render\": function ( data, type, row, meta ) {\n                    let result = '';\n                    if (typeof(data.name) !== 'undefined') {\n                        result = '<p class=\"var_link\" data-type=\"source\" style=\"cursor: pointer\"><code>' +\n                            data.name + '</code> <span class=\"badge bg-info\">' + data.type + '</span></p>';\n                    } else {\n                        result = 'No match.'\n                    }\n                    return result;\n                }\n            },\n            {\n                // The target column.\n                \"data\": function ( row, type, val, meta ) {\n                    return row.target;\n                },\n                \"targets\": [4],\n                \"order\": 'asc',\n                \"render\": function ( data, type, row, meta ) {\n                    let result = '';\n                    if (typeof(data.name) !== 'undefined') {\n                        result = '<p class=\"var_link\" data-type=\"target\" style=\"cursor: pointer\"><code>' +\n                            data.name + '</code><span class=\"badge bg-info\">' + data.type + '</span>';\n                    } else {\n                        result = 'No match.'\n                    }\n                    return result;\n                }\n\n            },\n            {\n                // The result column.\n                \"data\": function ( row, type, val, meta ) {\n                    return row.result;\n                },\n                \"targets\": [5],\n                \"render\": function ( data, type, row, meta ) {\n                    let result = '';\n                    if (typeof(data.name) !== 'undefined') {\n                        result = '<p class=\"var_link\" data-type=\"result\" style=\"cursor: pointer\"><code>' +\n                            data.name + '</code><span class=\"badge bg-info\">' + data.type + '</span>';\n                    } else {\n                        result = 'Skipped.'\n                    }\n                    return result;\n                }\n            }\n        ],\n        infoCallback: function( settings, start, end, max, total, pre ) {\n            var api = this.api();\n            var pageInfo = api.page.info();\n\n            $('#clear-all-filters-text').html(\"Showing \" + total +\"/\"+ pageInfo.recordsTotal + \". Clear all.\");\n\n            let result = \"Showing \" + start + \" to \" + end + \" of \" + total + \" entries\";\n            result += \" (filtered from \" + pageInfo.recordsTotal + \" total entries).\";\n\n            return result;\n        },\n        initComplete : function() {\n            $('#search_bar').val(var_import_search_string);\n\n            update_search();\n\n            // Enable Hanfor specific table filtering.\n            $.fn.dataTable.ext.search.push(\n                function( settings, data, dataIndex ) {\n                    // data contains the row. data[0] is the content of the first column in the actual row.\n                    // Return true to include the row into the data. false to exclude.\n                    return evaluate_search(data);\n                }\n            );\n\n            this.api().draw();\n\n        }\n    });\n    new $.fn.dataTable.ColReorder(var_import_table, {});\n\n    // Bind big custom searchbar to search the table.\n    $('#search_bar').keypress(function(e) {\n        if(e.which === 13) { // Search on enter.\n            update_search();\n            var_import_table.draw();\n        }\n    });\n\n    let var_import_table_body = $('#var_import_table tbody');\n\n    // Add listener for variable link to modal.\n    var_import_table_body.on('click', '.var_link', function (event) {\n        // prevent body to be scrolled to the top.\n        event.preventDefault();\n        let data = var_import_table.row( $(this).parents('tr') ).data();\n        let type = $(this).attr('data-type');\n        load_modal(data, var_import_table, type);\n    });\n    \n    $('#save_variable_modal').click(function () {\n        let name = $(this).attr('data-name');\n        let row = var_import_table.row('#' + name);\n        store_modal(var_import_table, row);\n    });\n\n    $('#variable_type').on('change, focusout, keyup', function () {\n        let var_value_form = $('#variable_value_form_group');\n        if (['CONST', 'ENUMERATOR'].includes($( this ).val())) {\n            var_value_form.show();\n        } else {\n            var_value_form.hide();\n        }\n    });\n\n    // Add listener for table row action buttons.\n    var_import_table_body.on('click', '.target-btn, .source-btn, .skip-btn', function (event) {\n        // prevent body to be scrolled to the top.\n        event.preventDefault();\n        let row = var_import_table.row( $(this).parents('tr') );\n        let action = $(this).attr('data-action');\n        modify_row_by_action(row, action);\n    });\n\n    // Multiselect. Select single rows.\n    $('.select-all-button').on('click', function (e) {\n        // Toggle selection on\n        if ($( this ).hasClass('btn-secondary')) {\n            var_import_table.rows( {page:'current'} ).select();\n        }\n        else { // Toggle selection off\n            var_import_table.rows( {page:'current'} ).deselect();\n        }\n        // Toggle button state.\n        $('.select-all-button').toggleClass('btn-secondary btn-primary');\n    });\n\n    // Multiselect action buttons\n    $('.action-btn').click(function (e) {\n        apply_multiselect_action(var_import_table, $(this).attr('data-action'));\n    });\n\n    // Buttons that must be confirmed\n    // $('#delete_session_button').confirmation({\n    //   rootSelector: '#delete_session_button'\n    // });\n\n    // Tools Buttons\n    $('#delete_session_button').bootstrapConfirmButton({\n        onConfirm: function () {\n            apply_tools_action(var_import_table, $(this).attr('data-action'))\n        }\n    })\n\n    $('#apply_import_btn').click(function () {\n        apply_tools_action(var_import_table, $(this).attr('data-action'));\n    });\n\n    // Toggle \"Select all rows to `off` on user specific selection.\"\n    var_import_table.on( 'user-select', function ( ) {\n        let select_buttons = $('.select-all-button');\n        select_buttons.removeClass('btn-primary');\n        select_buttons.addClass('btn-secondary ');\n    });\n\n    // Clear all applied searches.\n    $('.clear-all-filters').click(function () {\n        $('#search_bar').val('').effect(\"highlight\", {color: 'green'}, 500);\n        update_search();\n        var_import_table.draw();\n    });\n} );\n\n//# sourceURL=webpack://hanfor/./js/variable-import.js?");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			id: moduleId,
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = __webpack_modules__;
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/chunk loaded */
/******/ 	(() => {
/******/ 		var deferred = [];
/******/ 		__webpack_require__.O = (result, chunkIds, fn, priority) => {
/******/ 			if(chunkIds) {
/******/ 				priority = priority || 0;
/******/ 				for(var i = deferred.length; i > 0 && deferred[i - 1][2] > priority; i--) deferred[i] = deferred[i - 1];
/******/ 				deferred[i] = [chunkIds, fn, priority];
/******/ 				return;
/******/ 			}
/******/ 			var notFulfilled = Infinity;
/******/ 			for (var i = 0; i < deferred.length; i++) {
/******/ 				var [chunkIds, fn, priority] = deferred[i];
/******/ 				var fulfilled = true;
/******/ 				for (var j = 0; j < chunkIds.length; j++) {
/******/ 					if ((priority & 1 === 0 || notFulfilled >= priority) && Object.keys(__webpack_require__.O).every((key) => (__webpack_require__.O[key](chunkIds[j])))) {
/******/ 						chunkIds.splice(j--, 1);
/******/ 					} else {
/******/ 						fulfilled = false;
/******/ 						if(priority < notFulfilled) notFulfilled = priority;
/******/ 					}
/******/ 				}
/******/ 				if(fulfilled) {
/******/ 					deferred.splice(i--, 1)
/******/ 					var r = fn();
/******/ 					if (r !== undefined) result = r;
/******/ 				}
/******/ 			}
/******/ 			return result;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/jsonp chunk loading */
/******/ 	(() => {
/******/ 		// no baseURI
/******/ 		
/******/ 		// object to store loaded and loading chunks
/******/ 		// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 		// [resolve, reject, Promise] = chunk loading, 0 = chunk loaded
/******/ 		var installedChunks = {
/******/ 			"variable_import": 0
/******/ 		};
/******/ 		
/******/ 		// no chunk on demand loading
/******/ 		
/******/ 		// no prefetching
/******/ 		
/******/ 		// no preloaded
/******/ 		
/******/ 		// no HMR
/******/ 		
/******/ 		// no HMR manifest
/******/ 		
/******/ 		__webpack_require__.O.j = (chunkId) => (installedChunks[chunkId] === 0);
/******/ 		
/******/ 		// install a JSONP callback for chunk loading
/******/ 		var webpackJsonpCallback = (parentChunkLoadingFunction, data) => {
/******/ 			var [chunkIds, moreModules, runtime] = data;
/******/ 			// add "moreModules" to the modules object,
/******/ 			// then flag all "chunkIds" as loaded and fire callback
/******/ 			var moduleId, chunkId, i = 0;
/******/ 			if(chunkIds.some((id) => (installedChunks[id] !== 0))) {
/******/ 				for(moduleId in moreModules) {
/******/ 					if(__webpack_require__.o(moreModules, moduleId)) {
/******/ 						__webpack_require__.m[moduleId] = moreModules[moduleId];
/******/ 					}
/******/ 				}
/******/ 				if(runtime) var result = runtime(__webpack_require__);
/******/ 			}
/******/ 			if(parentChunkLoadingFunction) parentChunkLoadingFunction(data);
/******/ 			for(;i < chunkIds.length; i++) {
/******/ 				chunkId = chunkIds[i];
/******/ 				if(__webpack_require__.o(installedChunks, chunkId) && installedChunks[chunkId]) {
/******/ 					installedChunks[chunkId][0]();
/******/ 				}
/******/ 				installedChunks[chunkId] = 0;
/******/ 			}
/******/ 			return __webpack_require__.O(result);
/******/ 		}
/******/ 		
/******/ 		var chunkLoadingGlobal = self["webpackChunkhanfor"] = self["webpackChunkhanfor"] || [];
/******/ 		chunkLoadingGlobal.forEach(webpackJsonpCallback.bind(null, 0));
/******/ 		chunkLoadingGlobal.push = webpackJsonpCallback.bind(null, chunkLoadingGlobal.push.bind(chunkLoadingGlobal));
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/nonce */
/******/ 	(() => {
/******/ 		__webpack_require__.nc = undefined;
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module depends on other loaded chunks and execution need to be delayed
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, ["commons"], () => (__webpack_require__("./js/variable-import.js")))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;