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

eval("/* provided dependency */ var $ = __webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\");\n__webpack_require__(/*! gasparesganga-jquery-loading-overlay */ \"./node_modules/gasparesganga-jquery-loading-overlay/dist/loadingoverlay.min.js\");\r\n__webpack_require__(/*! bootstrap */ \"./node_modules/bootstrap/dist/js/bootstrap.esm.js\");\r\n__webpack_require__(/*! datatables.net-bs5 */ \"./node_modules/datatables.net-bs5/js/dataTables.bootstrap5.mjs\");\r\n__webpack_require__(/*! datatables.net-select */ \"./node_modules/datatables.net-select/js/dataTables.select.mjs\");\r\n__webpack_require__(/*! jquery-ui/ui/widgets/autocomplete */ \"./node_modules/jquery-ui/ui/widgets/autocomplete.js\");\r\n__webpack_require__(/*! jquery-ui/ui/effects/effect-highlight */ \"./node_modules/jquery-ui/ui/effects/effect-highlight.js\");\r\n__webpack_require__(/*! ./bootstrap-tokenfield.js */ \"./js/bootstrap-tokenfield.js\");\r\n//require('datatables.net-colreorderwithresize-npm');\r\n__webpack_require__(/*! datatables.net-colreorder-bs5 */ \"./node_modules/datatables.net-colreorder-bs5/js/colReorder.bootstrap5.mjs\");\r\n__webpack_require__(/*! ./bootstrap-confirm-button */ \"./js/bootstrap-confirm-button.js\");\r\n\r\n\r\n// Globals\r\nlet available_types = ['bool', 'int', 'real', 'unknown', 'CONST', 'ENUM', 'ENUMERATOR'];\r\nlet global_changes = false;\r\nconst { SearchNode } = __webpack_require__(/*! ./datatables-advanced-search.js */ \"./js/datatables-advanced-search.js\");\r\nlet var_import_search_string = sessionStorage.getItem('var_import_search_string');\r\nlet search_tree = undefined;\r\nlet visible_columns = [true, true, true, true, true, true];\r\n\r\n\r\n/**\r\n * Apply search tree on datatables data.\r\n * @param data\r\n * @returns {bool|XPathResult}\r\n */\r\nfunction evaluate_search(data){\r\n    return search_tree.evaluate(data, visible_columns);\r\n}\r\n\r\n/**\r\n * Update the search expression tree.\r\n */\r\nfunction update_search() {\r\n    var_import_search_string = $('#search_bar').val().trim();\r\n    sessionStorage.setItem('var_import_search_string', var_import_search_string);\r\n    search_tree = SearchNode.fromQuery(var_import_search_string);\r\n}\r\n\r\nfunction load_enumerators_to_modal(var_name, var_import_table) {\r\n    let enum_div = $('#enumerators');\r\n    enum_div.html('');\r\n    let enum_html = '';\r\n    var_import_table.rows( ).every( function () {\r\n        let data = this.data();\r\n        if ((var_name.length < data.name.length) && data.name.startsWith(var_name)) {\r\n            if (typeof(data.result.name) !== 'undefined') {\r\n                enum_html += '<p><code>' + data.name + '</code> : <code>' + data.result.const_val + '</code></p>';\r\n            }\r\n        }\r\n    });\r\n\r\n    enum_div.html(enum_html);\r\n}\r\n\r\n\r\nfunction load_constraints_to_container(data, var_object, constraints_container, type) {\r\n    function add_constraints(constraints, handles = false, type = 'none') {\r\n        let constraints_html = '';\r\n\r\n        for (var key in constraints) {\r\n            let constraint = constraints[key];\r\n            if (constraint.origin !== type) {\r\n                continue;\r\n            }\r\n            if (handles) {\r\n                let text = '';\r\n                let css_class = '';\r\n                if (constraint.to_result) {\r\n                    text = 'Included in result (click to toggle).';\r\n                    css_class = 'btn-success';\r\n                } else {\r\n                    text = 'Not Included in result (click to toggle).';\r\n                    css_class = 'btn-secondary'\r\n                }\r\n                constraints_html += '<div class=\"constraint-element\">'\r\n                constraints_html += '<button type=\"button\" ' +\r\n                    'data-type=\"' + type + '\" ' +\r\n                    'data-constrid=\"' + constraint.id + '\" ' +\r\n                    'class=\"btn ' + css_class + ' btn-sm constraint-handle\">' +\r\n                    text +\r\n                    '</button>';\r\n                constraints_html += '<pre>' + constraint.constraint + '</pre>';\r\n                constraints_html += '</div>';\r\n            } else {\r\n                constraints_html += '<pre>' + constraint.constraint + '</pre>';\r\n            }\r\n        }\r\n        return constraints_html;\r\n    }\r\n\r\n    let constraints_list_dom = $('#constraints_list');\r\n    let constraints_html = '';\r\n    if (type === 'result') {\r\n        if ((typeof(data.target.constraints) !== 'undefined') && (data.target.constraints.length > 0)) {\r\n            constraints_html += '<h6>From Target</h6>';\r\n            constraints_html += add_constraints(data.available_constraints, true, 'target');\r\n        }\r\n        if ((typeof(data.source.constraints) !== 'undefined') && (data.source.constraints.length > 0)) {\r\n            constraints_html += '<h6>From Source</h6>';\r\n            constraints_html += add_constraints(data.available_constraints, true, 'source');\r\n        }\r\n    } else {\r\n        constraints_html += add_constraints(data.available_constraints, false, type);\r\n    }\r\n    constraints_list_dom.html(constraints_html);\r\n    constraints_container.show();\r\n}\r\n\r\n\r\nfunction load_modal(data, var_import_table, type) {\r\n    let var_view_modal = $('#variable_modal');\r\n    let var_value_form = $('#variable_value_form_group');\r\n    let enum_controls = $('.enum-controls');\r\n    let constraints_container = $('#constraints_container');\r\n    let var_object = Object();\r\n    let type_input = $('#variable_type');\r\n    let variable_value = $('#variable_value');\r\n    let save_variable_modal = $('#save_variable_modal');\r\n    let title = '';\r\n\r\n    type_input.prop('disabled', true);\r\n    variable_value.prop('disabled', true);\r\n    save_variable_modal.hide();\r\n    global_changes = false;\r\n\r\n    if (type === 'source') {\r\n        var_object = data.source;\r\n        title = 'Source Variable:';\r\n    } else if (type === 'target') {\r\n        var_object = data.target;\r\n        title = 'Target Variable:';\r\n    } else if (type === 'result') {\r\n        title = 'Resulting Variable:';\r\n        var_object = data.result;\r\n        type_input.prop('disabled', false);\r\n        variable_value.prop('disabled', false);\r\n        save_variable_modal.show();\r\n    }\r\n\r\n    type_input.autocomplete({\r\n        minLength: 0,\r\n        source: available_types\r\n    }).on('focus', function() { $(this).keydown(); });\r\n\r\n    // Prepare modal\r\n    $('#variable_modal_title').html(title + ' <code>' + data.name + '</code>');\r\n    save_variable_modal.attr('data-name', data.name);\r\n    type_input.val(var_object.type);\r\n    var_value_form.hide();\r\n    enum_controls.hide();\r\n    constraints_container.hide();\r\n\r\n\r\n    if (var_object.type === 'CONST' || var_object.type === 'ENUMERATOR') {\r\n        var_value_form.show();\r\n        variable_value.val(var_object.const_val);\r\n        //variable_value_old.val(var_object.const_val);\r\n    } else if (var_object.type === 'ENUM') {\r\n        enum_controls.show();\r\n        $('#enumerators').html('');\r\n        load_enumerators_to_modal(var_object.name, var_import_table);\r\n    }\r\n\r\n    load_constraints_to_container(data, var_object, constraints_container, type);\r\n\r\n    // Bind constraint handles\r\n    $('.constraint-handle').click(function () {\r\n        global_changes = true;\r\n        let constraint_id = $(this).attr('data-constrid');\r\n        let constraint = $(this).closest('div').find( \"pre\" );\r\n        let row = var_import_table.row('#' + data.name);\r\n        let row_data = row.data();\r\n\r\n        constraint.effect(\"highlight\", {color: 'green'}, 800);\r\n        $(this).toggleClass(\"btn-success\");\r\n        $(this).toggleClass(\"btn-secondary\");\r\n\r\n        if ($(this).hasClass(\"btn-success\")) {\r\n            $(this).html('Included in result (click to toggle).');\r\n            row_data.available_constraints[constraint_id].to_result = true;\r\n        } else {\r\n            $(this).html('Not Included in result (click to toggle).');\r\n            row_data.available_constraints[constraint_id].to_result = false;\r\n        }\r\n        row.data(row_data);\r\n    });\r\n\r\n    // $('#var_view_modal_body').html(body_html);\r\n    var_view_modal.modal('show');\r\n}\r\n\r\n\r\nfunction redraw_table(var_import_table) {\r\n    var_import_table.draw('full-hold');\r\n}\r\n\r\n\r\nfunction modify_row_by_action(row, action, redraw = true, store = true) {\r\n    let data = row.data();\r\n    if ((action === 'source') && (data.action !== 'source')) {\r\n        if (typeof(data.source.name) !== 'undefined') {\r\n            data.result = data.source;\r\n            data.action = 'source';\r\n        }\r\n    } else if ((action === 'target') && (data.action !== 'target')) {\r\n        if (typeof(data.target.name) !== 'undefined') {\r\n            data.result = data.target;\r\n            data.action = 'target';\r\n        }\r\n    } else if (action === 'skip') {\r\n        data.result = data.target;\r\n        data.action =  (typeof(data.target.name) !== 'undefined' ? 'target' : 'skipped');\r\n    }\r\n\r\n    for (var key in data.available_constraints) {\r\n        let constraint = data.available_constraints[key];\r\n        data.available_constraints[key].to_result = constraint.origin === action;\r\n    }\r\n\r\n    if (redraw) {\r\n        row.data(data).draw('full-hold');\r\n    } else {\r\n        row.data(data);\r\n    }\r\n    if (store) {\r\n        store_changes(data);\r\n    }\r\n}\r\n\r\n\r\nfunction get_selected_vars(variables_table) {\r\n    let selected_vars = [];\r\n    variables_table.rows( {selected:true} ).every( function () {\r\n        let d = this.data();\r\n        selected_vars.push(d['name']);\r\n    });\r\n    return selected_vars;\r\n}\r\n\r\n\r\nfunction apply_multiselect_action(var_import_table, action) {\r\n    var_import_table.rows( {selected:true} ).every( function () {\r\n        modify_row_by_action(this, action, false, false);\r\n    });\r\n    // redraw_table(var_import_table);\r\n    store_changes();\r\n}\r\n\r\n\r\nfunction store_modal(var_table, target_row) {\r\n    let var_view_modal = $('#variable_modal');\r\n    let type_by_modal = $('#variable_type').val();\r\n    let value_by_modal = $('#variable_value').val();\r\n    let table_data = target_row.data();\r\n    // First check if we have changes.\r\n    let changes = false;\r\n    if (table_data.result.type !== type_by_modal) {\r\n        changes = true;\r\n        table_data.result.type = type_by_modal;\r\n    }\r\n    if ((table_data.result.type === 'CONST' || table_data.result.type === 'ENUMERATOR') &&\r\n        (table_data.result.const_val !== value_by_modal)) {\r\n        changes = true;\r\n        table_data.result.const_val = value_by_modal;\r\n    }\r\n    if (changes || global_changes) {\r\n        table_data.action = 'custom';\r\n        // Sync with backend.\r\n        var_view_modal.LoadingOverlay('show');\r\n        $.post( \"api/\" + session_id + \"/store_variable\",\r\n            {\r\n                row: JSON.stringify(table_data)\r\n            },\r\n            // Update var table on success or show an error message.\r\n            function( data ) {\r\n                var_view_modal.LoadingOverlay('hide', true);\r\n                if (data['success'] === false) {\r\n                    alert(data['errormsg']);\r\n                } else {\r\n                    target_row.data(table_data).draw('full-hold');\r\n                    var_view_modal.modal('hide');\r\n                    $(target_row.node()).effect(\"highlight\", {color: 'green'}, 800);\r\n                }\r\n        });\r\n    } else {\r\n        var_view_modal.modal('hide');\r\n    }\r\n}\r\n\r\n\r\nfunction store_changes(data = false) {\r\n    let body = $('body');\r\n    body.LoadingOverlay('show');\r\n\r\n    // Fetch relevant changes\r\n    let rows = Object();\r\n    if (!data) {\r\n        $( '#var_import_table' ).DataTable().rows( {selected:true} ).every( function () {\r\n            let row = this.data();\r\n            rows[row.name] = {\r\n                action: row.action\r\n            };\r\n        });\r\n    } else {\r\n        rows[data.name] = {\r\n            action: data.action\r\n        }\r\n    }\r\n\r\n    rows = JSON.stringify(rows);\r\n\r\n    // Send changes to backend.\r\n    $.post( \"api/\" + session_id + \"/store_table\",\r\n        {\r\n            rows: rows\r\n        },\r\n        // Update requirements table on success or show an error message.\r\n        function( data ) {\r\n            body.LoadingOverlay('hide', true);\r\n            if (data['success'] === false) {\r\n                alert(data['errormsg']);\r\n            }\r\n    });\r\n}\r\n\r\n\r\nfunction apply_import(var_import_table) {\r\n    let body = $('body');\r\n    body.LoadingOverlay('show');\r\n\r\n    // Send changes to backend.\r\n    $.post( \"api/\" + session_id + \"/apply_import\",\r\n        {},\r\n        // Update requirements table on success or show an error message.\r\n        function( data ) {\r\n            body.LoadingOverlay('hide', true);\r\n            if (data['success'] === false) {\r\n                alert(data['errormsg']);\r\n            } else {\r\n                alert('Imported result variables.');\r\n            }\r\n    });\r\n}\r\n\r\n\r\nfunction delete_this_session() {\r\n    let body = $('body');\r\n    body.LoadingOverlay('show');\r\n\r\n    $.post( \"api/\" + session_id + \"/delete_me\",\r\n        {\r\n            id: session_id\r\n        },\r\n        // Hop to Hanfor root after successful deletion.\r\n        function( data ) {\r\n            body.LoadingOverlay('hide', true);\r\n            if (data['success'] === false) {\r\n                alert(data['errormsg']);\r\n            } else {\r\n                window.location.href = base_url + \"variables\";\r\n            }\r\n    });\r\n}\r\n\r\n\r\nfunction apply_tools_action(var_import_table, action) {\r\n    if (action === 'apply-import') {\r\n        apply_import(var_import_table);\r\n    }\r\n    if (action === 'delete-session') {\r\n        delete_this_session();\r\n    }\r\n}\r\n\r\n\r\n$(document).ready(function() {\r\n    // Prepare and load the variables table.\r\n    let var_import_table = $('#var_import_table').DataTable({\r\n        \"paging\": true,\r\n        \"stateSave\": true,\r\n        \"select\": {\r\n            style:    'os',\r\n            selector: 'td:first-child'\r\n        },\r\n        \"pageLength\": 200,\r\n        \"responsive\": true,\r\n        \"lengthMenu\": [[10, 50, 100, 500, -1], [10, 50, 100, 500, \"All\"]],\r\n        \"dom\": 'rt<\"container\"<\"row\"<\"col-md-6\"li><\"col-md-6\"p>>>',\r\n        \"ajax\": \"api/\" + session_id + \"/get_table_data\",\r\n        \"deferRender\": true,\r\n        \"rowId\": 'name',\r\n        \"columns\": [\r\n            {\r\n                // The mass selection column.\r\n                \"orderable\": false,\r\n                \"className\": 'select-checkbox',\r\n                \"targets\": [0],\r\n                \"data\": null,\r\n                \"defaultContent\": \"\"\r\n            },\r\n            {\r\n                // The actions column.\r\n                \"data\": function ( row, type, val, meta ) {\r\n                    return row;\r\n                },\r\n                \"targets\": [1],\r\n                \"orderable\": false,\r\n                \"render\": function ( data, type, row, meta ) {\r\n                    let result = '<div class=\"btn-group\" role=\"group\" aria-label=\"Basic example\">'\r\n                        + '<button type=\"button\" data-action=\"skip\" class=\"skip-btn btn btn-secondary'\r\n                        + (data.action === 'skipped' ? ' active' : '') + '\">Skip</button>'\r\n                        + '<button type=\"button\" data-action=\"source\" class=\"source-btn btn btn-secondary'\r\n                        + (data.action === 'source' ? ' active' : '') + '\">Source</button>'\r\n                        + '<button type=\"button\" data-action=\"target\" class=\"target-btn btn btn-secondary'\r\n                        + (data.action === 'target' ? ' active' : '') + '\">Target</button>'\r\n                        + '<button type=\"button\" data-action=\"custom\" class=\"custom-btn btn btn-secondary'\r\n                        + (data.action === 'custom' ? ' active' : '') + '\">Custom</button>'\r\n                        + '</div>';\r\n                    return result;\r\n                }\r\n            },\r\n            {\r\n                // The attributes column.\r\n                \"data\": function ( row, type, val, meta ) {\r\n                    return row;\r\n                },\r\n                \"targets\": [1],\r\n                \"render\": function ( data, type, row, meta ) {\r\n                    let result = ``;\r\n                    const has_source = typeof(data.source.name) !== 'undefined';\r\n                    const has_target = typeof(data.target.name) !== 'undefined';\r\n\r\n                    if (has_source && has_target) {\r\n                        result += '<span class=\"badge bg-info\">match_in_source_and_target</span>'\r\n                        if (data.source.type !== data.target.type) {\r\n                            result += '<span class=\"badge bg-info\">unmatched_types</span>'\r\n                        } else {\r\n                            result += '<span class=\"badge bg-info\">same_types</span>'\r\n                        }\r\n                    } else {\r\n                        if (!has_source) {\r\n                            result += '<span class=\"badge bg-info\">no_match_in_source</span>'\r\n                        }\r\n                        if (!has_target) {\r\n                            result += '<span class=\"badge bg-info\">no_match_in_target</span>'\r\n                        }\r\n                    }\r\n                    if (has_source && data.source.constraints.length > 0) {\r\n                        result += '<span class=\"badge bg-info\">source_has_constraints</span>'\r\n                    }\r\n                    if (has_target && data.target.constraints.length > 0) {\r\n                        result += '<span class=\"badge bg-info\">target_has_constraints</span>'\r\n                    }\r\n                    return result;\r\n                }\r\n            },\r\n            {\r\n                // The source column.\r\n                \"data\": function ( row, type, val, meta ) {\r\n                    return row.source;\r\n                },\r\n                \"targets\": [3],\r\n                \"render\": function ( data, type, row, meta ) {\r\n                    let result = '';\r\n                    if (typeof(data.name) !== 'undefined') {\r\n                        result = '<p class=\"var_link\" data-type=\"source\" style=\"cursor: pointer\"><code>' +\r\n                            data.name + '</code> <span class=\"badge bg-info\">' + data.type + '</span></p>';\r\n                    } else {\r\n                        result = 'No match.'\r\n                    }\r\n                    return result;\r\n                }\r\n            },\r\n            {\r\n                // The target column.\r\n                \"data\": function ( row, type, val, meta ) {\r\n                    return row.target;\r\n                },\r\n                \"targets\": [4],\r\n                \"order\": 'asc',\r\n                \"render\": function ( data, type, row, meta ) {\r\n                    let result = '';\r\n                    if (typeof(data.name) !== 'undefined') {\r\n                        result = '<p class=\"var_link\" data-type=\"target\" style=\"cursor: pointer\"><code>' +\r\n                            data.name + '</code><span class=\"badge bg-info\">' + data.type + '</span>';\r\n                    } else {\r\n                        result = 'No match.'\r\n                    }\r\n                    return result;\r\n                }\r\n\r\n            },\r\n            {\r\n                // The result column.\r\n                \"data\": function ( row, type, val, meta ) {\r\n                    return row.result;\r\n                },\r\n                \"targets\": [5],\r\n                \"render\": function ( data, type, row, meta ) {\r\n                    let result = '';\r\n                    if (typeof(data.name) !== 'undefined') {\r\n                        result = '<p class=\"var_link\" data-type=\"result\" style=\"cursor: pointer\"><code>' +\r\n                            data.name + '</code><span class=\"badge bg-info\">' + data.type + '</span>';\r\n                    } else {\r\n                        result = 'Skipped.'\r\n                    }\r\n                    return result;\r\n                }\r\n            }\r\n        ],\r\n        infoCallback: function( settings, start, end, max, total, pre ) {\r\n            var api = this.api();\r\n            var pageInfo = api.page.info();\r\n\r\n            $('#clear-all-filters-text').html(\"Showing \" + total +\"/\"+ pageInfo.recordsTotal + \". Clear all.\");\r\n\r\n            let result = \"Showing \" + start + \" to \" + end + \" of \" + total + \" entries\";\r\n            result += \" (filtered from \" + pageInfo.recordsTotal + \" total entries).\";\r\n\r\n            return result;\r\n        },\r\n        initComplete : function() {\r\n            $('#search_bar').val(var_import_search_string);\r\n\r\n            update_search();\r\n\r\n            // Enable Hanfor specific table filtering.\r\n            $.fn.dataTable.ext.search.push(\r\n                function( settings, data, dataIndex ) {\r\n                    // data contains the row. data[0] is the content of the first column in the actual row.\r\n                    // Return true to include the row into the data. false to exclude.\r\n                    return evaluate_search(data);\r\n                }\r\n            );\r\n\r\n            this.api().draw();\r\n\r\n        }\r\n    });\r\n    new $.fn.dataTable.ColReorder(var_import_table, {});\r\n\r\n    // Bind big custom searchbar to search the table.\r\n    $('#search_bar').keypress(function(e) {\r\n        if(e.which === 13) { // Search on enter.\r\n            update_search();\r\n            var_import_table.draw();\r\n        }\r\n    });\r\n\r\n    let var_import_table_body = $('#var_import_table tbody');\r\n\r\n    // Add listener for variable link to modal.\r\n    var_import_table_body.on('click', '.var_link', function (event) {\r\n        // prevent body to be scrolled to the top.\r\n        event.preventDefault();\r\n        let data = var_import_table.row( $(this).parents('tr') ).data();\r\n        let type = $(this).attr('data-type');\r\n        load_modal(data, var_import_table, type);\r\n    });\r\n    \r\n    $('#save_variable_modal').click(function () {\r\n        let name = $(this).attr('data-name');\r\n        let row = var_import_table.row('#' + name);\r\n        store_modal(var_import_table, row);\r\n    });\r\n\r\n    $('#variable_type').on('change, focusout, keyup', function () {\r\n        let var_value_form = $('#variable_value_form_group');\r\n        if (['CONST', 'ENUMERATOR'].includes($( this ).val())) {\r\n            var_value_form.show();\r\n        } else {\r\n            var_value_form.hide();\r\n        }\r\n    });\r\n\r\n    // Add listener for table row action buttons.\r\n    var_import_table_body.on('click', '.target-btn, .source-btn, .skip-btn', function (event) {\r\n        // prevent body to be scrolled to the top.\r\n        event.preventDefault();\r\n        let row = var_import_table.row( $(this).parents('tr') );\r\n        let action = $(this).attr('data-action');\r\n        modify_row_by_action(row, action);\r\n    });\r\n\r\n    // Multiselect. Select single rows.\r\n    $('.select-all-button').on('click', function (e) {\r\n        // Toggle selection on\r\n        if ($( this ).hasClass('btn-secondary')) {\r\n            var_import_table.rows( {page:'current'} ).select();\r\n        }\r\n        else { // Toggle selection off\r\n            var_import_table.rows( {page:'current'} ).deselect();\r\n        }\r\n        // Toggle button state.\r\n        $('.select-all-button').toggleClass('btn-secondary btn-primary');\r\n    });\r\n\r\n    // Multiselect action buttons\r\n    $('.action-btn').click(function (e) {\r\n        apply_multiselect_action(var_import_table, $(this).attr('data-action'));\r\n    });\r\n\r\n    // Buttons that must be confirmed\r\n    // $('#delete_session_button').confirmation({\r\n    //   rootSelector: '#delete_session_button'\r\n    // });\r\n\r\n    // Tools Buttons\r\n    $('#delete_session_button').bootstrapConfirmButton({\r\n        onConfirm: function () {\r\n            apply_tools_action(var_import_table, $(this).attr('data-action'))\r\n        }\r\n    })\r\n\r\n    $('#apply_import_btn').click(function () {\r\n        apply_tools_action(var_import_table, $(this).attr('data-action'));\r\n    });\r\n\r\n    // Toggle \"Select all rows to `off` on user specific selection.\"\r\n    var_import_table.on( 'user-select', function ( ) {\r\n        let select_buttons = $('.select-all-button');\r\n        select_buttons.removeClass('btn-primary');\r\n        select_buttons.addClass('btn-secondary ');\r\n    });\r\n\r\n    // Clear all applied searches.\r\n    $('.clear-all-filters').click(function () {\r\n        $('#search_bar').val('').effect(\"highlight\", {color: 'green'}, 500);\r\n        update_search();\r\n        var_import_table.draw();\r\n    });\r\n} );\n\n//# sourceURL=webpack://hanfor/./js/variable-import.js?");

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