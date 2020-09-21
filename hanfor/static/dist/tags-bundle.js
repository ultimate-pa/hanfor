/******/ (function(modules) { // webpackBootstrap
/******/ 	// install a JSONP callback for chunk loading
/******/ 	function webpackJsonpCallback(data) {
/******/ 		var chunkIds = data[0];
/******/ 		var moreModules = data[1];
/******/ 		var executeModules = data[2];
/******/
/******/ 		// add "moreModules" to the modules object,
/******/ 		// then flag all "chunkIds" as loaded and fire callback
/******/ 		var moduleId, chunkId, i = 0, resolves = [];
/******/ 		for(;i < chunkIds.length; i++) {
/******/ 			chunkId = chunkIds[i];
/******/ 			if(installedChunks[chunkId]) {
/******/ 				resolves.push(installedChunks[chunkId][0]);
/******/ 			}
/******/ 			installedChunks[chunkId] = 0;
/******/ 		}
/******/ 		for(moduleId in moreModules) {
/******/ 			if(Object.prototype.hasOwnProperty.call(moreModules, moduleId)) {
/******/ 				modules[moduleId] = moreModules[moduleId];
/******/ 			}
/******/ 		}
/******/ 		if(parentJsonpFunction) parentJsonpFunction(data);
/******/
/******/ 		while(resolves.length) {
/******/ 			resolves.shift()();
/******/ 		}
/******/
/******/ 		// add entry modules from loaded chunk to deferred list
/******/ 		deferredModules.push.apply(deferredModules, executeModules || []);
/******/
/******/ 		// run deferred modules when all chunks ready
/******/ 		return checkDeferredModules();
/******/ 	};
/******/ 	function checkDeferredModules() {
/******/ 		var result;
/******/ 		for(var i = 0; i < deferredModules.length; i++) {
/******/ 			var deferredModule = deferredModules[i];
/******/ 			var fulfilled = true;
/******/ 			for(var j = 1; j < deferredModule.length; j++) {
/******/ 				var depId = deferredModule[j];
/******/ 				if(installedChunks[depId] !== 0) fulfilled = false;
/******/ 			}
/******/ 			if(fulfilled) {
/******/ 				deferredModules.splice(i--, 1);
/******/ 				result = __webpack_require__(__webpack_require__.s = deferredModule[0]);
/******/ 			}
/******/ 		}
/******/ 		return result;
/******/ 	}
/******/
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// object to store loaded and loading chunks
/******/ 	// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 	// Promise = chunk loading, 0 = chunk loaded
/******/ 	var installedChunks = {
/******/ 		"tags": 0
/******/ 	};
/******/
/******/ 	var deferredModules = [];
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "./static/dist/";
/******/
/******/ 	var jsonpArray = window["webpackJsonp"] = window["webpackJsonp"] || [];
/******/ 	var oldJsonpFunction = jsonpArray.push.bind(jsonpArray);
/******/ 	jsonpArray.push = webpackJsonpCallback;
/******/ 	jsonpArray = jsonpArray.slice();
/******/ 	for(var i = 0; i < jsonpArray.length; i++) webpackJsonpCallback(jsonpArray[i]);
/******/ 	var parentJsonpFunction = oldJsonpFunction;
/******/
/******/
/******/ 	// add entry module to deferred list
/******/ 	deferredModules.push(["./js/tags.js","commons"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "./js/tags.js":
/*!********************!*\
  !*** ./js/tags.js ***!
  \********************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("/* WEBPACK VAR INJECTION */(function($) {__webpack_require__(/*! gasparesganga-jquery-loading-overlay */ \"./node_modules/gasparesganga-jquery-loading-overlay/src/loadingoverlay.js\");\n__webpack_require__(/*! bootstrap */ \"./node_modules/bootstrap/dist/js/bootstrap.js\");\n__webpack_require__(/*! bootstrap-confirmation2 */ \"./node_modules/bootstrap-confirmation2/dist/bootstrap-confirmation.js\");\n__webpack_require__(/*! datatables.net-bs4 */ \"./node_modules/datatables.net-bs4/js/dataTables.bootstrap4.js\");\n__webpack_require__(/*! jquery-ui/ui/widgets/autocomplete */ \"./node_modules/jquery-ui/ui/widgets/autocomplete.js\");\n__webpack_require__(/*! jquery-ui/ui/effects/effect-highlight */ \"./node_modules/jquery-ui/ui/effects/effect-highlight.js\");\n__webpack_require__(/*! ./bootstrap-tokenfield.js */ \"./js/bootstrap-tokenfield.js\");\n__webpack_require__(/*! awesomplete */ \"./node_modules/awesomplete/awesomplete.js\");\n__webpack_require__(/*! awesomplete/awesomplete.css */ \"./node_modules/awesomplete/awesomplete.css\");\n__webpack_require__(/*! ./colResizable-1.6.min.js */ \"./js/colResizable-1.6.min.js\");\n\nconst autosize = __webpack_require__(/*! autosize */ \"./node_modules/autosize/dist/autosize.js\");\nconst { SearchNode } = __webpack_require__(/*! ./datatables-advanced-search.js */ \"./js/datatables-advanced-search.js\");\nlet tag_search_string = sessionStorage.getItem('tag_search_string');\nlet search_autocomplete = [\n    \":AND:\",\n    \":OR:\",\n    \":NOT:\",\n    \":COL_INDEX_00:\",\n    \":COL_INDEX_01:\",\n    \":COL_INDEX_02:\",\n];\n\n/**\n * Update the search expression tree.\n */\nfunction update_search() {\n    tag_search_string = $('#search_bar').val().trim();\n    sessionStorage.setItem('tag_search_string', tag_search_string);\n    search_tree = SearchNode.fromQuery(tag_search_string);\n}\n\n\nfunction evaluate_search(data){\n    return search_tree.evaluate(data, [true, true, true]);\n}\n\n\n/**\n * Store the currently active (in the modal) tag.\n * @param tags_datatable\n */\nfunction store_tag(tags_datatable) {\n    let tag_modal_content = $('.modal-content');\n    tag_modal_content.LoadingOverlay('show');\n\n    // Get data.\n    let tag_name = $('#tag_name').val();\n    let tag_name_old = $('#tag_name_old').val();\n    let occurences = $('#occurences').val();\n    let tag_color = $('#tag_color').val();\n    let associated_row_id = parseInt($('#modal_associated_row_index').val());\n    let tag_description = $('#tag-description').val();\n\n    // Store the tag.\n    $.post( \"api/tag/update\",\n        {\n            name: tag_name,\n            name_old: tag_name_old,\n            occurences: occurences,\n            color: tag_color,\n            description: tag_description\n        },\n        // Update tag table on success or show an error message.\n        function( data ) {\n            tag_modal_content.LoadingOverlay('hide', true);\n            if (data['success'] === false) {\n                alert(data['errormsg']);\n            } else {\n                if (data.rebuild_table) {\n                    location.reload();\n                } else {\n                    tags_datatable.row(associated_row_id).data(data.data).draw();\n                    $('#tag_modal').modal('hide');\n                }\n            }\n    });\n}\n\n\nfunction delete_tag(name) {\n    let tag_modal_content = $('.modal-content');\n    tag_modal_content.LoadingOverlay('show');\n\n    let tag_name = $('#tag_name').val();\n    let occurences = $('#occurences').val();\n    $.ajax({\n      type: \"DELETE\",\n      url: \"api/tag/del_tag\",\n      data: {name: tag_name, occurences: occurences},\n      success: function (data) {\n        tag_modal_content.LoadingOverlay('hide', true);\n            if (data['success'] === false) {\n                alert(data['errormsg']);\n            } else {\n                if (data.rebuild_table) {\n                    location.reload();\n                } else {\n                    tags_datatable.row(associated_row_id).data(data.data).draw();\n                    $('#tag_modal').modal('hide');\n                }\n            }\n      }\n    });\n}\n\n$(document).ready(function() {\n    // Prepare and load the tags table.\n    let tags_table = $('#tags_table');\n    let tags_datatable = tags_table.DataTable({\n        \"paging\": true,\n        \"stateSave\": true,\n        \"pageLength\": 50,\n        \"responsive\": true,\n        \"lengthMenu\": [[10, 50, 100, 500, -1], [10, 50, 100, 500, \"All\"]],\n        \"dom\": 'rt<\"container\"<\"row\"<\"col-md-6\"li><\"col-md-6\"p>>>',\n        \"ajax\": \"api/tag/gets\",\n        \"deferRender\": true,\n        \"columns\": [\n            {\n                \"data\": \"name\",\n                \"render\": function ( data, type, row, meta ) {\n                    result = '<a class=\"modal-opener\" href=\"#\">' + data + '</span></br>';\n                    return result;\n                }\n            },\n            {\n                \"data\": \"description\",\n                \"render\": function ( data, type, row, meta ) {\n                    result = '<div class=\"white-space-pre\">' + data + '</div>';\n                    return result;\n                }\n\n            },\n            {\n                \"data\": \"used_by\",\n                \"render\": function ( data, type, row, meta ) {\n                    let result = '';\n                    $(data).each(function (id, name) {\n                        if (name.length > 0) {\n                            search_query = '?command=search&col=2&q=%5C%22' + name + '%5C%22';\n                            result += '<span class=\"badge badge-info\" style=\"background-color: ' + row.color +'\">' +\n                                '<a href=\"' + base_url + search_query + '\" target=\"_blank\">' + name + '</a>' +\n                                '</span> ';\n                        }\n                    });\n                    if (data.length > 1 && result.length > 0) {\n                        const search_all = '?command=search&col=5&q=' + row.name;\n                        result += '<span class=\"badge badge-info\" style=\"background-color: #4275d8\">' +\n                            '<a href=\"./' + search_all + '\" target=\"_blank\">Show all</a>' +\n                            '</span> ';\n                    }\n                    return result;\n                }\n            },\n            {\n                \"data\": \"used_by\",\n                \"visible\": false,\n                \"searchable\": false,\n                \"render\": function ( data, type, row, meta ) {\n                    result = '';\n                    $(data).each(function (id, name) {\n                        if (name.length > 0) {\n                            if (result.length > 1) {\n                                result += ', '\n                            }\n                            result += name;\n                        }\n                    });\n                    return result;\n                }\n            }\n        ],\n        initComplete : function() {\n            $('#search_bar').val(tag_search_string);\n            update_search();\n\n            // Enable Hanfor specific table filtering.\n            $.fn.dataTable.ext.search.push(\n                function( settings, data, dataIndex ) {\n                    // data contains the row. data[0] is the content of the first column in the actual row.\n                    // Return true to include the row into the data. false to exclude.\n                    return evaluate_search(data);\n                }\n            );\n            this.api().draw();\n            $('#tags_table').colResizable({\n                liveDrag:true,\n                postbackSafe: true\n            });\n        }\n    });\n    tags_datatable.column(3).visible(false);\n\n    let search_bar = $( \"#search_bar\" );\n    // Bind big custom searchbar to search the table.\n    search_bar.keypress(function(e){\n        if(e.which === 13) { // Search on enter.\n            update_search();\n            tags_datatable.draw();\n        }\n    });\n\n    new Awesomplete(search_bar[0], {\n        filter: function(text, input) {\n            let result = false;\n            // If we have an uneven number of \":\"\n            // We check if we have a match in the input tail starting from the last \":\"\n            if ((input.split(\":\").length-1)%2 === 1) {\n                result = Awesomplete.FILTER_CONTAINS(text, input.match(/[^:]*$/)[0]);\n            }\n            return result;\n        },\n        item: function(text, input) {\n            // Match inside \":\" enclosed item.\n            return Awesomplete.ITEM(text, input.match(/(:)([\\S]*$)/)[2]);\n        },\n        replace: function(text) {\n            // Cut of the tail starting from the last \":\" and replace by item text.\n            const before = this.input.value.match(/(.*)(:(?!.*:).*$)/)[1];\n            this.input.value = before + text;\n        },\n        list: search_autocomplete,\n        minChars: 1,\n        autoFirst: true\n    });\n\n    // Add listener for tag link to modal.\n    tags_table.find('tbody').on('click', 'a.modal-opener', function (event) {\n        // prevent body to be scrolled to the top.\n        event.preventDefault();\n\n        // Get row data\n        let data = tags_datatable.row($(event.target).parent()).data();\n        let row_id = tags_datatable.row($(event.target).parent()).index();\n\n        // Prepare tag modal\n        let tag_modal_content = $('.modal-content');\n        $('#tag_modal').modal('show');\n        $('#modal_associated_row_index').val(row_id);\n\n        // Meta information\n        $('#tag_name_old').val(data.name);\n        $('#occurences').val(data.used_by);\n\n        // Visible information\n        $('#tag_modal_title').html('Tag: ' + data.name);\n        $('#tag_name').val(data.name);\n        $('#tag_color').val(data.color);\n        $('#tag-description').val(data.description);\n\n        tag_modal_content.LoadingOverlay('hide');\n    });\n\n    // Store changes on tag on save.\n    $('#save_tag_modal').click(function () {\n        store_tag(tags_datatable);\n    });\n\n    $('.delete_tag').confirmation({\n      rootSelector: '.delete_tag'\n    }).click(function () {\n        delete_tag( $(this).attr('name') );\n    });\n\n    autosize($('#tag-description'));\n\n    $('#tag_modal').on('shown.bs.modal', function (e) {\n        autosize.update($('#tag-description'));\n    });\n\n    $('.clear-all-filters').click(function () {\n        $('#search_bar').val('').effect(\"highlight\", {color: 'green'}, 500);\n        update_search();\n        tags_datatable.draw();\n    });\n} );\n\n/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\")))//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9qcy90YWdzLmpzLmpzIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vLy4vanMvdGFncy5qcz80MWEzIl0sInNvdXJjZXNDb250ZW50IjpbInJlcXVpcmUoJ2dhc3BhcmVzZ2FuZ2EtanF1ZXJ5LWxvYWRpbmctb3ZlcmxheScpO1xucmVxdWlyZSgnYm9vdHN0cmFwJyk7XG5yZXF1aXJlKCdib290c3RyYXAtY29uZmlybWF0aW9uMicpO1xucmVxdWlyZSgnZGF0YXRhYmxlcy5uZXQtYnM0Jyk7XG5yZXF1aXJlKCdqcXVlcnktdWkvdWkvd2lkZ2V0cy9hdXRvY29tcGxldGUnKTtcbnJlcXVpcmUoJ2pxdWVyeS11aS91aS9lZmZlY3RzL2VmZmVjdC1oaWdobGlnaHQnKTtcbnJlcXVpcmUoJy4vYm9vdHN0cmFwLXRva2VuZmllbGQuanMnKTtcbnJlcXVpcmUoJ2F3ZXNvbXBsZXRlJyk7XG5yZXF1aXJlKCdhd2Vzb21wbGV0ZS9hd2Vzb21wbGV0ZS5jc3MnKTtcbnJlcXVpcmUoJy4vY29sUmVzaXphYmxlLTEuNi5taW4uanMnKTtcblxuY29uc3QgYXV0b3NpemUgPSByZXF1aXJlKCdhdXRvc2l6ZScpO1xuY29uc3QgeyBTZWFyY2hOb2RlIH0gPSByZXF1aXJlKCcuL2RhdGF0YWJsZXMtYWR2YW5jZWQtc2VhcmNoLmpzJyk7XG5sZXQgdGFnX3NlYXJjaF9zdHJpbmcgPSBzZXNzaW9uU3RvcmFnZS5nZXRJdGVtKCd0YWdfc2VhcmNoX3N0cmluZycpO1xubGV0IHNlYXJjaF9hdXRvY29tcGxldGUgPSBbXG4gICAgXCI6QU5EOlwiLFxuICAgIFwiOk9SOlwiLFxuICAgIFwiOk5PVDpcIixcbiAgICBcIjpDT0xfSU5ERVhfMDA6XCIsXG4gICAgXCI6Q09MX0lOREVYXzAxOlwiLFxuICAgIFwiOkNPTF9JTkRFWF8wMjpcIixcbl07XG5cbi8qKlxuICogVXBkYXRlIHRoZSBzZWFyY2ggZXhwcmVzc2lvbiB0cmVlLlxuICovXG5mdW5jdGlvbiB1cGRhdGVfc2VhcmNoKCkge1xuICAgIHRhZ19zZWFyY2hfc3RyaW5nID0gJCgnI3NlYXJjaF9iYXInKS52YWwoKS50cmltKCk7XG4gICAgc2Vzc2lvblN0b3JhZ2Uuc2V0SXRlbSgndGFnX3NlYXJjaF9zdHJpbmcnLCB0YWdfc2VhcmNoX3N0cmluZyk7XG4gICAgc2VhcmNoX3RyZWUgPSBTZWFyY2hOb2RlLmZyb21RdWVyeSh0YWdfc2VhcmNoX3N0cmluZyk7XG59XG5cblxuZnVuY3Rpb24gZXZhbHVhdGVfc2VhcmNoKGRhdGEpe1xuICAgIHJldHVybiBzZWFyY2hfdHJlZS5ldmFsdWF0ZShkYXRhLCBbdHJ1ZSwgdHJ1ZSwgdHJ1ZV0pO1xufVxuXG5cbi8qKlxuICogU3RvcmUgdGhlIGN1cnJlbnRseSBhY3RpdmUgKGluIHRoZSBtb2RhbCkgdGFnLlxuICogQHBhcmFtIHRhZ3NfZGF0YXRhYmxlXG4gKi9cbmZ1bmN0aW9uIHN0b3JlX3RhZyh0YWdzX2RhdGF0YWJsZSkge1xuICAgIGxldCB0YWdfbW9kYWxfY29udGVudCA9ICQoJy5tb2RhbC1jb250ZW50Jyk7XG4gICAgdGFnX21vZGFsX2NvbnRlbnQuTG9hZGluZ092ZXJsYXkoJ3Nob3cnKTtcblxuICAgIC8vIEdldCBkYXRhLlxuICAgIGxldCB0YWdfbmFtZSA9ICQoJyN0YWdfbmFtZScpLnZhbCgpO1xuICAgIGxldCB0YWdfbmFtZV9vbGQgPSAkKCcjdGFnX25hbWVfb2xkJykudmFsKCk7XG4gICAgbGV0IG9jY3VyZW5jZXMgPSAkKCcjb2NjdXJlbmNlcycpLnZhbCgpO1xuICAgIGxldCB0YWdfY29sb3IgPSAkKCcjdGFnX2NvbG9yJykudmFsKCk7XG4gICAgbGV0IGFzc29jaWF0ZWRfcm93X2lkID0gcGFyc2VJbnQoJCgnI21vZGFsX2Fzc29jaWF0ZWRfcm93X2luZGV4JykudmFsKCkpO1xuICAgIGxldCB0YWdfZGVzY3JpcHRpb24gPSAkKCcjdGFnLWRlc2NyaXB0aW9uJykudmFsKCk7XG5cbiAgICAvLyBTdG9yZSB0aGUgdGFnLlxuICAgICQucG9zdCggXCJhcGkvdGFnL3VwZGF0ZVwiLFxuICAgICAgICB7XG4gICAgICAgICAgICBuYW1lOiB0YWdfbmFtZSxcbiAgICAgICAgICAgIG5hbWVfb2xkOiB0YWdfbmFtZV9vbGQsXG4gICAgICAgICAgICBvY2N1cmVuY2VzOiBvY2N1cmVuY2VzLFxuICAgICAgICAgICAgY29sb3I6IHRhZ19jb2xvcixcbiAgICAgICAgICAgIGRlc2NyaXB0aW9uOiB0YWdfZGVzY3JpcHRpb25cbiAgICAgICAgfSxcbiAgICAgICAgLy8gVXBkYXRlIHRhZyB0YWJsZSBvbiBzdWNjZXNzIG9yIHNob3cgYW4gZXJyb3IgbWVzc2FnZS5cbiAgICAgICAgZnVuY3Rpb24oIGRhdGEgKSB7XG4gICAgICAgICAgICB0YWdfbW9kYWxfY29udGVudC5Mb2FkaW5nT3ZlcmxheSgnaGlkZScsIHRydWUpO1xuICAgICAgICAgICAgaWYgKGRhdGFbJ3N1Y2Nlc3MnXSA9PT0gZmFsc2UpIHtcbiAgICAgICAgICAgICAgICBhbGVydChkYXRhWydlcnJvcm1zZyddKTtcbiAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgaWYgKGRhdGEucmVidWlsZF90YWJsZSkge1xuICAgICAgICAgICAgICAgICAgICBsb2NhdGlvbi5yZWxvYWQoKTtcbiAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICB0YWdzX2RhdGF0YWJsZS5yb3coYXNzb2NpYXRlZF9yb3dfaWQpLmRhdGEoZGF0YS5kYXRhKS5kcmF3KCk7XG4gICAgICAgICAgICAgICAgICAgICQoJyN0YWdfbW9kYWwnKS5tb2RhbCgnaGlkZScpO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH1cbiAgICB9KTtcbn1cblxuXG5mdW5jdGlvbiBkZWxldGVfdGFnKG5hbWUpIHtcbiAgICBsZXQgdGFnX21vZGFsX2NvbnRlbnQgPSAkKCcubW9kYWwtY29udGVudCcpO1xuICAgIHRhZ19tb2RhbF9jb250ZW50LkxvYWRpbmdPdmVybGF5KCdzaG93Jyk7XG5cbiAgICBsZXQgdGFnX25hbWUgPSAkKCcjdGFnX25hbWUnKS52YWwoKTtcbiAgICBsZXQgb2NjdXJlbmNlcyA9ICQoJyNvY2N1cmVuY2VzJykudmFsKCk7XG4gICAgJC5hamF4KHtcbiAgICAgIHR5cGU6IFwiREVMRVRFXCIsXG4gICAgICB1cmw6IFwiYXBpL3RhZy9kZWxfdGFnXCIsXG4gICAgICBkYXRhOiB7bmFtZTogdGFnX25hbWUsIG9jY3VyZW5jZXM6IG9jY3VyZW5jZXN9LFxuICAgICAgc3VjY2VzczogZnVuY3Rpb24gKGRhdGEpIHtcbiAgICAgICAgdGFnX21vZGFsX2NvbnRlbnQuTG9hZGluZ092ZXJsYXkoJ2hpZGUnLCB0cnVlKTtcbiAgICAgICAgICAgIGlmIChkYXRhWydzdWNjZXNzJ10gPT09IGZhbHNlKSB7XG4gICAgICAgICAgICAgICAgYWxlcnQoZGF0YVsnZXJyb3Jtc2cnXSk7XG4gICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgIGlmIChkYXRhLnJlYnVpbGRfdGFibGUpIHtcbiAgICAgICAgICAgICAgICAgICAgbG9jYXRpb24ucmVsb2FkKCk7XG4gICAgICAgICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgICAgICAgICAgdGFnc19kYXRhdGFibGUucm93KGFzc29jaWF0ZWRfcm93X2lkKS5kYXRhKGRhdGEuZGF0YSkuZHJhdygpO1xuICAgICAgICAgICAgICAgICAgICAkKCcjdGFnX21vZGFsJykubW9kYWwoJ2hpZGUnKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICB9XG4gICAgfSk7XG59XG5cbiQoZG9jdW1lbnQpLnJlYWR5KGZ1bmN0aW9uKCkge1xuICAgIC8vIFByZXBhcmUgYW5kIGxvYWQgdGhlIHRhZ3MgdGFibGUuXG4gICAgbGV0IHRhZ3NfdGFibGUgPSAkKCcjdGFnc190YWJsZScpO1xuICAgIGxldCB0YWdzX2RhdGF0YWJsZSA9IHRhZ3NfdGFibGUuRGF0YVRhYmxlKHtcbiAgICAgICAgXCJwYWdpbmdcIjogdHJ1ZSxcbiAgICAgICAgXCJzdGF0ZVNhdmVcIjogdHJ1ZSxcbiAgICAgICAgXCJwYWdlTGVuZ3RoXCI6IDUwLFxuICAgICAgICBcInJlc3BvbnNpdmVcIjogdHJ1ZSxcbiAgICAgICAgXCJsZW5ndGhNZW51XCI6IFtbMTAsIDUwLCAxMDAsIDUwMCwgLTFdLCBbMTAsIDUwLCAxMDAsIDUwMCwgXCJBbGxcIl1dLFxuICAgICAgICBcImRvbVwiOiAncnQ8XCJjb250YWluZXJcIjxcInJvd1wiPFwiY29sLW1kLTZcImxpPjxcImNvbC1tZC02XCJwPj4+JyxcbiAgICAgICAgXCJhamF4XCI6IFwiYXBpL3RhZy9nZXRzXCIsXG4gICAgICAgIFwiZGVmZXJSZW5kZXJcIjogdHJ1ZSxcbiAgICAgICAgXCJjb2x1bW5zXCI6IFtcbiAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgICBcImRhdGFcIjogXCJuYW1lXCIsXG4gICAgICAgICAgICAgICAgXCJyZW5kZXJcIjogZnVuY3Rpb24gKCBkYXRhLCB0eXBlLCByb3csIG1ldGEgKSB7XG4gICAgICAgICAgICAgICAgICAgIHJlc3VsdCA9ICc8YSBjbGFzcz1cIm1vZGFsLW9wZW5lclwiIGhyZWY9XCIjXCI+JyArIGRhdGEgKyAnPC9zcGFuPjwvYnI+JztcbiAgICAgICAgICAgICAgICAgICAgcmV0dXJuIHJlc3VsdDtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9LFxuICAgICAgICAgICAge1xuICAgICAgICAgICAgICAgIFwiZGF0YVwiOiBcImRlc2NyaXB0aW9uXCIsXG4gICAgICAgICAgICAgICAgXCJyZW5kZXJcIjogZnVuY3Rpb24gKCBkYXRhLCB0eXBlLCByb3csIG1ldGEgKSB7XG4gICAgICAgICAgICAgICAgICAgIHJlc3VsdCA9ICc8ZGl2IGNsYXNzPVwid2hpdGUtc3BhY2UtcHJlXCI+JyArIGRhdGEgKyAnPC9kaXY+JztcbiAgICAgICAgICAgICAgICAgICAgcmV0dXJuIHJlc3VsdDtcbiAgICAgICAgICAgICAgICB9XG5cbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgICB7XG4gICAgICAgICAgICAgICAgXCJkYXRhXCI6IFwidXNlZF9ieVwiLFxuICAgICAgICAgICAgICAgIFwicmVuZGVyXCI6IGZ1bmN0aW9uICggZGF0YSwgdHlwZSwgcm93LCBtZXRhICkge1xuICAgICAgICAgICAgICAgICAgICBsZXQgcmVzdWx0ID0gJyc7XG4gICAgICAgICAgICAgICAgICAgICQoZGF0YSkuZWFjaChmdW5jdGlvbiAoaWQsIG5hbWUpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIGlmIChuYW1lLmxlbmd0aCA+IDApIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICBzZWFyY2hfcXVlcnkgPSAnP2NvbW1hbmQ9c2VhcmNoJmNvbD0yJnE9JTVDJTIyJyArIG5hbWUgKyAnJTVDJTIyJztcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICByZXN1bHQgKz0gJzxzcGFuIGNsYXNzPVwiYmFkZ2UgYmFkZ2UtaW5mb1wiIHN0eWxlPVwiYmFja2dyb3VuZC1jb2xvcjogJyArIHJvdy5jb2xvciArJ1wiPicgK1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAnPGEgaHJlZj1cIicgKyBiYXNlX3VybCArIHNlYXJjaF9xdWVyeSArICdcIiB0YXJnZXQ9XCJfYmxhbmtcIj4nICsgbmFtZSArICc8L2E+JyArXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICc8L3NwYW4+ICc7XG4gICAgICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgICAgICAgICBpZiAoZGF0YS5sZW5ndGggPiAxICYmIHJlc3VsdC5sZW5ndGggPiAwKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICBjb25zdCBzZWFyY2hfYWxsID0gJz9jb21tYW5kPXNlYXJjaCZjb2w9NSZxPScgKyByb3cubmFtZTtcbiAgICAgICAgICAgICAgICAgICAgICAgIHJlc3VsdCArPSAnPHNwYW4gY2xhc3M9XCJiYWRnZSBiYWRnZS1pbmZvXCIgc3R5bGU9XCJiYWNrZ3JvdW5kLWNvbG9yOiAjNDI3NWQ4XCI+JyArXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgJzxhIGhyZWY9XCIuLycgKyBzZWFyY2hfYWxsICsgJ1wiIHRhcmdldD1cIl9ibGFua1wiPlNob3cgYWxsPC9hPicgK1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICc8L3NwYW4+ICc7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICAgICAgcmV0dXJuIHJlc3VsdDtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9LFxuICAgICAgICAgICAge1xuICAgICAgICAgICAgICAgIFwiZGF0YVwiOiBcInVzZWRfYnlcIixcbiAgICAgICAgICAgICAgICBcInZpc2libGVcIjogZmFsc2UsXG4gICAgICAgICAgICAgICAgXCJzZWFyY2hhYmxlXCI6IGZhbHNlLFxuICAgICAgICAgICAgICAgIFwicmVuZGVyXCI6IGZ1bmN0aW9uICggZGF0YSwgdHlwZSwgcm93LCBtZXRhICkge1xuICAgICAgICAgICAgICAgICAgICByZXN1bHQgPSAnJztcbiAgICAgICAgICAgICAgICAgICAgJChkYXRhKS5lYWNoKGZ1bmN0aW9uIChpZCwgbmFtZSkge1xuICAgICAgICAgICAgICAgICAgICAgICAgaWYgKG5hbWUubGVuZ3RoID4gMCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgIGlmIChyZXN1bHQubGVuZ3RoID4gMSkge1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICByZXN1bHQgKz0gJywgJ1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICByZXN1bHQgKz0gbmFtZTtcbiAgICAgICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICAgICAgICAgIHJldHVybiByZXN1bHQ7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfVxuICAgICAgICBdLFxuICAgICAgICBpbml0Q29tcGxldGUgOiBmdW5jdGlvbigpIHtcbiAgICAgICAgICAgICQoJyNzZWFyY2hfYmFyJykudmFsKHRhZ19zZWFyY2hfc3RyaW5nKTtcbiAgICAgICAgICAgIHVwZGF0ZV9zZWFyY2goKTtcblxuICAgICAgICAgICAgLy8gRW5hYmxlIEhhbmZvciBzcGVjaWZpYyB0YWJsZSBmaWx0ZXJpbmcuXG4gICAgICAgICAgICAkLmZuLmRhdGFUYWJsZS5leHQuc2VhcmNoLnB1c2goXG4gICAgICAgICAgICAgICAgZnVuY3Rpb24oIHNldHRpbmdzLCBkYXRhLCBkYXRhSW5kZXggKSB7XG4gICAgICAgICAgICAgICAgICAgIC8vIGRhdGEgY29udGFpbnMgdGhlIHJvdy4gZGF0YVswXSBpcyB0aGUgY29udGVudCBvZiB0aGUgZmlyc3QgY29sdW1uIGluIHRoZSBhY3R1YWwgcm93LlxuICAgICAgICAgICAgICAgICAgICAvLyBSZXR1cm4gdHJ1ZSB0byBpbmNsdWRlIHRoZSByb3cgaW50byB0aGUgZGF0YS4gZmFsc2UgdG8gZXhjbHVkZS5cbiAgICAgICAgICAgICAgICAgICAgcmV0dXJuIGV2YWx1YXRlX3NlYXJjaChkYXRhKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICApO1xuICAgICAgICAgICAgdGhpcy5hcGkoKS5kcmF3KCk7XG4gICAgICAgICAgICAkKCcjdGFnc190YWJsZScpLmNvbFJlc2l6YWJsZSh7XG4gICAgICAgICAgICAgICAgbGl2ZURyYWc6dHJ1ZSxcbiAgICAgICAgICAgICAgICBwb3N0YmFja1NhZmU6IHRydWVcbiAgICAgICAgICAgIH0pO1xuICAgICAgICB9XG4gICAgfSk7XG4gICAgdGFnc19kYXRhdGFibGUuY29sdW1uKDMpLnZpc2libGUoZmFsc2UpO1xuXG4gICAgbGV0IHNlYXJjaF9iYXIgPSAkKCBcIiNzZWFyY2hfYmFyXCIgKTtcbiAgICAvLyBCaW5kIGJpZyBjdXN0b20gc2VhcmNoYmFyIHRvIHNlYXJjaCB0aGUgdGFibGUuXG4gICAgc2VhcmNoX2Jhci5rZXlwcmVzcyhmdW5jdGlvbihlKXtcbiAgICAgICAgaWYoZS53aGljaCA9PT0gMTMpIHsgLy8gU2VhcmNoIG9uIGVudGVyLlxuICAgICAgICAgICAgdXBkYXRlX3NlYXJjaCgpO1xuICAgICAgICAgICAgdGFnc19kYXRhdGFibGUuZHJhdygpO1xuICAgICAgICB9XG4gICAgfSk7XG5cbiAgICBuZXcgQXdlc29tcGxldGUoc2VhcmNoX2JhclswXSwge1xuICAgICAgICBmaWx0ZXI6IGZ1bmN0aW9uKHRleHQsIGlucHV0KSB7XG4gICAgICAgICAgICBsZXQgcmVzdWx0ID0gZmFsc2U7XG4gICAgICAgICAgICAvLyBJZiB3ZSBoYXZlIGFuIHVuZXZlbiBudW1iZXIgb2YgXCI6XCJcbiAgICAgICAgICAgIC8vIFdlIGNoZWNrIGlmIHdlIGhhdmUgYSBtYXRjaCBpbiB0aGUgaW5wdXQgdGFpbCBzdGFydGluZyBmcm9tIHRoZSBsYXN0IFwiOlwiXG4gICAgICAgICAgICBpZiAoKGlucHV0LnNwbGl0KFwiOlwiKS5sZW5ndGgtMSklMiA9PT0gMSkge1xuICAgICAgICAgICAgICAgIHJlc3VsdCA9IEF3ZXNvbXBsZXRlLkZJTFRFUl9DT05UQUlOUyh0ZXh0LCBpbnB1dC5tYXRjaCgvW146XSokLylbMF0pO1xuICAgICAgICAgICAgfVxuICAgICAgICAgICAgcmV0dXJuIHJlc3VsdDtcbiAgICAgICAgfSxcbiAgICAgICAgaXRlbTogZnVuY3Rpb24odGV4dCwgaW5wdXQpIHtcbiAgICAgICAgICAgIC8vIE1hdGNoIGluc2lkZSBcIjpcIiBlbmNsb3NlZCBpdGVtLlxuICAgICAgICAgICAgcmV0dXJuIEF3ZXNvbXBsZXRlLklURU0odGV4dCwgaW5wdXQubWF0Y2goLyg6KShbXFxTXSokKS8pWzJdKTtcbiAgICAgICAgfSxcbiAgICAgICAgcmVwbGFjZTogZnVuY3Rpb24odGV4dCkge1xuICAgICAgICAgICAgLy8gQ3V0IG9mIHRoZSB0YWlsIHN0YXJ0aW5nIGZyb20gdGhlIGxhc3QgXCI6XCIgYW5kIHJlcGxhY2UgYnkgaXRlbSB0ZXh0LlxuICAgICAgICAgICAgY29uc3QgYmVmb3JlID0gdGhpcy5pbnB1dC52YWx1ZS5tYXRjaCgvKC4qKSg6KD8hLio6KS4qJCkvKVsxXTtcbiAgICAgICAgICAgIHRoaXMuaW5wdXQudmFsdWUgPSBiZWZvcmUgKyB0ZXh0O1xuICAgICAgICB9LFxuICAgICAgICBsaXN0OiBzZWFyY2hfYXV0b2NvbXBsZXRlLFxuICAgICAgICBtaW5DaGFyczogMSxcbiAgICAgICAgYXV0b0ZpcnN0OiB0cnVlXG4gICAgfSk7XG5cbiAgICAvLyBBZGQgbGlzdGVuZXIgZm9yIHRhZyBsaW5rIHRvIG1vZGFsLlxuICAgIHRhZ3NfdGFibGUuZmluZCgndGJvZHknKS5vbignY2xpY2snLCAnYS5tb2RhbC1vcGVuZXInLCBmdW5jdGlvbiAoZXZlbnQpIHtcbiAgICAgICAgLy8gcHJldmVudCBib2R5IHRvIGJlIHNjcm9sbGVkIHRvIHRoZSB0b3AuXG4gICAgICAgIGV2ZW50LnByZXZlbnREZWZhdWx0KCk7XG5cbiAgICAgICAgLy8gR2V0IHJvdyBkYXRhXG4gICAgICAgIGxldCBkYXRhID0gdGFnc19kYXRhdGFibGUucm93KCQoZXZlbnQudGFyZ2V0KS5wYXJlbnQoKSkuZGF0YSgpO1xuICAgICAgICBsZXQgcm93X2lkID0gdGFnc19kYXRhdGFibGUucm93KCQoZXZlbnQudGFyZ2V0KS5wYXJlbnQoKSkuaW5kZXgoKTtcblxuICAgICAgICAvLyBQcmVwYXJlIHRhZyBtb2RhbFxuICAgICAgICBsZXQgdGFnX21vZGFsX2NvbnRlbnQgPSAkKCcubW9kYWwtY29udGVudCcpO1xuICAgICAgICAkKCcjdGFnX21vZGFsJykubW9kYWwoJ3Nob3cnKTtcbiAgICAgICAgJCgnI21vZGFsX2Fzc29jaWF0ZWRfcm93X2luZGV4JykudmFsKHJvd19pZCk7XG5cbiAgICAgICAgLy8gTWV0YSBpbmZvcm1hdGlvblxuICAgICAgICAkKCcjdGFnX25hbWVfb2xkJykudmFsKGRhdGEubmFtZSk7XG4gICAgICAgICQoJyNvY2N1cmVuY2VzJykudmFsKGRhdGEudXNlZF9ieSk7XG5cbiAgICAgICAgLy8gVmlzaWJsZSBpbmZvcm1hdGlvblxuICAgICAgICAkKCcjdGFnX21vZGFsX3RpdGxlJykuaHRtbCgnVGFnOiAnICsgZGF0YS5uYW1lKTtcbiAgICAgICAgJCgnI3RhZ19uYW1lJykudmFsKGRhdGEubmFtZSk7XG4gICAgICAgICQoJyN0YWdfY29sb3InKS52YWwoZGF0YS5jb2xvcik7XG4gICAgICAgICQoJyN0YWctZGVzY3JpcHRpb24nKS52YWwoZGF0YS5kZXNjcmlwdGlvbik7XG5cbiAgICAgICAgdGFnX21vZGFsX2NvbnRlbnQuTG9hZGluZ092ZXJsYXkoJ2hpZGUnKTtcbiAgICB9KTtcblxuICAgIC8vIFN0b3JlIGNoYW5nZXMgb24gdGFnIG9uIHNhdmUuXG4gICAgJCgnI3NhdmVfdGFnX21vZGFsJykuY2xpY2soZnVuY3Rpb24gKCkge1xuICAgICAgICBzdG9yZV90YWcodGFnc19kYXRhdGFibGUpO1xuICAgIH0pO1xuXG4gICAgJCgnLmRlbGV0ZV90YWcnKS5jb25maXJtYXRpb24oe1xuICAgICAgcm9vdFNlbGVjdG9yOiAnLmRlbGV0ZV90YWcnXG4gICAgfSkuY2xpY2soZnVuY3Rpb24gKCkge1xuICAgICAgICBkZWxldGVfdGFnKCAkKHRoaXMpLmF0dHIoJ25hbWUnKSApO1xuICAgIH0pO1xuXG4gICAgYXV0b3NpemUoJCgnI3RhZy1kZXNjcmlwdGlvbicpKTtcblxuICAgICQoJyN0YWdfbW9kYWwnKS5vbignc2hvd24uYnMubW9kYWwnLCBmdW5jdGlvbiAoZSkge1xuICAgICAgICBhdXRvc2l6ZS51cGRhdGUoJCgnI3RhZy1kZXNjcmlwdGlvbicpKTtcbiAgICB9KTtcblxuICAgICQoJy5jbGVhci1hbGwtZmlsdGVycycpLmNsaWNrKGZ1bmN0aW9uICgpIHtcbiAgICAgICAgJCgnI3NlYXJjaF9iYXInKS52YWwoJycpLmVmZmVjdChcImhpZ2hsaWdodFwiLCB7Y29sb3I6ICdncmVlbid9LCA1MDApO1xuICAgICAgICB1cGRhdGVfc2VhcmNoKCk7XG4gICAgICAgIHRhZ3NfZGF0YXRhYmxlLmRyYXcoKTtcbiAgICB9KTtcbn0gKTtcbiJdLCJtYXBwaW5ncyI6IkFBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0EiLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./js/tags.js\n");

/***/ })

/******/ });