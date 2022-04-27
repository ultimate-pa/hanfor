/*
 * ATTENTION: An "eval-source-map" devtool has been used.
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file with attached SourceMaps in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./js/tags.js":
/*!********************!*\
  !*** ./js/tags.js ***!
  \********************/
/***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {

eval("/* provided dependency */ var $ = __webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\");\n/* provided dependency */ var jQuery = __webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\");\n__webpack_require__(/*! gasparesganga-jquery-loading-overlay */ \"./node_modules/gasparesganga-jquery-loading-overlay/src/loadingoverlay.js\");\n__webpack_require__(/*! bootstrap */ \"./node_modules/bootstrap/dist/js/bootstrap.js\");\n__webpack_require__(/*! bootstrap-confirmation2 */ \"./node_modules/bootstrap-confirmation2/dist/bootstrap-confirmation.js\");\n__webpack_require__(/*! datatables.net-bs4 */ \"./node_modules/datatables.net-bs4/js/dataTables.bootstrap4.js\");\n__webpack_require__(/*! jquery-ui/ui/widgets/autocomplete */ \"./node_modules/jquery-ui/ui/widgets/autocomplete.js\");\n__webpack_require__(/*! jquery-ui/ui/effects/effect-highlight */ \"./node_modules/jquery-ui/ui/effects/effect-highlight.js\");\n__webpack_require__(/*! ./bootstrap-tokenfield.js */ \"./js/bootstrap-tokenfield.js\");\n__webpack_require__(/*! awesomplete */ \"./node_modules/awesomplete/awesomplete.js\");\n__webpack_require__(/*! awesomplete/awesomplete.css */ \"./node_modules/awesomplete/awesomplete.css\");\n__webpack_require__(/*! datatables.net-colreorderwithresize-npm */ \"./node_modules/datatables.net-colreorderwithresize-npm/ColReorderWithResize.js\");\n\nconst autosize = __webpack_require__(/*! autosize */ \"./node_modules/autosize/dist/autosize.js\");\nconst { SearchNode } = __webpack_require__(/*! ./datatables-advanced-search.js */ \"./js/datatables-advanced-search.js\");\nlet tag_search_string = sessionStorage.getItem('tag_search_string');\nlet search_autocomplete = [\n    \":AND:\",\n    \":OR:\",\n    \":NOT:\",\n    \":COL_INDEX_00:\",\n    \":COL_INDEX_01:\",\n    \":COL_INDEX_02:\",\n];\n\n/**\n * Update the search expression tree.\n */\nfunction update_search() {\n    tag_search_string = $('#search_bar').val().trim();\n    sessionStorage.setItem('tag_search_string', tag_search_string);\n    search_tree = SearchNode.fromQuery(tag_search_string);\n}\n\n\nfunction evaluate_search(data){\n    return search_tree.evaluate(data, [true, true, true]);\n}\n\n\n/**\n * Store the currently active (in the modal) tag.\n * @param tags_datatable\n */\nfunction store_tag(tags_datatable) {\n    let tag_modal_content = $('.modal-content');\n    tag_modal_content.LoadingOverlay('show');\n\n    // Get data.\n    let tag_name = $('#tag_name').val();\n    let tag_name_old = $('#tag_name_old').val();\n    let occurences = $('#occurences').val();\n    let tag_color = $('#tag_color').val();\n    let associated_row_id = parseInt($('#modal_associated_row_index').val());\n    let tag_description = $('#tag-description').val();\n\n    // Store the tag.\n    $.post( \"api/tag/update\",\n        {\n            name: tag_name,\n            name_old: tag_name_old,\n            occurences: occurences,\n            color: tag_color,\n            description: tag_description\n        },\n        // Update tag table on success or show an error message.\n        function( data ) {\n            tag_modal_content.LoadingOverlay('hide', true);\n            if (data['success'] === false) {\n                alert(data['errormsg']);\n            } else {\n                if (data.rebuild_table) {\n                    location.reload();\n                } else {\n                    tags_datatable.row(associated_row_id).data(data.data).draw();\n                    $('#tag_modal').modal('hide');\n                }\n            }\n    });\n}\n\nfunction add_tag_row() {\n    var counter = 1;\n    jQuery('#add_tag').click(function(event){\n    event.preventDefault();\n    counter++;\n    var newRow = jQuery('<tr><td><input type=\"text\" name=\"first_name' +\n        counter + '\"/></td><td><input type=\"text\" name=\"last_name' +\n        counter + '\"/></td></tr>');\n    jQuery('table.authors-list').append(newRow);\n});\n}\nfunction delete_tag(name) {\n    let tag_modal_content = $('.modal-content');\n    tag_modal_content.LoadingOverlay('show');\n\n    let tag_name = $('#tag_name').val();\n    let occurences = $('#occurences').val();\n    $.ajax({\n      type: \"DELETE\",\n      url: \"api/tag/del_tag\",\n      data: {name: tag_name, occurences: occurences},\n      success: function (data) {\n        tag_modal_content.LoadingOverlay('hide', true);\n            if (data['success'] === false) {\n                alert(data['errormsg']);\n            } else {\n                if (data.rebuild_table) {\n                    location.reload();\n                } else {\n                    tags_datatable.row(associated_row_id).data(data.data).draw();\n                    $('#tag_modal').modal('hide');\n                }\n            }\n      }\n    });\n}\n\n$(document).ready(function() {\n    // Prepare and load the tags table.\n    let tags_table = $('#tags_table');\n    let tags_datatable = tags_table.DataTable({\n        \"paging\": true,\n        \"stateSave\": true,\n        \"pageLength\": 50,\n        \"responsive\": true,\n        \"lengthMenu\": [[10, 50, 100, 500, -1], [10, 50, 100, 500, \"All\"]],\n        \"dom\": 'rt<\"container\"<\"row\"<\"col-md-6\"li><\"col-md-6\"p>>>',\n        \"ajax\": \"api/tag/gets\",\n        \"deferRender\": true,\n        \"columns\": [\n            {\n                \"data\": \"name\",\n                \"render\": function ( data, type, row, meta ) {\n                    result = '<a class=\"modal-opener\" href=\"#\">' + data + '</span></br>';\n                    return result;\n                }\n            },\n            {\n                \"data\": \"description\",\n                \"render\": function ( data, type, row, meta ) {\n                    result = '<div class=\"white-space-pre\">' + data + '</div>';\n                    return result;\n                }\n\n            },\n            {\n                \"data\": \"used_by\",\n                \"render\": function ( data, type, row, meta ) {\n                    let result = '';\n                    $(data).each(function (id, name) {\n                        if (name.length > 0) {\n                            search_query = '?command=search&col=2&q=%5C%22' + name + '%5C%22';\n                            result += '<span class=\"badge badge-info\" style=\"background-color: ' + row.color +'\">' +\n                                '<a href=\"' + base_url + search_query + '\" target=\"_blank\">' + name + '</a>' +\n                                '</span> ';\n                        }\n                    });\n                    if (data.length > 1 && result.length > 0) {\n                        const search_all = '?command=search&col=5&q=' + row.name;\n                        result += '<span class=\"badge badge-info\" style=\"background-color: #4275d8\">' +\n                            '<a href=\"./' + search_all + '\" target=\"_blank\">Show all</a>' +\n                            '</span> ';\n                    }\n                    return result;\n                }\n            },\n            {\n                \"data\": \"used_by\",\n                \"visible\": false,\n                \"searchable\": false,\n                \"render\": function ( data, type, row, meta ) {\n                    result = '';\n                    $(data).each(function (id, name) {\n                        if (name.length > 0) {\n                            if (result.length > 1) {\n                                result += ', '\n                            }\n                            result += name;\n                        }\n                    });\n                    return result;\n                }\n            }\n        ],\n        initComplete : function() {\n            $('#search_bar').val(tag_search_string);\n            update_search();\n\n            // Enable Hanfor specific table filtering.\n            $.fn.dataTable.ext.search.push(\n                function( settings, data, dataIndex ) {\n                    // data contains the row. data[0] is the content of the first column in the actual row.\n                    // Return true to include the row into the data. false to exclude.\n                    return evaluate_search(data);\n                }\n            );\n            this.api().draw();\n        }\n    });\n    tags_datatable.column(3).visible(false);\n    new $.fn.dataTable.ColReorder(tags_datatable, {});\n\n    let search_bar = $( \"#search_bar\" );\n    // Bind big custom searchbar to search the table.\n    search_bar.keypress(function(e){\n        if(e.which === 13) { // Search on enter.\n            update_search();\n            tags_datatable.draw();\n        }\n    });\n\n    new Awesomplete(search_bar[0], {\n        filter: function(text, input) {\n            let result = false;\n            // If we have an uneven number of \":\"\n            // We check if we have a match in the input tail starting from the last \":\"\n            if ((input.split(\":\").length-1)%2 === 1) {\n                result = Awesomplete.FILTER_CONTAINS(text, input.match(/[^:]*$/)[0]);\n            }\n            return result;\n        },\n        item: function(text, input) {\n            // Match inside \":\" enclosed item.\n            return Awesomplete.ITEM(text, input.match(/(:)([\\S]*$)/)[2]);\n        },\n        replace: function(text) {\n            // Cut of the tail starting from the last \":\" and replace by item text.\n            const before = this.input.value.match(/(.*)(:(?!.*:).*$)/)[1];\n            this.input.value = before + text;\n        },\n        list: search_autocomplete,\n        minChars: 1,\n        autoFirst: true\n    });\n\n    // Add listener for tag link to modal.\n    tags_table.find('tbody').on('click', 'a.modal-opener', function (event) {\n        // prevent body to be scrolled to the top.\n        event.preventDefault();\n\n        // Get row data\n        let data = tags_datatable.row($(event.target).parent()).data();\n        let row_id = tags_datatable.row($(event.target).parent()).index();\n\n        // Prepare tag modal\n        let tag_modal_content = $('.modal-content');\n        $('#tag_modal').modal('show');\n        $('#modal_associated_row_index').val(row_id);\n\n        // Meta information\n        $('#tag_name_old').val(data.name);\n        $('#occurences').val(data.used_by);\n\n        // Visible information\n        $('#tag_modal_title').html('Tag: ' + data.name);\n        $('#tag_name').val(data.name);\n        $('#tag_color').val(data.color);\n        $('#tag-description').val(data.description);\n\n        tag_modal_content.LoadingOverlay('hide');\n    });\n\n    // Store changes on tag on save.\n    $('#save_tag_modal').click(function () {\n        store_tag(tags_datatable);\n    });\n\n    $('.delete_tag').confirmation({\n      rootSelector: '.delete_tag'\n    }).click(function () {\n        delete_tag( $(this).attr('name') );\n    });\n\n    autosize($('#tag-description'));\n\n    $('#tag_modal').on('shown.bs.modal', function (e) {\n        autosize.update($('#tag-description'));\n    });\n\n    $('.clear-all-filters').click(function () {\n        $('#search_bar').val('').effect(\"highlight\", {color: 'green'}, 500);\n        update_search();\n        tags_datatable.draw();\n    });\n} );\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9qcy90YWdzLmpzLmpzIiwibWFwcGluZ3MiOiI7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL2hhbmZvci8uL2pzL3RhZ3MuanM/NDFhMyJdLCJzb3VyY2VzQ29udGVudCI6WyJyZXF1aXJlKCdnYXNwYXJlc2dhbmdhLWpxdWVyeS1sb2FkaW5nLW92ZXJsYXknKTtcbnJlcXVpcmUoJ2Jvb3RzdHJhcCcpO1xucmVxdWlyZSgnYm9vdHN0cmFwLWNvbmZpcm1hdGlvbjInKTtcbnJlcXVpcmUoJ2RhdGF0YWJsZXMubmV0LWJzNCcpO1xucmVxdWlyZSgnanF1ZXJ5LXVpL3VpL3dpZGdldHMvYXV0b2NvbXBsZXRlJyk7XG5yZXF1aXJlKCdqcXVlcnktdWkvdWkvZWZmZWN0cy9lZmZlY3QtaGlnaGxpZ2h0Jyk7XG5yZXF1aXJlKCcuL2Jvb3RzdHJhcC10b2tlbmZpZWxkLmpzJyk7XG5yZXF1aXJlKCdhd2Vzb21wbGV0ZScpO1xucmVxdWlyZSgnYXdlc29tcGxldGUvYXdlc29tcGxldGUuY3NzJyk7XG5yZXF1aXJlKCdkYXRhdGFibGVzLm5ldC1jb2xyZW9yZGVyd2l0aHJlc2l6ZS1ucG0nKTtcblxuY29uc3QgYXV0b3NpemUgPSByZXF1aXJlKCdhdXRvc2l6ZScpO1xuY29uc3QgeyBTZWFyY2hOb2RlIH0gPSByZXF1aXJlKCcuL2RhdGF0YWJsZXMtYWR2YW5jZWQtc2VhcmNoLmpzJyk7XG5sZXQgdGFnX3NlYXJjaF9zdHJpbmcgPSBzZXNzaW9uU3RvcmFnZS5nZXRJdGVtKCd0YWdfc2VhcmNoX3N0cmluZycpO1xubGV0IHNlYXJjaF9hdXRvY29tcGxldGUgPSBbXG4gICAgXCI6QU5EOlwiLFxuICAgIFwiOk9SOlwiLFxuICAgIFwiOk5PVDpcIixcbiAgICBcIjpDT0xfSU5ERVhfMDA6XCIsXG4gICAgXCI6Q09MX0lOREVYXzAxOlwiLFxuICAgIFwiOkNPTF9JTkRFWF8wMjpcIixcbl07XG5cbi8qKlxuICogVXBkYXRlIHRoZSBzZWFyY2ggZXhwcmVzc2lvbiB0cmVlLlxuICovXG5mdW5jdGlvbiB1cGRhdGVfc2VhcmNoKCkge1xuICAgIHRhZ19zZWFyY2hfc3RyaW5nID0gJCgnI3NlYXJjaF9iYXInKS52YWwoKS50cmltKCk7XG4gICAgc2Vzc2lvblN0b3JhZ2Uuc2V0SXRlbSgndGFnX3NlYXJjaF9zdHJpbmcnLCB0YWdfc2VhcmNoX3N0cmluZyk7XG4gICAgc2VhcmNoX3RyZWUgPSBTZWFyY2hOb2RlLmZyb21RdWVyeSh0YWdfc2VhcmNoX3N0cmluZyk7XG59XG5cblxuZnVuY3Rpb24gZXZhbHVhdGVfc2VhcmNoKGRhdGEpe1xuICAgIHJldHVybiBzZWFyY2hfdHJlZS5ldmFsdWF0ZShkYXRhLCBbdHJ1ZSwgdHJ1ZSwgdHJ1ZV0pO1xufVxuXG5cbi8qKlxuICogU3RvcmUgdGhlIGN1cnJlbnRseSBhY3RpdmUgKGluIHRoZSBtb2RhbCkgdGFnLlxuICogQHBhcmFtIHRhZ3NfZGF0YXRhYmxlXG4gKi9cbmZ1bmN0aW9uIHN0b3JlX3RhZyh0YWdzX2RhdGF0YWJsZSkge1xuICAgIGxldCB0YWdfbW9kYWxfY29udGVudCA9ICQoJy5tb2RhbC1jb250ZW50Jyk7XG4gICAgdGFnX21vZGFsX2NvbnRlbnQuTG9hZGluZ092ZXJsYXkoJ3Nob3cnKTtcblxuICAgIC8vIEdldCBkYXRhLlxuICAgIGxldCB0YWdfbmFtZSA9ICQoJyN0YWdfbmFtZScpLnZhbCgpO1xuICAgIGxldCB0YWdfbmFtZV9vbGQgPSAkKCcjdGFnX25hbWVfb2xkJykudmFsKCk7XG4gICAgbGV0IG9jY3VyZW5jZXMgPSAkKCcjb2NjdXJlbmNlcycpLnZhbCgpO1xuICAgIGxldCB0YWdfY29sb3IgPSAkKCcjdGFnX2NvbG9yJykudmFsKCk7XG4gICAgbGV0IGFzc29jaWF0ZWRfcm93X2lkID0gcGFyc2VJbnQoJCgnI21vZGFsX2Fzc29jaWF0ZWRfcm93X2luZGV4JykudmFsKCkpO1xuICAgIGxldCB0YWdfZGVzY3JpcHRpb24gPSAkKCcjdGFnLWRlc2NyaXB0aW9uJykudmFsKCk7XG5cbiAgICAvLyBTdG9yZSB0aGUgdGFnLlxuICAgICQucG9zdCggXCJhcGkvdGFnL3VwZGF0ZVwiLFxuICAgICAgICB7XG4gICAgICAgICAgICBuYW1lOiB0YWdfbmFtZSxcbiAgICAgICAgICAgIG5hbWVfb2xkOiB0YWdfbmFtZV9vbGQsXG4gICAgICAgICAgICBvY2N1cmVuY2VzOiBvY2N1cmVuY2VzLFxuICAgICAgICAgICAgY29sb3I6IHRhZ19jb2xvcixcbiAgICAgICAgICAgIGRlc2NyaXB0aW9uOiB0YWdfZGVzY3JpcHRpb25cbiAgICAgICAgfSxcbiAgICAgICAgLy8gVXBkYXRlIHRhZyB0YWJsZSBvbiBzdWNjZXNzIG9yIHNob3cgYW4gZXJyb3IgbWVzc2FnZS5cbiAgICAgICAgZnVuY3Rpb24oIGRhdGEgKSB7XG4gICAgICAgICAgICB0YWdfbW9kYWxfY29udGVudC5Mb2FkaW5nT3ZlcmxheSgnaGlkZScsIHRydWUpO1xuICAgICAgICAgICAgaWYgKGRhdGFbJ3N1Y2Nlc3MnXSA9PT0gZmFsc2UpIHtcbiAgICAgICAgICAgICAgICBhbGVydChkYXRhWydlcnJvcm1zZyddKTtcbiAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgaWYgKGRhdGEucmVidWlsZF90YWJsZSkge1xuICAgICAgICAgICAgICAgICAgICBsb2NhdGlvbi5yZWxvYWQoKTtcbiAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICB0YWdzX2RhdGF0YWJsZS5yb3coYXNzb2NpYXRlZF9yb3dfaWQpLmRhdGEoZGF0YS5kYXRhKS5kcmF3KCk7XG4gICAgICAgICAgICAgICAgICAgICQoJyN0YWdfbW9kYWwnKS5tb2RhbCgnaGlkZScpO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH1cbiAgICB9KTtcbn1cblxuZnVuY3Rpb24gYWRkX3RhZ19yb3coKSB7XG4gICAgdmFyIGNvdW50ZXIgPSAxO1xuICAgIGpRdWVyeSgnI2FkZF90YWcnKS5jbGljayhmdW5jdGlvbihldmVudCl7XG4gICAgZXZlbnQucHJldmVudERlZmF1bHQoKTtcbiAgICBjb3VudGVyKys7XG4gICAgdmFyIG5ld1JvdyA9IGpRdWVyeSgnPHRyPjx0ZD48aW5wdXQgdHlwZT1cInRleHRcIiBuYW1lPVwiZmlyc3RfbmFtZScgK1xuICAgICAgICBjb3VudGVyICsgJ1wiLz48L3RkPjx0ZD48aW5wdXQgdHlwZT1cInRleHRcIiBuYW1lPVwibGFzdF9uYW1lJyArXG4gICAgICAgIGNvdW50ZXIgKyAnXCIvPjwvdGQ+PC90cj4nKTtcbiAgICBqUXVlcnkoJ3RhYmxlLmF1dGhvcnMtbGlzdCcpLmFwcGVuZChuZXdSb3cpO1xufSk7XG59XG5mdW5jdGlvbiBkZWxldGVfdGFnKG5hbWUpIHtcbiAgICBsZXQgdGFnX21vZGFsX2NvbnRlbnQgPSAkKCcubW9kYWwtY29udGVudCcpO1xuICAgIHRhZ19tb2RhbF9jb250ZW50LkxvYWRpbmdPdmVybGF5KCdzaG93Jyk7XG5cbiAgICBsZXQgdGFnX25hbWUgPSAkKCcjdGFnX25hbWUnKS52YWwoKTtcbiAgICBsZXQgb2NjdXJlbmNlcyA9ICQoJyNvY2N1cmVuY2VzJykudmFsKCk7XG4gICAgJC5hamF4KHtcbiAgICAgIHR5cGU6IFwiREVMRVRFXCIsXG4gICAgICB1cmw6IFwiYXBpL3RhZy9kZWxfdGFnXCIsXG4gICAgICBkYXRhOiB7bmFtZTogdGFnX25hbWUsIG9jY3VyZW5jZXM6IG9jY3VyZW5jZXN9LFxuICAgICAgc3VjY2VzczogZnVuY3Rpb24gKGRhdGEpIHtcbiAgICAgICAgdGFnX21vZGFsX2NvbnRlbnQuTG9hZGluZ092ZXJsYXkoJ2hpZGUnLCB0cnVlKTtcbiAgICAgICAgICAgIGlmIChkYXRhWydzdWNjZXNzJ10gPT09IGZhbHNlKSB7XG4gICAgICAgICAgICAgICAgYWxlcnQoZGF0YVsnZXJyb3Jtc2cnXSk7XG4gICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgIGlmIChkYXRhLnJlYnVpbGRfdGFibGUpIHtcbiAgICAgICAgICAgICAgICAgICAgbG9jYXRpb24ucmVsb2FkKCk7XG4gICAgICAgICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgICAgICAgICAgdGFnc19kYXRhdGFibGUucm93KGFzc29jaWF0ZWRfcm93X2lkKS5kYXRhKGRhdGEuZGF0YSkuZHJhdygpO1xuICAgICAgICAgICAgICAgICAgICAkKCcjdGFnX21vZGFsJykubW9kYWwoJ2hpZGUnKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICB9XG4gICAgfSk7XG59XG5cbiQoZG9jdW1lbnQpLnJlYWR5KGZ1bmN0aW9uKCkge1xuICAgIC8vIFByZXBhcmUgYW5kIGxvYWQgdGhlIHRhZ3MgdGFibGUuXG4gICAgbGV0IHRhZ3NfdGFibGUgPSAkKCcjdGFnc190YWJsZScpO1xuICAgIGxldCB0YWdzX2RhdGF0YWJsZSA9IHRhZ3NfdGFibGUuRGF0YVRhYmxlKHtcbiAgICAgICAgXCJwYWdpbmdcIjogdHJ1ZSxcbiAgICAgICAgXCJzdGF0ZVNhdmVcIjogdHJ1ZSxcbiAgICAgICAgXCJwYWdlTGVuZ3RoXCI6IDUwLFxuICAgICAgICBcInJlc3BvbnNpdmVcIjogdHJ1ZSxcbiAgICAgICAgXCJsZW5ndGhNZW51XCI6IFtbMTAsIDUwLCAxMDAsIDUwMCwgLTFdLCBbMTAsIDUwLCAxMDAsIDUwMCwgXCJBbGxcIl1dLFxuICAgICAgICBcImRvbVwiOiAncnQ8XCJjb250YWluZXJcIjxcInJvd1wiPFwiY29sLW1kLTZcImxpPjxcImNvbC1tZC02XCJwPj4+JyxcbiAgICAgICAgXCJhamF4XCI6IFwiYXBpL3RhZy9nZXRzXCIsXG4gICAgICAgIFwiZGVmZXJSZW5kZXJcIjogdHJ1ZSxcbiAgICAgICAgXCJjb2x1bW5zXCI6IFtcbiAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgICBcImRhdGFcIjogXCJuYW1lXCIsXG4gICAgICAgICAgICAgICAgXCJyZW5kZXJcIjogZnVuY3Rpb24gKCBkYXRhLCB0eXBlLCByb3csIG1ldGEgKSB7XG4gICAgICAgICAgICAgICAgICAgIHJlc3VsdCA9ICc8YSBjbGFzcz1cIm1vZGFsLW9wZW5lclwiIGhyZWY9XCIjXCI+JyArIGRhdGEgKyAnPC9zcGFuPjwvYnI+JztcbiAgICAgICAgICAgICAgICAgICAgcmV0dXJuIHJlc3VsdDtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9LFxuICAgICAgICAgICAge1xuICAgICAgICAgICAgICAgIFwiZGF0YVwiOiBcImRlc2NyaXB0aW9uXCIsXG4gICAgICAgICAgICAgICAgXCJyZW5kZXJcIjogZnVuY3Rpb24gKCBkYXRhLCB0eXBlLCByb3csIG1ldGEgKSB7XG4gICAgICAgICAgICAgICAgICAgIHJlc3VsdCA9ICc8ZGl2IGNsYXNzPVwid2hpdGUtc3BhY2UtcHJlXCI+JyArIGRhdGEgKyAnPC9kaXY+JztcbiAgICAgICAgICAgICAgICAgICAgcmV0dXJuIHJlc3VsdDtcbiAgICAgICAgICAgICAgICB9XG5cbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgICB7XG4gICAgICAgICAgICAgICAgXCJkYXRhXCI6IFwidXNlZF9ieVwiLFxuICAgICAgICAgICAgICAgIFwicmVuZGVyXCI6IGZ1bmN0aW9uICggZGF0YSwgdHlwZSwgcm93LCBtZXRhICkge1xuICAgICAgICAgICAgICAgICAgICBsZXQgcmVzdWx0ID0gJyc7XG4gICAgICAgICAgICAgICAgICAgICQoZGF0YSkuZWFjaChmdW5jdGlvbiAoaWQsIG5hbWUpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIGlmIChuYW1lLmxlbmd0aCA+IDApIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICBzZWFyY2hfcXVlcnkgPSAnP2NvbW1hbmQ9c2VhcmNoJmNvbD0yJnE9JTVDJTIyJyArIG5hbWUgKyAnJTVDJTIyJztcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICByZXN1bHQgKz0gJzxzcGFuIGNsYXNzPVwiYmFkZ2UgYmFkZ2UtaW5mb1wiIHN0eWxlPVwiYmFja2dyb3VuZC1jb2xvcjogJyArIHJvdy5jb2xvciArJ1wiPicgK1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAnPGEgaHJlZj1cIicgKyBiYXNlX3VybCArIHNlYXJjaF9xdWVyeSArICdcIiB0YXJnZXQ9XCJfYmxhbmtcIj4nICsgbmFtZSArICc8L2E+JyArXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICc8L3NwYW4+ICc7XG4gICAgICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgICAgICAgICBpZiAoZGF0YS5sZW5ndGggPiAxICYmIHJlc3VsdC5sZW5ndGggPiAwKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICBjb25zdCBzZWFyY2hfYWxsID0gJz9jb21tYW5kPXNlYXJjaCZjb2w9NSZxPScgKyByb3cubmFtZTtcbiAgICAgICAgICAgICAgICAgICAgICAgIHJlc3VsdCArPSAnPHNwYW4gY2xhc3M9XCJiYWRnZSBiYWRnZS1pbmZvXCIgc3R5bGU9XCJiYWNrZ3JvdW5kLWNvbG9yOiAjNDI3NWQ4XCI+JyArXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgJzxhIGhyZWY9XCIuLycgKyBzZWFyY2hfYWxsICsgJ1wiIHRhcmdldD1cIl9ibGFua1wiPlNob3cgYWxsPC9hPicgK1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICc8L3NwYW4+ICc7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICAgICAgcmV0dXJuIHJlc3VsdDtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9LFxuICAgICAgICAgICAge1xuICAgICAgICAgICAgICAgIFwiZGF0YVwiOiBcInVzZWRfYnlcIixcbiAgICAgICAgICAgICAgICBcInZpc2libGVcIjogZmFsc2UsXG4gICAgICAgICAgICAgICAgXCJzZWFyY2hhYmxlXCI6IGZhbHNlLFxuICAgICAgICAgICAgICAgIFwicmVuZGVyXCI6IGZ1bmN0aW9uICggZGF0YSwgdHlwZSwgcm93LCBtZXRhICkge1xuICAgICAgICAgICAgICAgICAgICByZXN1bHQgPSAnJztcbiAgICAgICAgICAgICAgICAgICAgJChkYXRhKS5lYWNoKGZ1bmN0aW9uIChpZCwgbmFtZSkge1xuICAgICAgICAgICAgICAgICAgICAgICAgaWYgKG5hbWUubGVuZ3RoID4gMCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgIGlmIChyZXN1bHQubGVuZ3RoID4gMSkge1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICByZXN1bHQgKz0gJywgJ1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICByZXN1bHQgKz0gbmFtZTtcbiAgICAgICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICAgICAgICAgIHJldHVybiByZXN1bHQ7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfVxuICAgICAgICBdLFxuICAgICAgICBpbml0Q29tcGxldGUgOiBmdW5jdGlvbigpIHtcbiAgICAgICAgICAgICQoJyNzZWFyY2hfYmFyJykudmFsKHRhZ19zZWFyY2hfc3RyaW5nKTtcbiAgICAgICAgICAgIHVwZGF0ZV9zZWFyY2goKTtcblxuICAgICAgICAgICAgLy8gRW5hYmxlIEhhbmZvciBzcGVjaWZpYyB0YWJsZSBmaWx0ZXJpbmcuXG4gICAgICAgICAgICAkLmZuLmRhdGFUYWJsZS5leHQuc2VhcmNoLnB1c2goXG4gICAgICAgICAgICAgICAgZnVuY3Rpb24oIHNldHRpbmdzLCBkYXRhLCBkYXRhSW5kZXggKSB7XG4gICAgICAgICAgICAgICAgICAgIC8vIGRhdGEgY29udGFpbnMgdGhlIHJvdy4gZGF0YVswXSBpcyB0aGUgY29udGVudCBvZiB0aGUgZmlyc3QgY29sdW1uIGluIHRoZSBhY3R1YWwgcm93LlxuICAgICAgICAgICAgICAgICAgICAvLyBSZXR1cm4gdHJ1ZSB0byBpbmNsdWRlIHRoZSByb3cgaW50byB0aGUgZGF0YS4gZmFsc2UgdG8gZXhjbHVkZS5cbiAgICAgICAgICAgICAgICAgICAgcmV0dXJuIGV2YWx1YXRlX3NlYXJjaChkYXRhKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICApO1xuICAgICAgICAgICAgdGhpcy5hcGkoKS5kcmF3KCk7XG4gICAgICAgIH1cbiAgICB9KTtcbiAgICB0YWdzX2RhdGF0YWJsZS5jb2x1bW4oMykudmlzaWJsZShmYWxzZSk7XG4gICAgbmV3ICQuZm4uZGF0YVRhYmxlLkNvbFJlb3JkZXIodGFnc19kYXRhdGFibGUsIHt9KTtcblxuICAgIGxldCBzZWFyY2hfYmFyID0gJCggXCIjc2VhcmNoX2JhclwiICk7XG4gICAgLy8gQmluZCBiaWcgY3VzdG9tIHNlYXJjaGJhciB0byBzZWFyY2ggdGhlIHRhYmxlLlxuICAgIHNlYXJjaF9iYXIua2V5cHJlc3MoZnVuY3Rpb24oZSl7XG4gICAgICAgIGlmKGUud2hpY2ggPT09IDEzKSB7IC8vIFNlYXJjaCBvbiBlbnRlci5cbiAgICAgICAgICAgIHVwZGF0ZV9zZWFyY2goKTtcbiAgICAgICAgICAgIHRhZ3NfZGF0YXRhYmxlLmRyYXcoKTtcbiAgICAgICAgfVxuICAgIH0pO1xuXG4gICAgbmV3IEF3ZXNvbXBsZXRlKHNlYXJjaF9iYXJbMF0sIHtcbiAgICAgICAgZmlsdGVyOiBmdW5jdGlvbih0ZXh0LCBpbnB1dCkge1xuICAgICAgICAgICAgbGV0IHJlc3VsdCA9IGZhbHNlO1xuICAgICAgICAgICAgLy8gSWYgd2UgaGF2ZSBhbiB1bmV2ZW4gbnVtYmVyIG9mIFwiOlwiXG4gICAgICAgICAgICAvLyBXZSBjaGVjayBpZiB3ZSBoYXZlIGEgbWF0Y2ggaW4gdGhlIGlucHV0IHRhaWwgc3RhcnRpbmcgZnJvbSB0aGUgbGFzdCBcIjpcIlxuICAgICAgICAgICAgaWYgKChpbnB1dC5zcGxpdChcIjpcIikubGVuZ3RoLTEpJTIgPT09IDEpIHtcbiAgICAgICAgICAgICAgICByZXN1bHQgPSBBd2Vzb21wbGV0ZS5GSUxURVJfQ09OVEFJTlModGV4dCwgaW5wdXQubWF0Y2goL1teOl0qJC8pWzBdKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgICAgIHJldHVybiByZXN1bHQ7XG4gICAgICAgIH0sXG4gICAgICAgIGl0ZW06IGZ1bmN0aW9uKHRleHQsIGlucHV0KSB7XG4gICAgICAgICAgICAvLyBNYXRjaCBpbnNpZGUgXCI6XCIgZW5jbG9zZWQgaXRlbS5cbiAgICAgICAgICAgIHJldHVybiBBd2Vzb21wbGV0ZS5JVEVNKHRleHQsIGlucHV0Lm1hdGNoKC8oOikoW1xcU10qJCkvKVsyXSk7XG4gICAgICAgIH0sXG4gICAgICAgIHJlcGxhY2U6IGZ1bmN0aW9uKHRleHQpIHtcbiAgICAgICAgICAgIC8vIEN1dCBvZiB0aGUgdGFpbCBzdGFydGluZyBmcm9tIHRoZSBsYXN0IFwiOlwiIGFuZCByZXBsYWNlIGJ5IGl0ZW0gdGV4dC5cbiAgICAgICAgICAgIGNvbnN0IGJlZm9yZSA9IHRoaXMuaW5wdXQudmFsdWUubWF0Y2goLyguKikoOig/IS4qOikuKiQpLylbMV07XG4gICAgICAgICAgICB0aGlzLmlucHV0LnZhbHVlID0gYmVmb3JlICsgdGV4dDtcbiAgICAgICAgfSxcbiAgICAgICAgbGlzdDogc2VhcmNoX2F1dG9jb21wbGV0ZSxcbiAgICAgICAgbWluQ2hhcnM6IDEsXG4gICAgICAgIGF1dG9GaXJzdDogdHJ1ZVxuICAgIH0pO1xuXG4gICAgLy8gQWRkIGxpc3RlbmVyIGZvciB0YWcgbGluayB0byBtb2RhbC5cbiAgICB0YWdzX3RhYmxlLmZpbmQoJ3Rib2R5Jykub24oJ2NsaWNrJywgJ2EubW9kYWwtb3BlbmVyJywgZnVuY3Rpb24gKGV2ZW50KSB7XG4gICAgICAgIC8vIHByZXZlbnQgYm9keSB0byBiZSBzY3JvbGxlZCB0byB0aGUgdG9wLlxuICAgICAgICBldmVudC5wcmV2ZW50RGVmYXVsdCgpO1xuXG4gICAgICAgIC8vIEdldCByb3cgZGF0YVxuICAgICAgICBsZXQgZGF0YSA9IHRhZ3NfZGF0YXRhYmxlLnJvdygkKGV2ZW50LnRhcmdldCkucGFyZW50KCkpLmRhdGEoKTtcbiAgICAgICAgbGV0IHJvd19pZCA9IHRhZ3NfZGF0YXRhYmxlLnJvdygkKGV2ZW50LnRhcmdldCkucGFyZW50KCkpLmluZGV4KCk7XG5cbiAgICAgICAgLy8gUHJlcGFyZSB0YWcgbW9kYWxcbiAgICAgICAgbGV0IHRhZ19tb2RhbF9jb250ZW50ID0gJCgnLm1vZGFsLWNvbnRlbnQnKTtcbiAgICAgICAgJCgnI3RhZ19tb2RhbCcpLm1vZGFsKCdzaG93Jyk7XG4gICAgICAgICQoJyNtb2RhbF9hc3NvY2lhdGVkX3Jvd19pbmRleCcpLnZhbChyb3dfaWQpO1xuXG4gICAgICAgIC8vIE1ldGEgaW5mb3JtYXRpb25cbiAgICAgICAgJCgnI3RhZ19uYW1lX29sZCcpLnZhbChkYXRhLm5hbWUpO1xuICAgICAgICAkKCcjb2NjdXJlbmNlcycpLnZhbChkYXRhLnVzZWRfYnkpO1xuXG4gICAgICAgIC8vIFZpc2libGUgaW5mb3JtYXRpb25cbiAgICAgICAgJCgnI3RhZ19tb2RhbF90aXRsZScpLmh0bWwoJ1RhZzogJyArIGRhdGEubmFtZSk7XG4gICAgICAgICQoJyN0YWdfbmFtZScpLnZhbChkYXRhLm5hbWUpO1xuICAgICAgICAkKCcjdGFnX2NvbG9yJykudmFsKGRhdGEuY29sb3IpO1xuICAgICAgICAkKCcjdGFnLWRlc2NyaXB0aW9uJykudmFsKGRhdGEuZGVzY3JpcHRpb24pO1xuXG4gICAgICAgIHRhZ19tb2RhbF9jb250ZW50LkxvYWRpbmdPdmVybGF5KCdoaWRlJyk7XG4gICAgfSk7XG5cbiAgICAvLyBTdG9yZSBjaGFuZ2VzIG9uIHRhZyBvbiBzYXZlLlxuICAgICQoJyNzYXZlX3RhZ19tb2RhbCcpLmNsaWNrKGZ1bmN0aW9uICgpIHtcbiAgICAgICAgc3RvcmVfdGFnKHRhZ3NfZGF0YXRhYmxlKTtcbiAgICB9KTtcblxuICAgICQoJy5kZWxldGVfdGFnJykuY29uZmlybWF0aW9uKHtcbiAgICAgIHJvb3RTZWxlY3RvcjogJy5kZWxldGVfdGFnJ1xuICAgIH0pLmNsaWNrKGZ1bmN0aW9uICgpIHtcbiAgICAgICAgZGVsZXRlX3RhZyggJCh0aGlzKS5hdHRyKCduYW1lJykgKTtcbiAgICB9KTtcblxuICAgIGF1dG9zaXplKCQoJyN0YWctZGVzY3JpcHRpb24nKSk7XG5cbiAgICAkKCcjdGFnX21vZGFsJykub24oJ3Nob3duLmJzLm1vZGFsJywgZnVuY3Rpb24gKGUpIHtcbiAgICAgICAgYXV0b3NpemUudXBkYXRlKCQoJyN0YWctZGVzY3JpcHRpb24nKSk7XG4gICAgfSk7XG5cbiAgICAkKCcuY2xlYXItYWxsLWZpbHRlcnMnKS5jbGljayhmdW5jdGlvbiAoKSB7XG4gICAgICAgICQoJyNzZWFyY2hfYmFyJykudmFsKCcnKS5lZmZlY3QoXCJoaWdobGlnaHRcIiwge2NvbG9yOiAnZ3JlZW4nfSwgNTAwKTtcbiAgICAgICAgdXBkYXRlX3NlYXJjaCgpO1xuICAgICAgICB0YWdzX2RhdGF0YWJsZS5kcmF3KCk7XG4gICAgfSk7XG59ICk7XG4iXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./js/tags.js\n");

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
/******/ 	/* webpack/runtime/global */
/******/ 	(() => {
/******/ 		__webpack_require__.g = (function() {
/******/ 			if (typeof globalThis === 'object') return globalThis;
/******/ 			try {
/******/ 				return this || new Function('return this')();
/******/ 			} catch (e) {
/******/ 				if (typeof window === 'object') return window;
/******/ 			}
/******/ 		})();
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
/******/ 			"tags": 0
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
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module depends on other loaded chunks and execution need to be delayed
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, ["commons"], () => (__webpack_require__("./js/tags.js")))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;