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

eval("/* provided dependency */ var $ = __webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\");\n__webpack_require__(/*! gasparesganga-jquery-loading-overlay */ \"./node_modules/gasparesganga-jquery-loading-overlay/src/loadingoverlay.js\");\r\n__webpack_require__(/*! bootstrap */ \"./node_modules/bootstrap/dist/js/bootstrap.js\");\r\n__webpack_require__(/*! bootstrap-confirmation2 */ \"./node_modules/bootstrap-confirmation2/dist/bootstrap-confirmation.js\");\r\n__webpack_require__(/*! datatables.net-bs4 */ \"./node_modules/datatables.net-bs4/js/dataTables.bootstrap4.js\");\r\n__webpack_require__(/*! jquery-ui/ui/widgets/autocomplete */ \"./node_modules/jquery-ui/ui/widgets/autocomplete.js\");\r\n__webpack_require__(/*! jquery-ui/ui/effects/effect-highlight */ \"./node_modules/jquery-ui/ui/effects/effect-highlight.js\");\r\n__webpack_require__(/*! ./bootstrap-tokenfield.js */ \"./js/bootstrap-tokenfield.js\");\r\n__webpack_require__(/*! awesomplete */ \"./node_modules/awesomplete/awesomplete.js\");\r\n__webpack_require__(/*! awesomplete/awesomplete.css */ \"./node_modules/awesomplete/awesomplete.css\");\r\n__webpack_require__(/*! datatables.net-colreorderwithresize-npm */ \"./node_modules/datatables.net-colreorderwithresize-npm/ColReorderWithResize.js\");\r\n\r\nconst autosize = __webpack_require__(/*! autosize */ \"./node_modules/autosize/dist/autosize.js\");\r\nconst { SearchNode } = __webpack_require__(/*! ./datatables-advanced-search.js */ \"./js/datatables-advanced-search.js\");\r\nlet tag_search_string = sessionStorage.getItem('tag_search_string');\r\nlet search_autocomplete = [\r\n    \":AND:\",\r\n    \":OR:\",\r\n    \":NOT:\",\r\n    \":COL_INDEX_00:\",\r\n    \":COL_INDEX_01:\",\r\n    \":COL_INDEX_02:\",\r\n];\r\n\r\n/**\r\n * Update the search expression tree.\r\n */\r\nfunction update_search() {\r\n    tag_search_string = $('#search_bar').val().trim();\r\n    sessionStorage.setItem('tag_search_string', tag_search_string);\r\n    search_tree = SearchNode.fromQuery(tag_search_string);\r\n}\r\n\r\n\r\nfunction evaluate_search(data){\r\n    return search_tree.evaluate(data, [true, true, true]);\r\n}\r\n\r\n\r\n/**\r\n * Store the currently active (in the modal) tag.\r\n * @param tags_datatable\r\n */\r\nfunction store_tag(tags_datatable) {\r\n    let tag_modal_content = $('.modal-content');\r\n    tag_modal_content.LoadingOverlay('show');\r\n\r\n    // Get data.\r\n    let tag_name = $('#tag_name').val();\r\n    let tag_name_old = $('#tag_name_old').val();\r\n    let occurences = $('#occurences').val();\r\n    let tag_color = $('#tag_color').val();\r\n    let associated_row_id = parseInt($('#modal_associated_row_index').val());\r\n    let tag_description = $('#tag-description').val();\r\n\r\n    // Store the tag.\r\n    $.post( \"api/tag/update\",\r\n        {\r\n            name: tag_name,\r\n            name_old: tag_name_old,\r\n            occurences: occurences,\r\n            color: tag_color,\r\n            description: tag_description\r\n        },\r\n        // Update tag table on success or show an error message.\r\n        function( data ) {\r\n            tag_modal_content.LoadingOverlay('hide', true);\r\n            if (data['success'] === false) {\r\n                alert(data['errormsg']);\r\n            } else {\r\n                if (data.rebuild_table) {\r\n                    location.reload();\r\n                } else {\r\n                    tags_datatable.row(associated_row_id).data(data.data).draw();\r\n                    $('#tag_modal').modal('hide');\r\n                }\r\n            }\r\n    });\r\n}\r\n\r\n\r\nfunction delete_tag(name) {\r\n    let tag_modal_content = $('.modal-content');\r\n    tag_modal_content.LoadingOverlay('show');\r\n\r\n    let tag_name = $('#tag_name').val();\r\n    let occurences = $('#occurences').val();\r\n    $.ajax({\r\n      type: \"DELETE\",\r\n      url: \"api/tag/del_tag\",\r\n      data: {name: tag_name, occurences: occurences},\r\n      success: function (data) {\r\n        tag_modal_content.LoadingOverlay('hide', true);\r\n            if (data['success'] === false) {\r\n                alert(data['errormsg']);\r\n            } else {\r\n                if (data.rebuild_table) {\r\n                    location.reload();\r\n                } else {\r\n                    tags_datatable.row(associated_row_id).data(data.data).draw();\r\n                    $('#tag_modal').modal('hide');\r\n                }\r\n            }\r\n      }\r\n    });\r\n}\r\n\r\n$(document).ready(function() {\r\n    // Prepare and load the tags table.\r\n    let tags_table = $('#tags_table');\r\n    let tags_datatable = tags_table.DataTable({\r\n        \"paging\": true,\r\n        \"stateSave\": true,\r\n        \"pageLength\": 50,\r\n        \"responsive\": true,\r\n        \"lengthMenu\": [[10, 50, 100, 500, -1], [10, 50, 100, 500, \"All\"]],\r\n        \"dom\": 'rt<\"container\"<\"row\"<\"col-md-6\"li><\"col-md-6\"p>>>',\r\n        \"ajax\": \"api/tag/gets\",\r\n        \"deferRender\": true,\r\n        \"columns\": [\r\n            {\r\n                \"data\": \"name\",\r\n                \"render\": function ( data, type, row, meta ) {\r\n                    result = '<a class=\"modal-opener\" href=\"#\">' + data + '</span></br>';\r\n                    return result;\r\n                }\r\n            },\r\n            {\r\n                \"data\": \"description\",\r\n                \"render\": function ( data, type, row, meta ) {\r\n                    result = '<div class=\"white-space-pre\">' + data + '</div>';\r\n                    return result;\r\n                }\r\n\r\n            },\r\n            {\r\n                \"data\": \"used_by\",\r\n                \"render\": function ( data, type, row, meta ) {\r\n                    let result = '';\r\n                    $(data).each(function (id, name) {\r\n                        if (name.length > 0) {\r\n                            search_query = '?command=search&col=2&q=%5C%22' + name + '%5C%22';\r\n                            result += '<span class=\"badge badge-info\" style=\"background-color: ' + row.color +'\">' +\r\n                                '<a href=\"' + base_url + search_query + '\" target=\"_blank\">' + name + '</a>' +\r\n                                '</span> ';\r\n                        }\r\n                    });\r\n                    if (data.length > 1 && result.length > 0) {\r\n                        const search_all = '?command=search&col=5&q=' + row.name;\r\n                        result += '<span class=\"badge badge-info\" style=\"background-color: #4275d8\">' +\r\n                            '<a href=\"./' + search_all + '\" target=\"_blank\">Show all</a>' +\r\n                            '</span> ';\r\n                    }\r\n                    return result;\r\n                }\r\n            },\r\n            {\r\n                \"data\": \"used_by\",\r\n                \"visible\": false,\r\n                \"searchable\": false,\r\n                \"render\": function ( data, type, row, meta ) {\r\n                    result = '';\r\n                    $(data).each(function (id, name) {\r\n                        if (name.length > 0) {\r\n                            if (result.length > 1) {\r\n                                result += ', '\r\n                            }\r\n                            result += name;\r\n                        }\r\n                    });\r\n                    return result;\r\n                }\r\n            }\r\n        ],\r\n        initComplete : function() {\r\n            $('#search_bar').val(tag_search_string);\r\n            update_search();\r\n\r\n            // Enable Hanfor specific table filtering.\r\n            $.fn.dataTable.ext.search.push(\r\n                function( settings, data, dataIndex ) {\r\n                    // data contains the row. data[0] is the content of the first column in the actual row.\r\n                    // Return true to include the row into the data. false to exclude.\r\n                    return evaluate_search(data);\r\n                }\r\n            );\r\n            this.api().draw();\r\n        }\r\n    });\r\n    tags_datatable.column(3).visible(false);\r\n    new $.fn.dataTable.ColReorder(tags_datatable, {});\r\n\r\n    let search_bar = $( \"#search_bar\" );\r\n    // Bind big custom searchbar to search the table.\r\n    search_bar.keypress(function(e){\r\n        if(e.which === 13) { // Search on enter.\r\n            update_search();\r\n            tags_datatable.draw();\r\n        }\r\n    });\r\n\r\n    new Awesomplete(search_bar[0], {\r\n        filter: function(text, input) {\r\n            let result = false;\r\n            // If we have an uneven number of \":\"\r\n            // We check if we have a match in the input tail starting from the last \":\"\r\n            if ((input.split(\":\").length-1)%2 === 1) {\r\n                result = Awesomplete.FILTER_CONTAINS(text, input.match(/[^:]*$/)[0]);\r\n            }\r\n            return result;\r\n        },\r\n        item: function(text, input) {\r\n            // Match inside \":\" enclosed item.\r\n            return Awesomplete.ITEM(text, input.match(/(:)([\\S]*$)/)[2]);\r\n        },\r\n        replace: function(text) {\r\n            // Cut of the tail starting from the last \":\" and replace by item text.\r\n            const before = this.input.value.match(/(.*)(:(?!.*:).*$)/)[1];\r\n            this.input.value = before + text;\r\n        },\r\n        list: search_autocomplete,\r\n        minChars: 1,\r\n        autoFirst: true\r\n    });\r\n\r\n    // Add listener for tag link to modal.\r\n    tags_table.find('tbody').on('click', 'a.modal-opener', function (event) {\r\n        // prevent body to be scrolled to the top.\r\n        event.preventDefault();\r\n\r\n        // Get row data\r\n        let data = tags_datatable.row($(event.target).parent()).data();\r\n        let row_id = tags_datatable.row($(event.target).parent()).index();\r\n\r\n        // Prepare tag modal\r\n        let tag_modal_content = $('.modal-content');\r\n        $('#tag_modal').modal('show');\r\n        $('#modal_associated_row_index').val(row_id);\r\n\r\n        // Meta information\r\n        $('#tag_name_old').val(data.name);\r\n        $('#occurences').val(data.used_by);\r\n\r\n        // Visible information\r\n        $('#tag_modal_title').html('Tag: ' + data.name);\r\n        $('#tag_name').val(data.name);\r\n        $('#tag_color').val(data.color);\r\n        $('#tag-description').val(data.description);\r\n\r\n        tag_modal_content.LoadingOverlay('hide');\r\n    });\r\n\r\n    // Store changes on tag on save.\r\n    $('#save_tag_modal').click(function () {\r\n        store_tag(tags_datatable);\r\n    });\r\n\r\n    $('.delete_tag').confirmation({\r\n      rootSelector: '.delete_tag'\r\n    }).click(function () {\r\n        delete_tag( $(this).attr('name') );\r\n    });\r\n\r\n    autosize($('#tag-description'));\r\n\r\n    $('#tag_modal').on('shown.bs.modal', function (e) {\r\n        autosize.update($('#tag-description'));\r\n    });\r\n\r\n    $('.clear-all-filters').click(function () {\r\n        $('#search_bar').val('').effect(\"highlight\", {color: 'green'}, 500);\r\n        update_search();\r\n        tags_datatable.draw();\r\n    });\r\n} );\r\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9qcy90YWdzLmpzLmpzIiwibWFwcGluZ3MiOiI7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL2hhbmZvci8uL2pzL3RhZ3MuanM/NDFhMyJdLCJzb3VyY2VzQ29udGVudCI6WyJyZXF1aXJlKCdnYXNwYXJlc2dhbmdhLWpxdWVyeS1sb2FkaW5nLW92ZXJsYXknKTtcclxucmVxdWlyZSgnYm9vdHN0cmFwJyk7XHJcbnJlcXVpcmUoJ2Jvb3RzdHJhcC1jb25maXJtYXRpb24yJyk7XHJcbnJlcXVpcmUoJ2RhdGF0YWJsZXMubmV0LWJzNCcpO1xyXG5yZXF1aXJlKCdqcXVlcnktdWkvdWkvd2lkZ2V0cy9hdXRvY29tcGxldGUnKTtcclxucmVxdWlyZSgnanF1ZXJ5LXVpL3VpL2VmZmVjdHMvZWZmZWN0LWhpZ2hsaWdodCcpO1xyXG5yZXF1aXJlKCcuL2Jvb3RzdHJhcC10b2tlbmZpZWxkLmpzJyk7XHJcbnJlcXVpcmUoJ2F3ZXNvbXBsZXRlJyk7XHJcbnJlcXVpcmUoJ2F3ZXNvbXBsZXRlL2F3ZXNvbXBsZXRlLmNzcycpO1xyXG5yZXF1aXJlKCdkYXRhdGFibGVzLm5ldC1jb2xyZW9yZGVyd2l0aHJlc2l6ZS1ucG0nKTtcclxuXHJcbmNvbnN0IGF1dG9zaXplID0gcmVxdWlyZSgnYXV0b3NpemUnKTtcclxuY29uc3QgeyBTZWFyY2hOb2RlIH0gPSByZXF1aXJlKCcuL2RhdGF0YWJsZXMtYWR2YW5jZWQtc2VhcmNoLmpzJyk7XHJcbmxldCB0YWdfc2VhcmNoX3N0cmluZyA9IHNlc3Npb25TdG9yYWdlLmdldEl0ZW0oJ3RhZ19zZWFyY2hfc3RyaW5nJyk7XHJcbmxldCBzZWFyY2hfYXV0b2NvbXBsZXRlID0gW1xyXG4gICAgXCI6QU5EOlwiLFxyXG4gICAgXCI6T1I6XCIsXHJcbiAgICBcIjpOT1Q6XCIsXHJcbiAgICBcIjpDT0xfSU5ERVhfMDA6XCIsXHJcbiAgICBcIjpDT0xfSU5ERVhfMDE6XCIsXHJcbiAgICBcIjpDT0xfSU5ERVhfMDI6XCIsXHJcbl07XHJcblxyXG4vKipcclxuICogVXBkYXRlIHRoZSBzZWFyY2ggZXhwcmVzc2lvbiB0cmVlLlxyXG4gKi9cclxuZnVuY3Rpb24gdXBkYXRlX3NlYXJjaCgpIHtcclxuICAgIHRhZ19zZWFyY2hfc3RyaW5nID0gJCgnI3NlYXJjaF9iYXInKS52YWwoKS50cmltKCk7XHJcbiAgICBzZXNzaW9uU3RvcmFnZS5zZXRJdGVtKCd0YWdfc2VhcmNoX3N0cmluZycsIHRhZ19zZWFyY2hfc3RyaW5nKTtcclxuICAgIHNlYXJjaF90cmVlID0gU2VhcmNoTm9kZS5mcm9tUXVlcnkodGFnX3NlYXJjaF9zdHJpbmcpO1xyXG59XHJcblxyXG5cclxuZnVuY3Rpb24gZXZhbHVhdGVfc2VhcmNoKGRhdGEpe1xyXG4gICAgcmV0dXJuIHNlYXJjaF90cmVlLmV2YWx1YXRlKGRhdGEsIFt0cnVlLCB0cnVlLCB0cnVlXSk7XHJcbn1cclxuXHJcblxyXG4vKipcclxuICogU3RvcmUgdGhlIGN1cnJlbnRseSBhY3RpdmUgKGluIHRoZSBtb2RhbCkgdGFnLlxyXG4gKiBAcGFyYW0gdGFnc19kYXRhdGFibGVcclxuICovXHJcbmZ1bmN0aW9uIHN0b3JlX3RhZyh0YWdzX2RhdGF0YWJsZSkge1xyXG4gICAgbGV0IHRhZ19tb2RhbF9jb250ZW50ID0gJCgnLm1vZGFsLWNvbnRlbnQnKTtcclxuICAgIHRhZ19tb2RhbF9jb250ZW50LkxvYWRpbmdPdmVybGF5KCdzaG93Jyk7XHJcblxyXG4gICAgLy8gR2V0IGRhdGEuXHJcbiAgICBsZXQgdGFnX25hbWUgPSAkKCcjdGFnX25hbWUnKS52YWwoKTtcclxuICAgIGxldCB0YWdfbmFtZV9vbGQgPSAkKCcjdGFnX25hbWVfb2xkJykudmFsKCk7XHJcbiAgICBsZXQgb2NjdXJlbmNlcyA9ICQoJyNvY2N1cmVuY2VzJykudmFsKCk7XHJcbiAgICBsZXQgdGFnX2NvbG9yID0gJCgnI3RhZ19jb2xvcicpLnZhbCgpO1xyXG4gICAgbGV0IGFzc29jaWF0ZWRfcm93X2lkID0gcGFyc2VJbnQoJCgnI21vZGFsX2Fzc29jaWF0ZWRfcm93X2luZGV4JykudmFsKCkpO1xyXG4gICAgbGV0IHRhZ19kZXNjcmlwdGlvbiA9ICQoJyN0YWctZGVzY3JpcHRpb24nKS52YWwoKTtcclxuXHJcbiAgICAvLyBTdG9yZSB0aGUgdGFnLlxyXG4gICAgJC5wb3N0KCBcImFwaS90YWcvdXBkYXRlXCIsXHJcbiAgICAgICAge1xyXG4gICAgICAgICAgICBuYW1lOiB0YWdfbmFtZSxcclxuICAgICAgICAgICAgbmFtZV9vbGQ6IHRhZ19uYW1lX29sZCxcclxuICAgICAgICAgICAgb2NjdXJlbmNlczogb2NjdXJlbmNlcyxcclxuICAgICAgICAgICAgY29sb3I6IHRhZ19jb2xvcixcclxuICAgICAgICAgICAgZGVzY3JpcHRpb246IHRhZ19kZXNjcmlwdGlvblxyXG4gICAgICAgIH0sXHJcbiAgICAgICAgLy8gVXBkYXRlIHRhZyB0YWJsZSBvbiBzdWNjZXNzIG9yIHNob3cgYW4gZXJyb3IgbWVzc2FnZS5cclxuICAgICAgICBmdW5jdGlvbiggZGF0YSApIHtcclxuICAgICAgICAgICAgdGFnX21vZGFsX2NvbnRlbnQuTG9hZGluZ092ZXJsYXkoJ2hpZGUnLCB0cnVlKTtcclxuICAgICAgICAgICAgaWYgKGRhdGFbJ3N1Y2Nlc3MnXSA9PT0gZmFsc2UpIHtcclxuICAgICAgICAgICAgICAgIGFsZXJ0KGRhdGFbJ2Vycm9ybXNnJ10pO1xyXG4gICAgICAgICAgICB9IGVsc2Uge1xyXG4gICAgICAgICAgICAgICAgaWYgKGRhdGEucmVidWlsZF90YWJsZSkge1xyXG4gICAgICAgICAgICAgICAgICAgIGxvY2F0aW9uLnJlbG9hZCgpO1xyXG4gICAgICAgICAgICAgICAgfSBlbHNlIHtcclxuICAgICAgICAgICAgICAgICAgICB0YWdzX2RhdGF0YWJsZS5yb3coYXNzb2NpYXRlZF9yb3dfaWQpLmRhdGEoZGF0YS5kYXRhKS5kcmF3KCk7XHJcbiAgICAgICAgICAgICAgICAgICAgJCgnI3RhZ19tb2RhbCcpLm1vZGFsKCdoaWRlJyk7XHJcbiAgICAgICAgICAgICAgICB9XHJcbiAgICAgICAgICAgIH1cclxuICAgIH0pO1xyXG59XHJcblxyXG5cclxuZnVuY3Rpb24gZGVsZXRlX3RhZyhuYW1lKSB7XHJcbiAgICBsZXQgdGFnX21vZGFsX2NvbnRlbnQgPSAkKCcubW9kYWwtY29udGVudCcpO1xyXG4gICAgdGFnX21vZGFsX2NvbnRlbnQuTG9hZGluZ092ZXJsYXkoJ3Nob3cnKTtcclxuXHJcbiAgICBsZXQgdGFnX25hbWUgPSAkKCcjdGFnX25hbWUnKS52YWwoKTtcclxuICAgIGxldCBvY2N1cmVuY2VzID0gJCgnI29jY3VyZW5jZXMnKS52YWwoKTtcclxuICAgICQuYWpheCh7XHJcbiAgICAgIHR5cGU6IFwiREVMRVRFXCIsXHJcbiAgICAgIHVybDogXCJhcGkvdGFnL2RlbF90YWdcIixcclxuICAgICAgZGF0YToge25hbWU6IHRhZ19uYW1lLCBvY2N1cmVuY2VzOiBvY2N1cmVuY2VzfSxcclxuICAgICAgc3VjY2VzczogZnVuY3Rpb24gKGRhdGEpIHtcclxuICAgICAgICB0YWdfbW9kYWxfY29udGVudC5Mb2FkaW5nT3ZlcmxheSgnaGlkZScsIHRydWUpO1xyXG4gICAgICAgICAgICBpZiAoZGF0YVsnc3VjY2VzcyddID09PSBmYWxzZSkge1xyXG4gICAgICAgICAgICAgICAgYWxlcnQoZGF0YVsnZXJyb3Jtc2cnXSk7XHJcbiAgICAgICAgICAgIH0gZWxzZSB7XHJcbiAgICAgICAgICAgICAgICBpZiAoZGF0YS5yZWJ1aWxkX3RhYmxlKSB7XHJcbiAgICAgICAgICAgICAgICAgICAgbG9jYXRpb24ucmVsb2FkKCk7XHJcbiAgICAgICAgICAgICAgICB9IGVsc2Uge1xyXG4gICAgICAgICAgICAgICAgICAgIHRhZ3NfZGF0YXRhYmxlLnJvdyhhc3NvY2lhdGVkX3Jvd19pZCkuZGF0YShkYXRhLmRhdGEpLmRyYXcoKTtcclxuICAgICAgICAgICAgICAgICAgICAkKCcjdGFnX21vZGFsJykubW9kYWwoJ2hpZGUnKTtcclxuICAgICAgICAgICAgICAgIH1cclxuICAgICAgICAgICAgfVxyXG4gICAgICB9XHJcbiAgICB9KTtcclxufVxyXG5cclxuJChkb2N1bWVudCkucmVhZHkoZnVuY3Rpb24oKSB7XHJcbiAgICAvLyBQcmVwYXJlIGFuZCBsb2FkIHRoZSB0YWdzIHRhYmxlLlxyXG4gICAgbGV0IHRhZ3NfdGFibGUgPSAkKCcjdGFnc190YWJsZScpO1xyXG4gICAgbGV0IHRhZ3NfZGF0YXRhYmxlID0gdGFnc190YWJsZS5EYXRhVGFibGUoe1xyXG4gICAgICAgIFwicGFnaW5nXCI6IHRydWUsXHJcbiAgICAgICAgXCJzdGF0ZVNhdmVcIjogdHJ1ZSxcclxuICAgICAgICBcInBhZ2VMZW5ndGhcIjogNTAsXHJcbiAgICAgICAgXCJyZXNwb25zaXZlXCI6IHRydWUsXHJcbiAgICAgICAgXCJsZW5ndGhNZW51XCI6IFtbMTAsIDUwLCAxMDAsIDUwMCwgLTFdLCBbMTAsIDUwLCAxMDAsIDUwMCwgXCJBbGxcIl1dLFxyXG4gICAgICAgIFwiZG9tXCI6ICdydDxcImNvbnRhaW5lclwiPFwicm93XCI8XCJjb2wtbWQtNlwibGk+PFwiY29sLW1kLTZcInA+Pj4nLFxyXG4gICAgICAgIFwiYWpheFwiOiBcImFwaS90YWcvZ2V0c1wiLFxyXG4gICAgICAgIFwiZGVmZXJSZW5kZXJcIjogdHJ1ZSxcclxuICAgICAgICBcImNvbHVtbnNcIjogW1xyXG4gICAgICAgICAgICB7XHJcbiAgICAgICAgICAgICAgICBcImRhdGFcIjogXCJuYW1lXCIsXHJcbiAgICAgICAgICAgICAgICBcInJlbmRlclwiOiBmdW5jdGlvbiAoIGRhdGEsIHR5cGUsIHJvdywgbWV0YSApIHtcclxuICAgICAgICAgICAgICAgICAgICByZXN1bHQgPSAnPGEgY2xhc3M9XCJtb2RhbC1vcGVuZXJcIiBocmVmPVwiI1wiPicgKyBkYXRhICsgJzwvc3Bhbj48L2JyPic7XHJcbiAgICAgICAgICAgICAgICAgICAgcmV0dXJuIHJlc3VsdDtcclxuICAgICAgICAgICAgICAgIH1cclxuICAgICAgICAgICAgfSxcclxuICAgICAgICAgICAge1xyXG4gICAgICAgICAgICAgICAgXCJkYXRhXCI6IFwiZGVzY3JpcHRpb25cIixcclxuICAgICAgICAgICAgICAgIFwicmVuZGVyXCI6IGZ1bmN0aW9uICggZGF0YSwgdHlwZSwgcm93LCBtZXRhICkge1xyXG4gICAgICAgICAgICAgICAgICAgIHJlc3VsdCA9ICc8ZGl2IGNsYXNzPVwid2hpdGUtc3BhY2UtcHJlXCI+JyArIGRhdGEgKyAnPC9kaXY+JztcclxuICAgICAgICAgICAgICAgICAgICByZXR1cm4gcmVzdWx0O1xyXG4gICAgICAgICAgICAgICAgfVxyXG5cclxuICAgICAgICAgICAgfSxcclxuICAgICAgICAgICAge1xyXG4gICAgICAgICAgICAgICAgXCJkYXRhXCI6IFwidXNlZF9ieVwiLFxyXG4gICAgICAgICAgICAgICAgXCJyZW5kZXJcIjogZnVuY3Rpb24gKCBkYXRhLCB0eXBlLCByb3csIG1ldGEgKSB7XHJcbiAgICAgICAgICAgICAgICAgICAgbGV0IHJlc3VsdCA9ICcnO1xyXG4gICAgICAgICAgICAgICAgICAgICQoZGF0YSkuZWFjaChmdW5jdGlvbiAoaWQsIG5hbWUpIHtcclxuICAgICAgICAgICAgICAgICAgICAgICAgaWYgKG5hbWUubGVuZ3RoID4gMCkge1xyXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgc2VhcmNoX3F1ZXJ5ID0gJz9jb21tYW5kPXNlYXJjaCZjb2w9MiZxPSU1QyUyMicgKyBuYW1lICsgJyU1QyUyMic7XHJcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICByZXN1bHQgKz0gJzxzcGFuIGNsYXNzPVwiYmFkZ2UgYmFkZ2UtaW5mb1wiIHN0eWxlPVwiYmFja2dyb3VuZC1jb2xvcjogJyArIHJvdy5jb2xvciArJ1wiPicgK1xyXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICc8YSBocmVmPVwiJyArIGJhc2VfdXJsICsgc2VhcmNoX3F1ZXJ5ICsgJ1wiIHRhcmdldD1cIl9ibGFua1wiPicgKyBuYW1lICsgJzwvYT4nICtcclxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAnPC9zcGFuPiAnO1xyXG4gICAgICAgICAgICAgICAgICAgICAgICB9XHJcbiAgICAgICAgICAgICAgICAgICAgfSk7XHJcbiAgICAgICAgICAgICAgICAgICAgaWYgKGRhdGEubGVuZ3RoID4gMSAmJiByZXN1bHQubGVuZ3RoID4gMCkge1xyXG4gICAgICAgICAgICAgICAgICAgICAgICBjb25zdCBzZWFyY2hfYWxsID0gJz9jb21tYW5kPXNlYXJjaCZjb2w9NSZxPScgKyByb3cubmFtZTtcclxuICAgICAgICAgICAgICAgICAgICAgICAgcmVzdWx0ICs9ICc8c3BhbiBjbGFzcz1cImJhZGdlIGJhZGdlLWluZm9cIiBzdHlsZT1cImJhY2tncm91bmQtY29sb3I6ICM0Mjc1ZDhcIj4nICtcclxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICc8YSBocmVmPVwiLi8nICsgc2VhcmNoX2FsbCArICdcIiB0YXJnZXQ9XCJfYmxhbmtcIj5TaG93IGFsbDwvYT4nICtcclxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICc8L3NwYW4+ICc7XHJcbiAgICAgICAgICAgICAgICAgICAgfVxyXG4gICAgICAgICAgICAgICAgICAgIHJldHVybiByZXN1bHQ7XHJcbiAgICAgICAgICAgICAgICB9XHJcbiAgICAgICAgICAgIH0sXHJcbiAgICAgICAgICAgIHtcclxuICAgICAgICAgICAgICAgIFwiZGF0YVwiOiBcInVzZWRfYnlcIixcclxuICAgICAgICAgICAgICAgIFwidmlzaWJsZVwiOiBmYWxzZSxcclxuICAgICAgICAgICAgICAgIFwic2VhcmNoYWJsZVwiOiBmYWxzZSxcclxuICAgICAgICAgICAgICAgIFwicmVuZGVyXCI6IGZ1bmN0aW9uICggZGF0YSwgdHlwZSwgcm93LCBtZXRhICkge1xyXG4gICAgICAgICAgICAgICAgICAgIHJlc3VsdCA9ICcnO1xyXG4gICAgICAgICAgICAgICAgICAgICQoZGF0YSkuZWFjaChmdW5jdGlvbiAoaWQsIG5hbWUpIHtcclxuICAgICAgICAgICAgICAgICAgICAgICAgaWYgKG5hbWUubGVuZ3RoID4gMCkge1xyXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgaWYgKHJlc3VsdC5sZW5ndGggPiAxKSB7XHJcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgcmVzdWx0ICs9ICcsICdcclxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIH1cclxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIHJlc3VsdCArPSBuYW1lO1xyXG4gICAgICAgICAgICAgICAgICAgICAgICB9XHJcbiAgICAgICAgICAgICAgICAgICAgfSk7XHJcbiAgICAgICAgICAgICAgICAgICAgcmV0dXJuIHJlc3VsdDtcclxuICAgICAgICAgICAgICAgIH1cclxuICAgICAgICAgICAgfVxyXG4gICAgICAgIF0sXHJcbiAgICAgICAgaW5pdENvbXBsZXRlIDogZnVuY3Rpb24oKSB7XHJcbiAgICAgICAgICAgICQoJyNzZWFyY2hfYmFyJykudmFsKHRhZ19zZWFyY2hfc3RyaW5nKTtcclxuICAgICAgICAgICAgdXBkYXRlX3NlYXJjaCgpO1xyXG5cclxuICAgICAgICAgICAgLy8gRW5hYmxlIEhhbmZvciBzcGVjaWZpYyB0YWJsZSBmaWx0ZXJpbmcuXHJcbiAgICAgICAgICAgICQuZm4uZGF0YVRhYmxlLmV4dC5zZWFyY2gucHVzaChcclxuICAgICAgICAgICAgICAgIGZ1bmN0aW9uKCBzZXR0aW5ncywgZGF0YSwgZGF0YUluZGV4ICkge1xyXG4gICAgICAgICAgICAgICAgICAgIC8vIGRhdGEgY29udGFpbnMgdGhlIHJvdy4gZGF0YVswXSBpcyB0aGUgY29udGVudCBvZiB0aGUgZmlyc3QgY29sdW1uIGluIHRoZSBhY3R1YWwgcm93LlxyXG4gICAgICAgICAgICAgICAgICAgIC8vIFJldHVybiB0cnVlIHRvIGluY2x1ZGUgdGhlIHJvdyBpbnRvIHRoZSBkYXRhLiBmYWxzZSB0byBleGNsdWRlLlxyXG4gICAgICAgICAgICAgICAgICAgIHJldHVybiBldmFsdWF0ZV9zZWFyY2goZGF0YSk7XHJcbiAgICAgICAgICAgICAgICB9XHJcbiAgICAgICAgICAgICk7XHJcbiAgICAgICAgICAgIHRoaXMuYXBpKCkuZHJhdygpO1xyXG4gICAgICAgIH1cclxuICAgIH0pO1xyXG4gICAgdGFnc19kYXRhdGFibGUuY29sdW1uKDMpLnZpc2libGUoZmFsc2UpO1xyXG4gICAgbmV3ICQuZm4uZGF0YVRhYmxlLkNvbFJlb3JkZXIodGFnc19kYXRhdGFibGUsIHt9KTtcclxuXHJcbiAgICBsZXQgc2VhcmNoX2JhciA9ICQoIFwiI3NlYXJjaF9iYXJcIiApO1xyXG4gICAgLy8gQmluZCBiaWcgY3VzdG9tIHNlYXJjaGJhciB0byBzZWFyY2ggdGhlIHRhYmxlLlxyXG4gICAgc2VhcmNoX2Jhci5rZXlwcmVzcyhmdW5jdGlvbihlKXtcclxuICAgICAgICBpZihlLndoaWNoID09PSAxMykgeyAvLyBTZWFyY2ggb24gZW50ZXIuXHJcbiAgICAgICAgICAgIHVwZGF0ZV9zZWFyY2goKTtcclxuICAgICAgICAgICAgdGFnc19kYXRhdGFibGUuZHJhdygpO1xyXG4gICAgICAgIH1cclxuICAgIH0pO1xyXG5cclxuICAgIG5ldyBBd2Vzb21wbGV0ZShzZWFyY2hfYmFyWzBdLCB7XHJcbiAgICAgICAgZmlsdGVyOiBmdW5jdGlvbih0ZXh0LCBpbnB1dCkge1xyXG4gICAgICAgICAgICBsZXQgcmVzdWx0ID0gZmFsc2U7XHJcbiAgICAgICAgICAgIC8vIElmIHdlIGhhdmUgYW4gdW5ldmVuIG51bWJlciBvZiBcIjpcIlxyXG4gICAgICAgICAgICAvLyBXZSBjaGVjayBpZiB3ZSBoYXZlIGEgbWF0Y2ggaW4gdGhlIGlucHV0IHRhaWwgc3RhcnRpbmcgZnJvbSB0aGUgbGFzdCBcIjpcIlxyXG4gICAgICAgICAgICBpZiAoKGlucHV0LnNwbGl0KFwiOlwiKS5sZW5ndGgtMSklMiA9PT0gMSkge1xyXG4gICAgICAgICAgICAgICAgcmVzdWx0ID0gQXdlc29tcGxldGUuRklMVEVSX0NPTlRBSU5TKHRleHQsIGlucHV0Lm1hdGNoKC9bXjpdKiQvKVswXSk7XHJcbiAgICAgICAgICAgIH1cclxuICAgICAgICAgICAgcmV0dXJuIHJlc3VsdDtcclxuICAgICAgICB9LFxyXG4gICAgICAgIGl0ZW06IGZ1bmN0aW9uKHRleHQsIGlucHV0KSB7XHJcbiAgICAgICAgICAgIC8vIE1hdGNoIGluc2lkZSBcIjpcIiBlbmNsb3NlZCBpdGVtLlxyXG4gICAgICAgICAgICByZXR1cm4gQXdlc29tcGxldGUuSVRFTSh0ZXh0LCBpbnB1dC5tYXRjaCgvKDopKFtcXFNdKiQpLylbMl0pO1xyXG4gICAgICAgIH0sXHJcbiAgICAgICAgcmVwbGFjZTogZnVuY3Rpb24odGV4dCkge1xyXG4gICAgICAgICAgICAvLyBDdXQgb2YgdGhlIHRhaWwgc3RhcnRpbmcgZnJvbSB0aGUgbGFzdCBcIjpcIiBhbmQgcmVwbGFjZSBieSBpdGVtIHRleHQuXHJcbiAgICAgICAgICAgIGNvbnN0IGJlZm9yZSA9IHRoaXMuaW5wdXQudmFsdWUubWF0Y2goLyguKikoOig/IS4qOikuKiQpLylbMV07XHJcbiAgICAgICAgICAgIHRoaXMuaW5wdXQudmFsdWUgPSBiZWZvcmUgKyB0ZXh0O1xyXG4gICAgICAgIH0sXHJcbiAgICAgICAgbGlzdDogc2VhcmNoX2F1dG9jb21wbGV0ZSxcclxuICAgICAgICBtaW5DaGFyczogMSxcclxuICAgICAgICBhdXRvRmlyc3Q6IHRydWVcclxuICAgIH0pO1xyXG5cclxuICAgIC8vIEFkZCBsaXN0ZW5lciBmb3IgdGFnIGxpbmsgdG8gbW9kYWwuXHJcbiAgICB0YWdzX3RhYmxlLmZpbmQoJ3Rib2R5Jykub24oJ2NsaWNrJywgJ2EubW9kYWwtb3BlbmVyJywgZnVuY3Rpb24gKGV2ZW50KSB7XHJcbiAgICAgICAgLy8gcHJldmVudCBib2R5IHRvIGJlIHNjcm9sbGVkIHRvIHRoZSB0b3AuXHJcbiAgICAgICAgZXZlbnQucHJldmVudERlZmF1bHQoKTtcclxuXHJcbiAgICAgICAgLy8gR2V0IHJvdyBkYXRhXHJcbiAgICAgICAgbGV0IGRhdGEgPSB0YWdzX2RhdGF0YWJsZS5yb3coJChldmVudC50YXJnZXQpLnBhcmVudCgpKS5kYXRhKCk7XHJcbiAgICAgICAgbGV0IHJvd19pZCA9IHRhZ3NfZGF0YXRhYmxlLnJvdygkKGV2ZW50LnRhcmdldCkucGFyZW50KCkpLmluZGV4KCk7XHJcblxyXG4gICAgICAgIC8vIFByZXBhcmUgdGFnIG1vZGFsXHJcbiAgICAgICAgbGV0IHRhZ19tb2RhbF9jb250ZW50ID0gJCgnLm1vZGFsLWNvbnRlbnQnKTtcclxuICAgICAgICAkKCcjdGFnX21vZGFsJykubW9kYWwoJ3Nob3cnKTtcclxuICAgICAgICAkKCcjbW9kYWxfYXNzb2NpYXRlZF9yb3dfaW5kZXgnKS52YWwocm93X2lkKTtcclxuXHJcbiAgICAgICAgLy8gTWV0YSBpbmZvcm1hdGlvblxyXG4gICAgICAgICQoJyN0YWdfbmFtZV9vbGQnKS52YWwoZGF0YS5uYW1lKTtcclxuICAgICAgICAkKCcjb2NjdXJlbmNlcycpLnZhbChkYXRhLnVzZWRfYnkpO1xyXG5cclxuICAgICAgICAvLyBWaXNpYmxlIGluZm9ybWF0aW9uXHJcbiAgICAgICAgJCgnI3RhZ19tb2RhbF90aXRsZScpLmh0bWwoJ1RhZzogJyArIGRhdGEubmFtZSk7XHJcbiAgICAgICAgJCgnI3RhZ19uYW1lJykudmFsKGRhdGEubmFtZSk7XHJcbiAgICAgICAgJCgnI3RhZ19jb2xvcicpLnZhbChkYXRhLmNvbG9yKTtcclxuICAgICAgICAkKCcjdGFnLWRlc2NyaXB0aW9uJykudmFsKGRhdGEuZGVzY3JpcHRpb24pO1xyXG5cclxuICAgICAgICB0YWdfbW9kYWxfY29udGVudC5Mb2FkaW5nT3ZlcmxheSgnaGlkZScpO1xyXG4gICAgfSk7XHJcblxyXG4gICAgLy8gU3RvcmUgY2hhbmdlcyBvbiB0YWcgb24gc2F2ZS5cclxuICAgICQoJyNzYXZlX3RhZ19tb2RhbCcpLmNsaWNrKGZ1bmN0aW9uICgpIHtcclxuICAgICAgICBzdG9yZV90YWcodGFnc19kYXRhdGFibGUpO1xyXG4gICAgfSk7XHJcblxyXG4gICAgJCgnLmRlbGV0ZV90YWcnKS5jb25maXJtYXRpb24oe1xyXG4gICAgICByb290U2VsZWN0b3I6ICcuZGVsZXRlX3RhZydcclxuICAgIH0pLmNsaWNrKGZ1bmN0aW9uICgpIHtcclxuICAgICAgICBkZWxldGVfdGFnKCAkKHRoaXMpLmF0dHIoJ25hbWUnKSApO1xyXG4gICAgfSk7XHJcblxyXG4gICAgYXV0b3NpemUoJCgnI3RhZy1kZXNjcmlwdGlvbicpKTtcclxuXHJcbiAgICAkKCcjdGFnX21vZGFsJykub24oJ3Nob3duLmJzLm1vZGFsJywgZnVuY3Rpb24gKGUpIHtcclxuICAgICAgICBhdXRvc2l6ZS51cGRhdGUoJCgnI3RhZy1kZXNjcmlwdGlvbicpKTtcclxuICAgIH0pO1xyXG5cclxuICAgICQoJy5jbGVhci1hbGwtZmlsdGVycycpLmNsaWNrKGZ1bmN0aW9uICgpIHtcclxuICAgICAgICAkKCcjc2VhcmNoX2JhcicpLnZhbCgnJykuZWZmZWN0KFwiaGlnaGxpZ2h0XCIsIHtjb2xvcjogJ2dyZWVuJ30sIDUwMCk7XHJcbiAgICAgICAgdXBkYXRlX3NlYXJjaCgpO1xyXG4gICAgICAgIHRhZ3NfZGF0YXRhYmxlLmRyYXcoKTtcclxuICAgIH0pO1xyXG59ICk7XHJcbiJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./js/tags.js\n");

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