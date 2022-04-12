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

eval("/* provided dependency */ var $ = __webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\");\n/* provided dependency */ var jQuery = __webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\");\n__webpack_require__(/*! gasparesganga-jquery-loading-overlay */ \"./node_modules/gasparesganga-jquery-loading-overlay/src/loadingoverlay.js\");\r\n__webpack_require__(/*! bootstrap */ \"./node_modules/bootstrap/dist/js/bootstrap.js\");\r\n__webpack_require__(/*! bootstrap-confirmation2 */ \"./node_modules/bootstrap-confirmation2/dist/bootstrap-confirmation.js\");\r\n__webpack_require__(/*! datatables.net-bs4 */ \"./node_modules/datatables.net-bs4/js/dataTables.bootstrap4.js\");\r\n__webpack_require__(/*! jquery-ui/ui/widgets/autocomplete */ \"./node_modules/jquery-ui/ui/widgets/autocomplete.js\");\r\n__webpack_require__(/*! jquery-ui/ui/effects/effect-highlight */ \"./node_modules/jquery-ui/ui/effects/effect-highlight.js\");\r\n__webpack_require__(/*! ./bootstrap-tokenfield.js */ \"./js/bootstrap-tokenfield.js\");\r\n__webpack_require__(/*! awesomplete */ \"./node_modules/awesomplete/awesomplete.js\");\r\n__webpack_require__(/*! awesomplete/awesomplete.css */ \"./node_modules/awesomplete/awesomplete.css\");\r\n__webpack_require__(/*! datatables.net-colreorderwithresize-npm */ \"./node_modules/datatables.net-colreorderwithresize-npm/ColReorderWithResize.js\");\r\n\r\nconst autosize = __webpack_require__(/*! autosize */ \"./node_modules/autosize/dist/autosize.js\");\r\nconst { SearchNode } = __webpack_require__(/*! ./datatables-advanced-search.js */ \"./js/datatables-advanced-search.js\");\r\nlet tag_search_string = sessionStorage.getItem('tag_search_string');\r\nlet search_autocomplete = [\r\n    \":AND:\",\r\n    \":OR:\",\r\n    \":NOT:\",\r\n    \":COL_INDEX_00:\",\r\n    \":COL_INDEX_01:\",\r\n    \":COL_INDEX_02:\",\r\n];\r\n\r\n/**\r\n * Update the search expression tree.\r\n */\r\nfunction update_search() {\r\n    tag_search_string = $('#search_bar').val().trim();\r\n    sessionStorage.setItem('tag_search_string', tag_search_string);\r\n    search_tree = SearchNode.fromQuery(tag_search_string);\r\n}\r\n\r\n\r\nfunction evaluate_search(data){\r\n    return search_tree.evaluate(data, [true, true, true]);\r\n}\r\n\r\n\r\n/**\r\n * Store the currently active (in the modal) tag.\r\n * @param tags_datatable\r\n */\r\nfunction store_tag(tags_datatable) {\r\n    let tag_modal_content = $('.modal-content');\r\n    tag_modal_content.LoadingOverlay('show');\r\n\r\n    // Get data.\r\n    let tag_name = $('#tag_name').val();\r\n    let tag_name_old = $('#tag_name_old').val();\r\n    let occurences = $('#occurences').val();\r\n    let tag_color = $('#tag_color').val();\r\n    let associated_row_id = parseInt($('#modal_associated_row_index').val());\r\n    let tag_description = $('#tag-description').val();\r\n\r\n    // Store the tag.\r\n    $.post( \"api/tag/update\",\r\n        {\r\n            name: tag_name,\r\n            name_old: tag_name_old,\r\n            occurences: occurences,\r\n            color: tag_color,\r\n            description: tag_description\r\n        },\r\n        // Update tag table on success or show an error message.\r\n        function( data ) {\r\n            tag_modal_content.LoadingOverlay('hide', true);\r\n            if (data['success'] === false) {\r\n                alert(data['errormsg']);\r\n            } else {\r\n                if (data.rebuild_table) {\r\n                    location.reload();\r\n                } else {\r\n                    tags_datatable.row(associated_row_id).data(data.data).draw();\r\n                    $('#tag_modal').modal('hide');\r\n                }\r\n            }\r\n    });\r\n}\r\n\r\nfunction add_tag_row() {\r\n    var counter = 1;\r\n    jQuery('#add_tag').click(function(event){\r\n    event.preventDefault();\r\n    counter++;\r\n    var newRow = jQuery('<tr><td><input type=\"text\" name=\"first_name' +\r\n        counter + '\"/></td><td><input type=\"text\" name=\"last_name' +\r\n        counter + '\"/></td></tr>');\r\n    jQuery('table.authors-list').append(newRow);\r\n});\r\n}\r\nfunction delete_tag(name) {\r\n    let tag_modal_content = $('.modal-content');\r\n    tag_modal_content.LoadingOverlay('show');\r\n\r\n    let tag_name = $('#tag_name').val();\r\n    let occurences = $('#occurences').val();\r\n    $.ajax({\r\n      type: \"DELETE\",\r\n      url: \"api/tag/del_tag\",\r\n      data: {name: tag_name, occurences: occurences},\r\n      success: function (data) {\r\n        tag_modal_content.LoadingOverlay('hide', true);\r\n            if (data['success'] === false) {\r\n                alert(data['errormsg']);\r\n            } else {\r\n                if (data.rebuild_table) {\r\n                    location.reload();\r\n                } else {\r\n                    tags_datatable.row(associated_row_id).data(data.data).draw();\r\n                    $('#tag_modal').modal('hide');\r\n                }\r\n            }\r\n      }\r\n    });\r\n}\r\n\r\n$(document).ready(function() {\r\n    // Prepare and load the tags table.\r\n    let tags_table = $('#tags_table');\r\n    let tags_datatable = tags_table.DataTable({\r\n        \"paging\": true,\r\n        \"stateSave\": true,\r\n        \"pageLength\": 50,\r\n        \"responsive\": true,\r\n        \"lengthMenu\": [[10, 50, 100, 500, -1], [10, 50, 100, 500, \"All\"]],\r\n        \"dom\": 'rt<\"container\"<\"row\"<\"col-md-6\"li><\"col-md-6\"p>>>',\r\n        \"ajax\": \"api/tag/gets\",\r\n        \"deferRender\": true,\r\n        \"columns\": [\r\n            {\r\n                \"data\": \"name\",\r\n                \"render\": function ( data, type, row, meta ) {\r\n                    result = '<a class=\"modal-opener\" href=\"#\">' + data + '</span></br>';\r\n                    return result;\r\n                }\r\n            },\r\n            {\r\n                \"data\": \"description\",\r\n                \"render\": function ( data, type, row, meta ) {\r\n                    result = '<div class=\"white-space-pre\">' + data + '</div>';\r\n                    return result;\r\n                }\r\n\r\n            },\r\n            {\r\n                \"data\": \"used_by\",\r\n                \"render\": function ( data, type, row, meta ) {\r\n                    let result = '';\r\n                    $(data).each(function (id, name) {\r\n                        if (name.length > 0) {\r\n                            search_query = '?command=search&col=2&q=%5C%22' + name + '%5C%22';\r\n                            result += '<span class=\"badge badge-info\" style=\"background-color: ' + row.color +'\">' +\r\n                                '<a href=\"' + base_url + search_query + '\" target=\"_blank\">' + name + '</a>' +\r\n                                '</span> ';\r\n                        }\r\n                    });\r\n                    if (data.length > 1 && result.length > 0) {\r\n                        const search_all = '?command=search&col=5&q=' + row.name;\r\n                        result += '<span class=\"badge badge-info\" style=\"background-color: #4275d8\">' +\r\n                            '<a href=\"./' + search_all + '\" target=\"_blank\">Show all</a>' +\r\n                            '</span> ';\r\n                    }\r\n                    return result;\r\n                }\r\n            },\r\n            {\r\n                \"data\": \"used_by\",\r\n                \"visible\": false,\r\n                \"searchable\": false,\r\n                \"render\": function ( data, type, row, meta ) {\r\n                    result = '';\r\n                    $(data).each(function (id, name) {\r\n                        if (name.length > 0) {\r\n                            if (result.length > 1) {\r\n                                result += ', '\r\n                            }\r\n                            result += name;\r\n                        }\r\n                    });\r\n                    return result;\r\n                }\r\n            }\r\n        ],\r\n        initComplete : function() {\r\n            $('#search_bar').val(tag_search_string);\r\n            update_search();\r\n\r\n            // Enable Hanfor specific table filtering.\r\n            $.fn.dataTable.ext.search.push(\r\n                function( settings, data, dataIndex ) {\r\n                    // data contains the row. data[0] is the content of the first column in the actual row.\r\n                    // Return true to include the row into the data. false to exclude.\r\n                    return evaluate_search(data);\r\n                }\r\n            );\r\n            this.api().draw();\r\n        }\r\n    });\r\n    tags_datatable.column(3).visible(false);\r\n    new $.fn.dataTable.ColReorder(tags_datatable, {});\r\n\r\n    let search_bar = $( \"#search_bar\" );\r\n    // Bind big custom searchbar to search the table.\r\n    search_bar.keypress(function(e){\r\n        if(e.which === 13) { // Search on enter.\r\n            update_search();\r\n            tags_datatable.draw();\r\n        }\r\n    });\r\n\r\n    new Awesomplete(search_bar[0], {\r\n        filter: function(text, input) {\r\n            let result = false;\r\n            // If we have an uneven number of \":\"\r\n            // We check if we have a match in the input tail starting from the last \":\"\r\n            if ((input.split(\":\").length-1)%2 === 1) {\r\n                result = Awesomplete.FILTER_CONTAINS(text, input.match(/[^:]*$/)[0]);\r\n            }\r\n            return result;\r\n        },\r\n        item: function(text, input) {\r\n            // Match inside \":\" enclosed item.\r\n            return Awesomplete.ITEM(text, input.match(/(:)([\\S]*$)/)[2]);\r\n        },\r\n        replace: function(text) {\r\n            // Cut of the tail starting from the last \":\" and replace by item text.\r\n            const before = this.input.value.match(/(.*)(:(?!.*:).*$)/)[1];\r\n            this.input.value = before + text;\r\n        },\r\n        list: search_autocomplete,\r\n        minChars: 1,\r\n        autoFirst: true\r\n    });\r\n\r\n    // Add listener for tag link to modal.\r\n    tags_table.find('tbody').on('click', 'a.modal-opener', function (event) {\r\n        // prevent body to be scrolled to the top.\r\n        event.preventDefault();\r\n\r\n        // Get row data\r\n        let data = tags_datatable.row($(event.target).parent()).data();\r\n        let row_id = tags_datatable.row($(event.target).parent()).index();\r\n\r\n        // Prepare tag modal\r\n        let tag_modal_content = $('.modal-content');\r\n        $('#tag_modal').modal('show');\r\n        $('#modal_associated_row_index').val(row_id);\r\n\r\n        // Meta information\r\n        $('#tag_name_old').val(data.name);\r\n        $('#occurences').val(data.used_by);\r\n\r\n        // Visible information\r\n        $('#tag_modal_title').html('Tag: ' + data.name);\r\n        $('#tag_name').val(data.name);\r\n        $('#tag_color').val(data.color);\r\n        $('#tag-description').val(data.description);\r\n\r\n        tag_modal_content.LoadingOverlay('hide');\r\n    });\r\n\r\n    // Store changes on tag on save.\r\n    $('#save_tag_modal').click(function () {\r\n        store_tag(tags_datatable);\r\n    });\r\n\r\n    $('.delete_tag').confirmation({\r\n      rootSelector: '.delete_tag'\r\n    }).click(function () {\r\n        delete_tag( $(this).attr('name') );\r\n    });\r\n\r\n    autosize($('#tag-description'));\r\n\r\n    $('#tag_modal').on('shown.bs.modal', function (e) {\r\n        autosize.update($('#tag-description'));\r\n    });\r\n\r\n    $('.clear-all-filters').click(function () {\r\n        $('#search_bar').val('').effect(\"highlight\", {color: 'green'}, 500);\r\n        update_search();\r\n        tags_datatable.draw();\r\n    });\r\n} );\r\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9qcy90YWdzLmpzLmpzIiwibWFwcGluZ3MiOiI7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL2hhbmZvci8uL2pzL3RhZ3MuanM/NDFhMyJdLCJzb3VyY2VzQ29udGVudCI6WyJyZXF1aXJlKCdnYXNwYXJlc2dhbmdhLWpxdWVyeS1sb2FkaW5nLW92ZXJsYXknKTtcclxucmVxdWlyZSgnYm9vdHN0cmFwJyk7XHJcbnJlcXVpcmUoJ2Jvb3RzdHJhcC1jb25maXJtYXRpb24yJyk7XHJcbnJlcXVpcmUoJ2RhdGF0YWJsZXMubmV0LWJzNCcpO1xyXG5yZXF1aXJlKCdqcXVlcnktdWkvdWkvd2lkZ2V0cy9hdXRvY29tcGxldGUnKTtcclxucmVxdWlyZSgnanF1ZXJ5LXVpL3VpL2VmZmVjdHMvZWZmZWN0LWhpZ2hsaWdodCcpO1xyXG5yZXF1aXJlKCcuL2Jvb3RzdHJhcC10b2tlbmZpZWxkLmpzJyk7XHJcbnJlcXVpcmUoJ2F3ZXNvbXBsZXRlJyk7XHJcbnJlcXVpcmUoJ2F3ZXNvbXBsZXRlL2F3ZXNvbXBsZXRlLmNzcycpO1xyXG5yZXF1aXJlKCdkYXRhdGFibGVzLm5ldC1jb2xyZW9yZGVyd2l0aHJlc2l6ZS1ucG0nKTtcclxuXHJcbmNvbnN0IGF1dG9zaXplID0gcmVxdWlyZSgnYXV0b3NpemUnKTtcclxuY29uc3QgeyBTZWFyY2hOb2RlIH0gPSByZXF1aXJlKCcuL2RhdGF0YWJsZXMtYWR2YW5jZWQtc2VhcmNoLmpzJyk7XHJcbmxldCB0YWdfc2VhcmNoX3N0cmluZyA9IHNlc3Npb25TdG9yYWdlLmdldEl0ZW0oJ3RhZ19zZWFyY2hfc3RyaW5nJyk7XHJcbmxldCBzZWFyY2hfYXV0b2NvbXBsZXRlID0gW1xyXG4gICAgXCI6QU5EOlwiLFxyXG4gICAgXCI6T1I6XCIsXHJcbiAgICBcIjpOT1Q6XCIsXHJcbiAgICBcIjpDT0xfSU5ERVhfMDA6XCIsXHJcbiAgICBcIjpDT0xfSU5ERVhfMDE6XCIsXHJcbiAgICBcIjpDT0xfSU5ERVhfMDI6XCIsXHJcbl07XHJcblxyXG4vKipcclxuICogVXBkYXRlIHRoZSBzZWFyY2ggZXhwcmVzc2lvbiB0cmVlLlxyXG4gKi9cclxuZnVuY3Rpb24gdXBkYXRlX3NlYXJjaCgpIHtcclxuICAgIHRhZ19zZWFyY2hfc3RyaW5nID0gJCgnI3NlYXJjaF9iYXInKS52YWwoKS50cmltKCk7XHJcbiAgICBzZXNzaW9uU3RvcmFnZS5zZXRJdGVtKCd0YWdfc2VhcmNoX3N0cmluZycsIHRhZ19zZWFyY2hfc3RyaW5nKTtcclxuICAgIHNlYXJjaF90cmVlID0gU2VhcmNoTm9kZS5mcm9tUXVlcnkodGFnX3NlYXJjaF9zdHJpbmcpO1xyXG59XHJcblxyXG5cclxuZnVuY3Rpb24gZXZhbHVhdGVfc2VhcmNoKGRhdGEpe1xyXG4gICAgcmV0dXJuIHNlYXJjaF90cmVlLmV2YWx1YXRlKGRhdGEsIFt0cnVlLCB0cnVlLCB0cnVlXSk7XHJcbn1cclxuXHJcblxyXG4vKipcclxuICogU3RvcmUgdGhlIGN1cnJlbnRseSBhY3RpdmUgKGluIHRoZSBtb2RhbCkgdGFnLlxyXG4gKiBAcGFyYW0gdGFnc19kYXRhdGFibGVcclxuICovXHJcbmZ1bmN0aW9uIHN0b3JlX3RhZyh0YWdzX2RhdGF0YWJsZSkge1xyXG4gICAgbGV0IHRhZ19tb2RhbF9jb250ZW50ID0gJCgnLm1vZGFsLWNvbnRlbnQnKTtcclxuICAgIHRhZ19tb2RhbF9jb250ZW50LkxvYWRpbmdPdmVybGF5KCdzaG93Jyk7XHJcblxyXG4gICAgLy8gR2V0IGRhdGEuXHJcbiAgICBsZXQgdGFnX25hbWUgPSAkKCcjdGFnX25hbWUnKS52YWwoKTtcclxuICAgIGxldCB0YWdfbmFtZV9vbGQgPSAkKCcjdGFnX25hbWVfb2xkJykudmFsKCk7XHJcbiAgICBsZXQgb2NjdXJlbmNlcyA9ICQoJyNvY2N1cmVuY2VzJykudmFsKCk7XHJcbiAgICBsZXQgdGFnX2NvbG9yID0gJCgnI3RhZ19jb2xvcicpLnZhbCgpO1xyXG4gICAgbGV0IGFzc29jaWF0ZWRfcm93X2lkID0gcGFyc2VJbnQoJCgnI21vZGFsX2Fzc29jaWF0ZWRfcm93X2luZGV4JykudmFsKCkpO1xyXG4gICAgbGV0IHRhZ19kZXNjcmlwdGlvbiA9ICQoJyN0YWctZGVzY3JpcHRpb24nKS52YWwoKTtcclxuXHJcbiAgICAvLyBTdG9yZSB0aGUgdGFnLlxyXG4gICAgJC5wb3N0KCBcImFwaS90YWcvdXBkYXRlXCIsXHJcbiAgICAgICAge1xyXG4gICAgICAgICAgICBuYW1lOiB0YWdfbmFtZSxcclxuICAgICAgICAgICAgbmFtZV9vbGQ6IHRhZ19uYW1lX29sZCxcclxuICAgICAgICAgICAgb2NjdXJlbmNlczogb2NjdXJlbmNlcyxcclxuICAgICAgICAgICAgY29sb3I6IHRhZ19jb2xvcixcclxuICAgICAgICAgICAgZGVzY3JpcHRpb246IHRhZ19kZXNjcmlwdGlvblxyXG4gICAgICAgIH0sXHJcbiAgICAgICAgLy8gVXBkYXRlIHRhZyB0YWJsZSBvbiBzdWNjZXNzIG9yIHNob3cgYW4gZXJyb3IgbWVzc2FnZS5cclxuICAgICAgICBmdW5jdGlvbiggZGF0YSApIHtcclxuICAgICAgICAgICAgdGFnX21vZGFsX2NvbnRlbnQuTG9hZGluZ092ZXJsYXkoJ2hpZGUnLCB0cnVlKTtcclxuICAgICAgICAgICAgaWYgKGRhdGFbJ3N1Y2Nlc3MnXSA9PT0gZmFsc2UpIHtcclxuICAgICAgICAgICAgICAgIGFsZXJ0KGRhdGFbJ2Vycm9ybXNnJ10pO1xyXG4gICAgICAgICAgICB9IGVsc2Uge1xyXG4gICAgICAgICAgICAgICAgaWYgKGRhdGEucmVidWlsZF90YWJsZSkge1xyXG4gICAgICAgICAgICAgICAgICAgIGxvY2F0aW9uLnJlbG9hZCgpO1xyXG4gICAgICAgICAgICAgICAgfSBlbHNlIHtcclxuICAgICAgICAgICAgICAgICAgICB0YWdzX2RhdGF0YWJsZS5yb3coYXNzb2NpYXRlZF9yb3dfaWQpLmRhdGEoZGF0YS5kYXRhKS5kcmF3KCk7XHJcbiAgICAgICAgICAgICAgICAgICAgJCgnI3RhZ19tb2RhbCcpLm1vZGFsKCdoaWRlJyk7XHJcbiAgICAgICAgICAgICAgICB9XHJcbiAgICAgICAgICAgIH1cclxuICAgIH0pO1xyXG59XHJcblxyXG5mdW5jdGlvbiBhZGRfdGFnX3JvdygpIHtcclxuICAgIHZhciBjb3VudGVyID0gMTtcclxuICAgIGpRdWVyeSgnI2FkZF90YWcnKS5jbGljayhmdW5jdGlvbihldmVudCl7XHJcbiAgICBldmVudC5wcmV2ZW50RGVmYXVsdCgpO1xyXG4gICAgY291bnRlcisrO1xyXG4gICAgdmFyIG5ld1JvdyA9IGpRdWVyeSgnPHRyPjx0ZD48aW5wdXQgdHlwZT1cInRleHRcIiBuYW1lPVwiZmlyc3RfbmFtZScgK1xyXG4gICAgICAgIGNvdW50ZXIgKyAnXCIvPjwvdGQ+PHRkPjxpbnB1dCB0eXBlPVwidGV4dFwiIG5hbWU9XCJsYXN0X25hbWUnICtcclxuICAgICAgICBjb3VudGVyICsgJ1wiLz48L3RkPjwvdHI+Jyk7XHJcbiAgICBqUXVlcnkoJ3RhYmxlLmF1dGhvcnMtbGlzdCcpLmFwcGVuZChuZXdSb3cpO1xyXG59KTtcclxufVxyXG5mdW5jdGlvbiBkZWxldGVfdGFnKG5hbWUpIHtcclxuICAgIGxldCB0YWdfbW9kYWxfY29udGVudCA9ICQoJy5tb2RhbC1jb250ZW50Jyk7XHJcbiAgICB0YWdfbW9kYWxfY29udGVudC5Mb2FkaW5nT3ZlcmxheSgnc2hvdycpO1xyXG5cclxuICAgIGxldCB0YWdfbmFtZSA9ICQoJyN0YWdfbmFtZScpLnZhbCgpO1xyXG4gICAgbGV0IG9jY3VyZW5jZXMgPSAkKCcjb2NjdXJlbmNlcycpLnZhbCgpO1xyXG4gICAgJC5hamF4KHtcclxuICAgICAgdHlwZTogXCJERUxFVEVcIixcclxuICAgICAgdXJsOiBcImFwaS90YWcvZGVsX3RhZ1wiLFxyXG4gICAgICBkYXRhOiB7bmFtZTogdGFnX25hbWUsIG9jY3VyZW5jZXM6IG9jY3VyZW5jZXN9LFxyXG4gICAgICBzdWNjZXNzOiBmdW5jdGlvbiAoZGF0YSkge1xyXG4gICAgICAgIHRhZ19tb2RhbF9jb250ZW50LkxvYWRpbmdPdmVybGF5KCdoaWRlJywgdHJ1ZSk7XHJcbiAgICAgICAgICAgIGlmIChkYXRhWydzdWNjZXNzJ10gPT09IGZhbHNlKSB7XHJcbiAgICAgICAgICAgICAgICBhbGVydChkYXRhWydlcnJvcm1zZyddKTtcclxuICAgICAgICAgICAgfSBlbHNlIHtcclxuICAgICAgICAgICAgICAgIGlmIChkYXRhLnJlYnVpbGRfdGFibGUpIHtcclxuICAgICAgICAgICAgICAgICAgICBsb2NhdGlvbi5yZWxvYWQoKTtcclxuICAgICAgICAgICAgICAgIH0gZWxzZSB7XHJcbiAgICAgICAgICAgICAgICAgICAgdGFnc19kYXRhdGFibGUucm93KGFzc29jaWF0ZWRfcm93X2lkKS5kYXRhKGRhdGEuZGF0YSkuZHJhdygpO1xyXG4gICAgICAgICAgICAgICAgICAgICQoJyN0YWdfbW9kYWwnKS5tb2RhbCgnaGlkZScpO1xyXG4gICAgICAgICAgICAgICAgfVxyXG4gICAgICAgICAgICB9XHJcbiAgICAgIH1cclxuICAgIH0pO1xyXG59XHJcblxyXG4kKGRvY3VtZW50KS5yZWFkeShmdW5jdGlvbigpIHtcclxuICAgIC8vIFByZXBhcmUgYW5kIGxvYWQgdGhlIHRhZ3MgdGFibGUuXHJcbiAgICBsZXQgdGFnc190YWJsZSA9ICQoJyN0YWdzX3RhYmxlJyk7XHJcbiAgICBsZXQgdGFnc19kYXRhdGFibGUgPSB0YWdzX3RhYmxlLkRhdGFUYWJsZSh7XHJcbiAgICAgICAgXCJwYWdpbmdcIjogdHJ1ZSxcclxuICAgICAgICBcInN0YXRlU2F2ZVwiOiB0cnVlLFxyXG4gICAgICAgIFwicGFnZUxlbmd0aFwiOiA1MCxcclxuICAgICAgICBcInJlc3BvbnNpdmVcIjogdHJ1ZSxcclxuICAgICAgICBcImxlbmd0aE1lbnVcIjogW1sxMCwgNTAsIDEwMCwgNTAwLCAtMV0sIFsxMCwgNTAsIDEwMCwgNTAwLCBcIkFsbFwiXV0sXHJcbiAgICAgICAgXCJkb21cIjogJ3J0PFwiY29udGFpbmVyXCI8XCJyb3dcIjxcImNvbC1tZC02XCJsaT48XCJjb2wtbWQtNlwicD4+PicsXHJcbiAgICAgICAgXCJhamF4XCI6IFwiYXBpL3RhZy9nZXRzXCIsXHJcbiAgICAgICAgXCJkZWZlclJlbmRlclwiOiB0cnVlLFxyXG4gICAgICAgIFwiY29sdW1uc1wiOiBbXHJcbiAgICAgICAgICAgIHtcclxuICAgICAgICAgICAgICAgIFwiZGF0YVwiOiBcIm5hbWVcIixcclxuICAgICAgICAgICAgICAgIFwicmVuZGVyXCI6IGZ1bmN0aW9uICggZGF0YSwgdHlwZSwgcm93LCBtZXRhICkge1xyXG4gICAgICAgICAgICAgICAgICAgIHJlc3VsdCA9ICc8YSBjbGFzcz1cIm1vZGFsLW9wZW5lclwiIGhyZWY9XCIjXCI+JyArIGRhdGEgKyAnPC9zcGFuPjwvYnI+JztcclxuICAgICAgICAgICAgICAgICAgICByZXR1cm4gcmVzdWx0O1xyXG4gICAgICAgICAgICAgICAgfVxyXG4gICAgICAgICAgICB9LFxyXG4gICAgICAgICAgICB7XHJcbiAgICAgICAgICAgICAgICBcImRhdGFcIjogXCJkZXNjcmlwdGlvblwiLFxyXG4gICAgICAgICAgICAgICAgXCJyZW5kZXJcIjogZnVuY3Rpb24gKCBkYXRhLCB0eXBlLCByb3csIG1ldGEgKSB7XHJcbiAgICAgICAgICAgICAgICAgICAgcmVzdWx0ID0gJzxkaXYgY2xhc3M9XCJ3aGl0ZS1zcGFjZS1wcmVcIj4nICsgZGF0YSArICc8L2Rpdj4nO1xyXG4gICAgICAgICAgICAgICAgICAgIHJldHVybiByZXN1bHQ7XHJcbiAgICAgICAgICAgICAgICB9XHJcblxyXG4gICAgICAgICAgICB9LFxyXG4gICAgICAgICAgICB7XHJcbiAgICAgICAgICAgICAgICBcImRhdGFcIjogXCJ1c2VkX2J5XCIsXHJcbiAgICAgICAgICAgICAgICBcInJlbmRlclwiOiBmdW5jdGlvbiAoIGRhdGEsIHR5cGUsIHJvdywgbWV0YSApIHtcclxuICAgICAgICAgICAgICAgICAgICBsZXQgcmVzdWx0ID0gJyc7XHJcbiAgICAgICAgICAgICAgICAgICAgJChkYXRhKS5lYWNoKGZ1bmN0aW9uIChpZCwgbmFtZSkge1xyXG4gICAgICAgICAgICAgICAgICAgICAgICBpZiAobmFtZS5sZW5ndGggPiAwKSB7XHJcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICBzZWFyY2hfcXVlcnkgPSAnP2NvbW1hbmQ9c2VhcmNoJmNvbD0yJnE9JTVDJTIyJyArIG5hbWUgKyAnJTVDJTIyJztcclxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIHJlc3VsdCArPSAnPHNwYW4gY2xhc3M9XCJiYWRnZSBiYWRnZS1pbmZvXCIgc3R5bGU9XCJiYWNrZ3JvdW5kLWNvbG9yOiAnICsgcm93LmNvbG9yICsnXCI+JyArXHJcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgJzxhIGhyZWY9XCInICsgYmFzZV91cmwgKyBzZWFyY2hfcXVlcnkgKyAnXCIgdGFyZ2V0PVwiX2JsYW5rXCI+JyArIG5hbWUgKyAnPC9hPicgK1xyXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICc8L3NwYW4+ICc7XHJcbiAgICAgICAgICAgICAgICAgICAgICAgIH1cclxuICAgICAgICAgICAgICAgICAgICB9KTtcclxuICAgICAgICAgICAgICAgICAgICBpZiAoZGF0YS5sZW5ndGggPiAxICYmIHJlc3VsdC5sZW5ndGggPiAwKSB7XHJcbiAgICAgICAgICAgICAgICAgICAgICAgIGNvbnN0IHNlYXJjaF9hbGwgPSAnP2NvbW1hbmQ9c2VhcmNoJmNvbD01JnE9JyArIHJvdy5uYW1lO1xyXG4gICAgICAgICAgICAgICAgICAgICAgICByZXN1bHQgKz0gJzxzcGFuIGNsYXNzPVwiYmFkZ2UgYmFkZ2UtaW5mb1wiIHN0eWxlPVwiYmFja2dyb3VuZC1jb2xvcjogIzQyNzVkOFwiPicgK1xyXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgJzxhIGhyZWY9XCIuLycgKyBzZWFyY2hfYWxsICsgJ1wiIHRhcmdldD1cIl9ibGFua1wiPlNob3cgYWxsPC9hPicgK1xyXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgJzwvc3Bhbj4gJztcclxuICAgICAgICAgICAgICAgICAgICB9XHJcbiAgICAgICAgICAgICAgICAgICAgcmV0dXJuIHJlc3VsdDtcclxuICAgICAgICAgICAgICAgIH1cclxuICAgICAgICAgICAgfSxcclxuICAgICAgICAgICAge1xyXG4gICAgICAgICAgICAgICAgXCJkYXRhXCI6IFwidXNlZF9ieVwiLFxyXG4gICAgICAgICAgICAgICAgXCJ2aXNpYmxlXCI6IGZhbHNlLFxyXG4gICAgICAgICAgICAgICAgXCJzZWFyY2hhYmxlXCI6IGZhbHNlLFxyXG4gICAgICAgICAgICAgICAgXCJyZW5kZXJcIjogZnVuY3Rpb24gKCBkYXRhLCB0eXBlLCByb3csIG1ldGEgKSB7XHJcbiAgICAgICAgICAgICAgICAgICAgcmVzdWx0ID0gJyc7XHJcbiAgICAgICAgICAgICAgICAgICAgJChkYXRhKS5lYWNoKGZ1bmN0aW9uIChpZCwgbmFtZSkge1xyXG4gICAgICAgICAgICAgICAgICAgICAgICBpZiAobmFtZS5sZW5ndGggPiAwKSB7XHJcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICBpZiAocmVzdWx0Lmxlbmd0aCA+IDEpIHtcclxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICByZXN1bHQgKz0gJywgJ1xyXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgfVxyXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgcmVzdWx0ICs9IG5hbWU7XHJcbiAgICAgICAgICAgICAgICAgICAgICAgIH1cclxuICAgICAgICAgICAgICAgICAgICB9KTtcclxuICAgICAgICAgICAgICAgICAgICByZXR1cm4gcmVzdWx0O1xyXG4gICAgICAgICAgICAgICAgfVxyXG4gICAgICAgICAgICB9XHJcbiAgICAgICAgXSxcclxuICAgICAgICBpbml0Q29tcGxldGUgOiBmdW5jdGlvbigpIHtcclxuICAgICAgICAgICAgJCgnI3NlYXJjaF9iYXInKS52YWwodGFnX3NlYXJjaF9zdHJpbmcpO1xyXG4gICAgICAgICAgICB1cGRhdGVfc2VhcmNoKCk7XHJcblxyXG4gICAgICAgICAgICAvLyBFbmFibGUgSGFuZm9yIHNwZWNpZmljIHRhYmxlIGZpbHRlcmluZy5cclxuICAgICAgICAgICAgJC5mbi5kYXRhVGFibGUuZXh0LnNlYXJjaC5wdXNoKFxyXG4gICAgICAgICAgICAgICAgZnVuY3Rpb24oIHNldHRpbmdzLCBkYXRhLCBkYXRhSW5kZXggKSB7XHJcbiAgICAgICAgICAgICAgICAgICAgLy8gZGF0YSBjb250YWlucyB0aGUgcm93LiBkYXRhWzBdIGlzIHRoZSBjb250ZW50IG9mIHRoZSBmaXJzdCBjb2x1bW4gaW4gdGhlIGFjdHVhbCByb3cuXHJcbiAgICAgICAgICAgICAgICAgICAgLy8gUmV0dXJuIHRydWUgdG8gaW5jbHVkZSB0aGUgcm93IGludG8gdGhlIGRhdGEuIGZhbHNlIHRvIGV4Y2x1ZGUuXHJcbiAgICAgICAgICAgICAgICAgICAgcmV0dXJuIGV2YWx1YXRlX3NlYXJjaChkYXRhKTtcclxuICAgICAgICAgICAgICAgIH1cclxuICAgICAgICAgICAgKTtcclxuICAgICAgICAgICAgdGhpcy5hcGkoKS5kcmF3KCk7XHJcbiAgICAgICAgfVxyXG4gICAgfSk7XHJcbiAgICB0YWdzX2RhdGF0YWJsZS5jb2x1bW4oMykudmlzaWJsZShmYWxzZSk7XHJcbiAgICBuZXcgJC5mbi5kYXRhVGFibGUuQ29sUmVvcmRlcih0YWdzX2RhdGF0YWJsZSwge30pO1xyXG5cclxuICAgIGxldCBzZWFyY2hfYmFyID0gJCggXCIjc2VhcmNoX2JhclwiICk7XHJcbiAgICAvLyBCaW5kIGJpZyBjdXN0b20gc2VhcmNoYmFyIHRvIHNlYXJjaCB0aGUgdGFibGUuXHJcbiAgICBzZWFyY2hfYmFyLmtleXByZXNzKGZ1bmN0aW9uKGUpe1xyXG4gICAgICAgIGlmKGUud2hpY2ggPT09IDEzKSB7IC8vIFNlYXJjaCBvbiBlbnRlci5cclxuICAgICAgICAgICAgdXBkYXRlX3NlYXJjaCgpO1xyXG4gICAgICAgICAgICB0YWdzX2RhdGF0YWJsZS5kcmF3KCk7XHJcbiAgICAgICAgfVxyXG4gICAgfSk7XHJcblxyXG4gICAgbmV3IEF3ZXNvbXBsZXRlKHNlYXJjaF9iYXJbMF0sIHtcclxuICAgICAgICBmaWx0ZXI6IGZ1bmN0aW9uKHRleHQsIGlucHV0KSB7XHJcbiAgICAgICAgICAgIGxldCByZXN1bHQgPSBmYWxzZTtcclxuICAgICAgICAgICAgLy8gSWYgd2UgaGF2ZSBhbiB1bmV2ZW4gbnVtYmVyIG9mIFwiOlwiXHJcbiAgICAgICAgICAgIC8vIFdlIGNoZWNrIGlmIHdlIGhhdmUgYSBtYXRjaCBpbiB0aGUgaW5wdXQgdGFpbCBzdGFydGluZyBmcm9tIHRoZSBsYXN0IFwiOlwiXHJcbiAgICAgICAgICAgIGlmICgoaW5wdXQuc3BsaXQoXCI6XCIpLmxlbmd0aC0xKSUyID09PSAxKSB7XHJcbiAgICAgICAgICAgICAgICByZXN1bHQgPSBBd2Vzb21wbGV0ZS5GSUxURVJfQ09OVEFJTlModGV4dCwgaW5wdXQubWF0Y2goL1teOl0qJC8pWzBdKTtcclxuICAgICAgICAgICAgfVxyXG4gICAgICAgICAgICByZXR1cm4gcmVzdWx0O1xyXG4gICAgICAgIH0sXHJcbiAgICAgICAgaXRlbTogZnVuY3Rpb24odGV4dCwgaW5wdXQpIHtcclxuICAgICAgICAgICAgLy8gTWF0Y2ggaW5zaWRlIFwiOlwiIGVuY2xvc2VkIGl0ZW0uXHJcbiAgICAgICAgICAgIHJldHVybiBBd2Vzb21wbGV0ZS5JVEVNKHRleHQsIGlucHV0Lm1hdGNoKC8oOikoW1xcU10qJCkvKVsyXSk7XHJcbiAgICAgICAgfSxcclxuICAgICAgICByZXBsYWNlOiBmdW5jdGlvbih0ZXh0KSB7XHJcbiAgICAgICAgICAgIC8vIEN1dCBvZiB0aGUgdGFpbCBzdGFydGluZyBmcm9tIHRoZSBsYXN0IFwiOlwiIGFuZCByZXBsYWNlIGJ5IGl0ZW0gdGV4dC5cclxuICAgICAgICAgICAgY29uc3QgYmVmb3JlID0gdGhpcy5pbnB1dC52YWx1ZS5tYXRjaCgvKC4qKSg6KD8hLio6KS4qJCkvKVsxXTtcclxuICAgICAgICAgICAgdGhpcy5pbnB1dC52YWx1ZSA9IGJlZm9yZSArIHRleHQ7XHJcbiAgICAgICAgfSxcclxuICAgICAgICBsaXN0OiBzZWFyY2hfYXV0b2NvbXBsZXRlLFxyXG4gICAgICAgIG1pbkNoYXJzOiAxLFxyXG4gICAgICAgIGF1dG9GaXJzdDogdHJ1ZVxyXG4gICAgfSk7XHJcblxyXG4gICAgLy8gQWRkIGxpc3RlbmVyIGZvciB0YWcgbGluayB0byBtb2RhbC5cclxuICAgIHRhZ3NfdGFibGUuZmluZCgndGJvZHknKS5vbignY2xpY2snLCAnYS5tb2RhbC1vcGVuZXInLCBmdW5jdGlvbiAoZXZlbnQpIHtcclxuICAgICAgICAvLyBwcmV2ZW50IGJvZHkgdG8gYmUgc2Nyb2xsZWQgdG8gdGhlIHRvcC5cclxuICAgICAgICBldmVudC5wcmV2ZW50RGVmYXVsdCgpO1xyXG5cclxuICAgICAgICAvLyBHZXQgcm93IGRhdGFcclxuICAgICAgICBsZXQgZGF0YSA9IHRhZ3NfZGF0YXRhYmxlLnJvdygkKGV2ZW50LnRhcmdldCkucGFyZW50KCkpLmRhdGEoKTtcclxuICAgICAgICBsZXQgcm93X2lkID0gdGFnc19kYXRhdGFibGUucm93KCQoZXZlbnQudGFyZ2V0KS5wYXJlbnQoKSkuaW5kZXgoKTtcclxuXHJcbiAgICAgICAgLy8gUHJlcGFyZSB0YWcgbW9kYWxcclxuICAgICAgICBsZXQgdGFnX21vZGFsX2NvbnRlbnQgPSAkKCcubW9kYWwtY29udGVudCcpO1xyXG4gICAgICAgICQoJyN0YWdfbW9kYWwnKS5tb2RhbCgnc2hvdycpO1xyXG4gICAgICAgICQoJyNtb2RhbF9hc3NvY2lhdGVkX3Jvd19pbmRleCcpLnZhbChyb3dfaWQpO1xyXG5cclxuICAgICAgICAvLyBNZXRhIGluZm9ybWF0aW9uXHJcbiAgICAgICAgJCgnI3RhZ19uYW1lX29sZCcpLnZhbChkYXRhLm5hbWUpO1xyXG4gICAgICAgICQoJyNvY2N1cmVuY2VzJykudmFsKGRhdGEudXNlZF9ieSk7XHJcblxyXG4gICAgICAgIC8vIFZpc2libGUgaW5mb3JtYXRpb25cclxuICAgICAgICAkKCcjdGFnX21vZGFsX3RpdGxlJykuaHRtbCgnVGFnOiAnICsgZGF0YS5uYW1lKTtcclxuICAgICAgICAkKCcjdGFnX25hbWUnKS52YWwoZGF0YS5uYW1lKTtcclxuICAgICAgICAkKCcjdGFnX2NvbG9yJykudmFsKGRhdGEuY29sb3IpO1xyXG4gICAgICAgICQoJyN0YWctZGVzY3JpcHRpb24nKS52YWwoZGF0YS5kZXNjcmlwdGlvbik7XHJcblxyXG4gICAgICAgIHRhZ19tb2RhbF9jb250ZW50LkxvYWRpbmdPdmVybGF5KCdoaWRlJyk7XHJcbiAgICB9KTtcclxuXHJcbiAgICAvLyBTdG9yZSBjaGFuZ2VzIG9uIHRhZyBvbiBzYXZlLlxyXG4gICAgJCgnI3NhdmVfdGFnX21vZGFsJykuY2xpY2soZnVuY3Rpb24gKCkge1xyXG4gICAgICAgIHN0b3JlX3RhZyh0YWdzX2RhdGF0YWJsZSk7XHJcbiAgICB9KTtcclxuXHJcbiAgICAkKCcuZGVsZXRlX3RhZycpLmNvbmZpcm1hdGlvbih7XHJcbiAgICAgIHJvb3RTZWxlY3RvcjogJy5kZWxldGVfdGFnJ1xyXG4gICAgfSkuY2xpY2soZnVuY3Rpb24gKCkge1xyXG4gICAgICAgIGRlbGV0ZV90YWcoICQodGhpcykuYXR0cignbmFtZScpICk7XHJcbiAgICB9KTtcclxuXHJcbiAgICBhdXRvc2l6ZSgkKCcjdGFnLWRlc2NyaXB0aW9uJykpO1xyXG5cclxuICAgICQoJyN0YWdfbW9kYWwnKS5vbignc2hvd24uYnMubW9kYWwnLCBmdW5jdGlvbiAoZSkge1xyXG4gICAgICAgIGF1dG9zaXplLnVwZGF0ZSgkKCcjdGFnLWRlc2NyaXB0aW9uJykpO1xyXG4gICAgfSk7XHJcblxyXG4gICAgJCgnLmNsZWFyLWFsbC1maWx0ZXJzJykuY2xpY2soZnVuY3Rpb24gKCkge1xyXG4gICAgICAgICQoJyNzZWFyY2hfYmFyJykudmFsKCcnKS5lZmZlY3QoXCJoaWdobGlnaHRcIiwge2NvbG9yOiAnZ3JlZW4nfSwgNTAwKTtcclxuICAgICAgICB1cGRhdGVfc2VhcmNoKCk7XHJcbiAgICAgICAgdGFnc19kYXRhdGFibGUuZHJhdygpO1xyXG4gICAgfSk7XHJcbn0gKTtcclxuIl0sIm5hbWVzIjpbXSwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./js/tags.js\n");

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