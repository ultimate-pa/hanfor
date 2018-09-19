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
/******/ 	__webpack_require__.p = "";
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

eval("/* WEBPACK VAR INJECTION */(function($) {__webpack_require__(/*! gasparesganga-jquery-loading-overlay */ \"./node_modules/gasparesganga-jquery-loading-overlay/src/loadingoverlay.js\");\n__webpack_require__(/*! bootstrap */ \"./node_modules/bootstrap/dist/js/bootstrap.js\");\n__webpack_require__(/*! bootstrap-confirmation2 */ \"./node_modules/bootstrap-confirmation2/dist/bootstrap-confirmation.js\");\n__webpack_require__(/*! datatables.net-bs4 */ \"./node_modules/datatables.net-bs4/js/dataTables.bootstrap4.js\");\n__webpack_require__(/*! jquery-ui/ui/widgets/autocomplete */ \"./node_modules/jquery-ui/ui/widgets/autocomplete.js\");\n__webpack_require__(/*! ./bootstrap-tokenfield.js */ \"./js/bootstrap-tokenfield.js\");\n\nlet tag_search_string = sessionStorage.getItem('tag_search_string');\n\n/**\n * Store the currently active (in the modal) tag.\n * @param tags_datatable\n */\nfunction store_tag(tags_datatable) {\n    tag_modal_content = $('.modal-content');\n    tag_modal_content.LoadingOverlay('show');\n\n    // Get data.\n    tag_name = $('#tag_name').val();\n    tag_name_old = $('#tag_name_old').val();\n    occurences = $('#occurences').val();\n    tag_color = $('#tag_color').val();\n    associated_row_id = parseInt($('#modal_associated_row_index').val());\n\n    // Store the tag.\n    $.post( \"api/tag/update\",\n        {\n            name: tag_name,\n            name_old: tag_name_old,\n            occurences: occurences,\n            color: tag_color\n        },\n        // Update tag table on success or show an error message.\n        function( data ) {\n            tag_modal_content.LoadingOverlay('hide', true);\n            if (data['success'] === false) {\n                alert(data['errormsg']);\n            } else {\n                if (data.rebuild_table) {\n                    location.reload();\n                } else {\n                    tags_datatable.row(associated_row_id).data(data.data).draw();\n                    $('#tag_modal').modal('hide');\n                }\n            }\n    });\n}\n\n\nfunction delete_tag(name) {\n    tag_modal_content = $('.modal-content');\n    tag_modal_content.LoadingOverlay('show');\n\n    tag_name = $('#tag_name').val();\n    occurences = $('#occurences').val();\n    $.post( \"api/tag/del_tag\",\n        {\n            name: tag_name,\n            occurences: occurences\n        },\n        // Update tag table on success or show an error message.\n        function( data ) {\n            tag_modal_content.LoadingOverlay('hide', true);\n            if (data['success'] === false) {\n                alert(data['errormsg']);\n            } else {\n                if (data.rebuild_table) {\n                    location.reload();\n                } else {\n                    tags_datatable.row(associated_row_id).data(data.data).draw();\n                    $('#tag_modal').modal('hide');\n                }\n            }\n    });\n}\n\n$(document).ready(function() {\n    // Prepare and load the tags table.\n    tags_table = $('#tags_table');\n    tags_datatable = tags_table.DataTable({\n        \"paging\": true,\n        \"stateSave\": true,\n        \"pageLength\": 50,\n        \"responsive\": true,\n        \"lengthMenu\": [[10, 50, 100, 500, -1], [10, 50, 100, 500, \"All\"]],\n        \"dom\": 'rt<\"container\"<\"row\"<\"col-md-6\"li><\"col-md-6\"p>>>',\n        \"ajax\": \"api/tag/gets\",\n        \"deferRender\": true,\n        \"columns\": [\n            {\n                \"data\": \"name\",\n                \"render\": function ( data, type, row, meta ) {\n                    result = '<a class=\"modal-opener\" href=\"#\">' + data + '</span></br>';\n                    return result;\n                }\n            },\n            {\n                \"data\": \"used_by\",\n                \"render\": function ( data, type, row, meta ) {\n                    result = '';\n                    $(data).each(function (id, name) {\n                        if (name.length > 0) {\n                            search_query = '?command=search&col=2&q=' + name;\n                            result += '<span class=\"badge\" style=\"background-color: ' + row.color +'\">' +\n                                '<a href=\"' + base_url + search_query + '\" target=\"_blank\">' + name + '</a>' +\n                                '</span>';\n                        }\n                    });\n                    return result;\n                }\n\n            },\n            {\n                \"data\": \"used_by\",\n                \"visible\": false,\n                \"searchable\": false,\n                \"render\": function ( data, type, row, meta ) {\n                    result = '';\n                    $(data).each(function (id, name) {\n                        if (name.length > 0) {\n                            if (result.length > 1) {\n                                result += ', '\n                            }\n                            result += name;\n                        }\n                    });\n                    return result;\n                }\n            }\n        ],\n        initComplete : function() {\n            $('#search_bar').val(tag_search_string);\n        }\n    });\n    tags_datatable.column(2).visible(false);\n\n    // Bind big custom searchbar to search the table.\n    $('#search_bar').keyup(function(){\n      tags_datatable.search($(this).val()).draw();\n      sessionStorage.setItem('tag_search_string', $(this).val());\n    });\n\n    // Add listener for tag link to modal.\n    tags_table.find('tbody').on('click', 'a.modal-opener', function (event) {\n        // prevent body to be scrolled to the top.\n        event.preventDefault();\n\n        // Get row data\n        let data = tags_datatable.row($(event.target).parent()).data();\n        let row_id = tags_datatable.row($(event.target).parent()).index();\n\n        // Prepare tag modal\n        tag_modal_content = $('.modal-content');\n        $('#tag_modal').modal('show');\n        $('#modal_associated_row_index').val(row_id);\n\n        // Meta information\n        $('#tag_name_old').val(data.name);\n        $('#occurences').val(data.used_by);\n\n        // Visible information\n        $('#tag_modal_title').html('Tag: ' + data.name);\n        $('#tag_name').val(data.name);\n        $('#tag_color').val(data.color);\n\n        tag_modal_content.LoadingOverlay('hide');\n    });\n\n    // Store changes on tag on save.\n    $('#save_tag_modal').click(function () {\n        store_tag(tags_datatable);\n    });\n\n    $('.delete_tag').confirmation({\n      rootSelector: '.delete_tag'\n    }).click(function () {\n        delete_tag( $(this).attr('name') );\n    });\n} );\n/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\")))//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9qcy90YWdzLmpzLmpzIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vLy4vanMvdGFncy5qcz80MWEzIl0sInNvdXJjZXNDb250ZW50IjpbInJlcXVpcmUoJ2dhc3BhcmVzZ2FuZ2EtanF1ZXJ5LWxvYWRpbmctb3ZlcmxheScpO1xucmVxdWlyZSgnYm9vdHN0cmFwJyk7XG5yZXF1aXJlKCdib290c3RyYXAtY29uZmlybWF0aW9uMicpO1xucmVxdWlyZSgnZGF0YXRhYmxlcy5uZXQtYnM0Jyk7XG5yZXF1aXJlKCdqcXVlcnktdWkvdWkvd2lkZ2V0cy9hdXRvY29tcGxldGUnKTtcbnJlcXVpcmUoJy4vYm9vdHN0cmFwLXRva2VuZmllbGQuanMnKTtcblxubGV0IHRhZ19zZWFyY2hfc3RyaW5nID0gc2Vzc2lvblN0b3JhZ2UuZ2V0SXRlbSgndGFnX3NlYXJjaF9zdHJpbmcnKTtcblxuLyoqXG4gKiBTdG9yZSB0aGUgY3VycmVudGx5IGFjdGl2ZSAoaW4gdGhlIG1vZGFsKSB0YWcuXG4gKiBAcGFyYW0gdGFnc19kYXRhdGFibGVcbiAqL1xuZnVuY3Rpb24gc3RvcmVfdGFnKHRhZ3NfZGF0YXRhYmxlKSB7XG4gICAgdGFnX21vZGFsX2NvbnRlbnQgPSAkKCcubW9kYWwtY29udGVudCcpO1xuICAgIHRhZ19tb2RhbF9jb250ZW50LkxvYWRpbmdPdmVybGF5KCdzaG93Jyk7XG5cbiAgICAvLyBHZXQgZGF0YS5cbiAgICB0YWdfbmFtZSA9ICQoJyN0YWdfbmFtZScpLnZhbCgpO1xuICAgIHRhZ19uYW1lX29sZCA9ICQoJyN0YWdfbmFtZV9vbGQnKS52YWwoKTtcbiAgICBvY2N1cmVuY2VzID0gJCgnI29jY3VyZW5jZXMnKS52YWwoKTtcbiAgICB0YWdfY29sb3IgPSAkKCcjdGFnX2NvbG9yJykudmFsKCk7XG4gICAgYXNzb2NpYXRlZF9yb3dfaWQgPSBwYXJzZUludCgkKCcjbW9kYWxfYXNzb2NpYXRlZF9yb3dfaW5kZXgnKS52YWwoKSk7XG5cbiAgICAvLyBTdG9yZSB0aGUgdGFnLlxuICAgICQucG9zdCggXCJhcGkvdGFnL3VwZGF0ZVwiLFxuICAgICAgICB7XG4gICAgICAgICAgICBuYW1lOiB0YWdfbmFtZSxcbiAgICAgICAgICAgIG5hbWVfb2xkOiB0YWdfbmFtZV9vbGQsXG4gICAgICAgICAgICBvY2N1cmVuY2VzOiBvY2N1cmVuY2VzLFxuICAgICAgICAgICAgY29sb3I6IHRhZ19jb2xvclxuICAgICAgICB9LFxuICAgICAgICAvLyBVcGRhdGUgdGFnIHRhYmxlIG9uIHN1Y2Nlc3Mgb3Igc2hvdyBhbiBlcnJvciBtZXNzYWdlLlxuICAgICAgICBmdW5jdGlvbiggZGF0YSApIHtcbiAgICAgICAgICAgIHRhZ19tb2RhbF9jb250ZW50LkxvYWRpbmdPdmVybGF5KCdoaWRlJywgdHJ1ZSk7XG4gICAgICAgICAgICBpZiAoZGF0YVsnc3VjY2VzcyddID09PSBmYWxzZSkge1xuICAgICAgICAgICAgICAgIGFsZXJ0KGRhdGFbJ2Vycm9ybXNnJ10pO1xuICAgICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgICAgICBpZiAoZGF0YS5yZWJ1aWxkX3RhYmxlKSB7XG4gICAgICAgICAgICAgICAgICAgIGxvY2F0aW9uLnJlbG9hZCgpO1xuICAgICAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgICAgIHRhZ3NfZGF0YXRhYmxlLnJvdyhhc3NvY2lhdGVkX3Jvd19pZCkuZGF0YShkYXRhLmRhdGEpLmRyYXcoKTtcbiAgICAgICAgICAgICAgICAgICAgJCgnI3RhZ19tb2RhbCcpLm1vZGFsKCdoaWRlJyk7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfVxuICAgIH0pO1xufVxuXG5cbmZ1bmN0aW9uIGRlbGV0ZV90YWcobmFtZSkge1xuICAgIHRhZ19tb2RhbF9jb250ZW50ID0gJCgnLm1vZGFsLWNvbnRlbnQnKTtcbiAgICB0YWdfbW9kYWxfY29udGVudC5Mb2FkaW5nT3ZlcmxheSgnc2hvdycpO1xuXG4gICAgdGFnX25hbWUgPSAkKCcjdGFnX25hbWUnKS52YWwoKTtcbiAgICBvY2N1cmVuY2VzID0gJCgnI29jY3VyZW5jZXMnKS52YWwoKTtcbiAgICAkLnBvc3QoIFwiYXBpL3RhZy9kZWxfdGFnXCIsXG4gICAgICAgIHtcbiAgICAgICAgICAgIG5hbWU6IHRhZ19uYW1lLFxuICAgICAgICAgICAgb2NjdXJlbmNlczogb2NjdXJlbmNlc1xuICAgICAgICB9LFxuICAgICAgICAvLyBVcGRhdGUgdGFnIHRhYmxlIG9uIHN1Y2Nlc3Mgb3Igc2hvdyBhbiBlcnJvciBtZXNzYWdlLlxuICAgICAgICBmdW5jdGlvbiggZGF0YSApIHtcbiAgICAgICAgICAgIHRhZ19tb2RhbF9jb250ZW50LkxvYWRpbmdPdmVybGF5KCdoaWRlJywgdHJ1ZSk7XG4gICAgICAgICAgICBpZiAoZGF0YVsnc3VjY2VzcyddID09PSBmYWxzZSkge1xuICAgICAgICAgICAgICAgIGFsZXJ0KGRhdGFbJ2Vycm9ybXNnJ10pO1xuICAgICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgICAgICBpZiAoZGF0YS5yZWJ1aWxkX3RhYmxlKSB7XG4gICAgICAgICAgICAgICAgICAgIGxvY2F0aW9uLnJlbG9hZCgpO1xuICAgICAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgICAgIHRhZ3NfZGF0YXRhYmxlLnJvdyhhc3NvY2lhdGVkX3Jvd19pZCkuZGF0YShkYXRhLmRhdGEpLmRyYXcoKTtcbiAgICAgICAgICAgICAgICAgICAgJCgnI3RhZ19tb2RhbCcpLm1vZGFsKCdoaWRlJyk7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfVxuICAgIH0pO1xufVxuXG4kKGRvY3VtZW50KS5yZWFkeShmdW5jdGlvbigpIHtcbiAgICAvLyBQcmVwYXJlIGFuZCBsb2FkIHRoZSB0YWdzIHRhYmxlLlxuICAgIHRhZ3NfdGFibGUgPSAkKCcjdGFnc190YWJsZScpO1xuICAgIHRhZ3NfZGF0YXRhYmxlID0gdGFnc190YWJsZS5EYXRhVGFibGUoe1xuICAgICAgICBcInBhZ2luZ1wiOiB0cnVlLFxuICAgICAgICBcInN0YXRlU2F2ZVwiOiB0cnVlLFxuICAgICAgICBcInBhZ2VMZW5ndGhcIjogNTAsXG4gICAgICAgIFwicmVzcG9uc2l2ZVwiOiB0cnVlLFxuICAgICAgICBcImxlbmd0aE1lbnVcIjogW1sxMCwgNTAsIDEwMCwgNTAwLCAtMV0sIFsxMCwgNTAsIDEwMCwgNTAwLCBcIkFsbFwiXV0sXG4gICAgICAgIFwiZG9tXCI6ICdydDxcImNvbnRhaW5lclwiPFwicm93XCI8XCJjb2wtbWQtNlwibGk+PFwiY29sLW1kLTZcInA+Pj4nLFxuICAgICAgICBcImFqYXhcIjogXCJhcGkvdGFnL2dldHNcIixcbiAgICAgICAgXCJkZWZlclJlbmRlclwiOiB0cnVlLFxuICAgICAgICBcImNvbHVtbnNcIjogW1xuICAgICAgICAgICAge1xuICAgICAgICAgICAgICAgIFwiZGF0YVwiOiBcIm5hbWVcIixcbiAgICAgICAgICAgICAgICBcInJlbmRlclwiOiBmdW5jdGlvbiAoIGRhdGEsIHR5cGUsIHJvdywgbWV0YSApIHtcbiAgICAgICAgICAgICAgICAgICAgcmVzdWx0ID0gJzxhIGNsYXNzPVwibW9kYWwtb3BlbmVyXCIgaHJlZj1cIiNcIj4nICsgZGF0YSArICc8L3NwYW4+PC9icj4nO1xuICAgICAgICAgICAgICAgICAgICByZXR1cm4gcmVzdWx0O1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgICB7XG4gICAgICAgICAgICAgICAgXCJkYXRhXCI6IFwidXNlZF9ieVwiLFxuICAgICAgICAgICAgICAgIFwicmVuZGVyXCI6IGZ1bmN0aW9uICggZGF0YSwgdHlwZSwgcm93LCBtZXRhICkge1xuICAgICAgICAgICAgICAgICAgICByZXN1bHQgPSAnJztcbiAgICAgICAgICAgICAgICAgICAgJChkYXRhKS5lYWNoKGZ1bmN0aW9uIChpZCwgbmFtZSkge1xuICAgICAgICAgICAgICAgICAgICAgICAgaWYgKG5hbWUubGVuZ3RoID4gMCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgIHNlYXJjaF9xdWVyeSA9ICc/Y29tbWFuZD1zZWFyY2gmY29sPTImcT0nICsgbmFtZTtcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICByZXN1bHQgKz0gJzxzcGFuIGNsYXNzPVwiYmFkZ2VcIiBzdHlsZT1cImJhY2tncm91bmQtY29sb3I6ICcgKyByb3cuY29sb3IgKydcIj4nICtcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgJzxhIGhyZWY9XCInICsgYmFzZV91cmwgKyBzZWFyY2hfcXVlcnkgKyAnXCIgdGFyZ2V0PVwiX2JsYW5rXCI+JyArIG5hbWUgKyAnPC9hPicgK1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAnPC9zcGFuPic7XG4gICAgICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgICAgICAgICByZXR1cm4gcmVzdWx0O1xuICAgICAgICAgICAgICAgIH1cblxuICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgICBcImRhdGFcIjogXCJ1c2VkX2J5XCIsXG4gICAgICAgICAgICAgICAgXCJ2aXNpYmxlXCI6IGZhbHNlLFxuICAgICAgICAgICAgICAgIFwic2VhcmNoYWJsZVwiOiBmYWxzZSxcbiAgICAgICAgICAgICAgICBcInJlbmRlclwiOiBmdW5jdGlvbiAoIGRhdGEsIHR5cGUsIHJvdywgbWV0YSApIHtcbiAgICAgICAgICAgICAgICAgICAgcmVzdWx0ID0gJyc7XG4gICAgICAgICAgICAgICAgICAgICQoZGF0YSkuZWFjaChmdW5jdGlvbiAoaWQsIG5hbWUpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIGlmIChuYW1lLmxlbmd0aCA+IDApIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICBpZiAocmVzdWx0Lmxlbmd0aCA+IDEpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgcmVzdWx0ICs9ICcsICdcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgcmVzdWx0ICs9IG5hbWU7XG4gICAgICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgICAgICAgICByZXR1cm4gcmVzdWx0O1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH1cbiAgICAgICAgXSxcbiAgICAgICAgaW5pdENvbXBsZXRlIDogZnVuY3Rpb24oKSB7XG4gICAgICAgICAgICAkKCcjc2VhcmNoX2JhcicpLnZhbCh0YWdfc2VhcmNoX3N0cmluZyk7XG4gICAgICAgIH1cbiAgICB9KTtcbiAgICB0YWdzX2RhdGF0YWJsZS5jb2x1bW4oMikudmlzaWJsZShmYWxzZSk7XG5cbiAgICAvLyBCaW5kIGJpZyBjdXN0b20gc2VhcmNoYmFyIHRvIHNlYXJjaCB0aGUgdGFibGUuXG4gICAgJCgnI3NlYXJjaF9iYXInKS5rZXl1cChmdW5jdGlvbigpe1xuICAgICAgdGFnc19kYXRhdGFibGUuc2VhcmNoKCQodGhpcykudmFsKCkpLmRyYXcoKTtcbiAgICAgIHNlc3Npb25TdG9yYWdlLnNldEl0ZW0oJ3RhZ19zZWFyY2hfc3RyaW5nJywgJCh0aGlzKS52YWwoKSk7XG4gICAgfSk7XG5cbiAgICAvLyBBZGQgbGlzdGVuZXIgZm9yIHRhZyBsaW5rIHRvIG1vZGFsLlxuICAgIHRhZ3NfdGFibGUuZmluZCgndGJvZHknKS5vbignY2xpY2snLCAnYS5tb2RhbC1vcGVuZXInLCBmdW5jdGlvbiAoZXZlbnQpIHtcbiAgICAgICAgLy8gcHJldmVudCBib2R5IHRvIGJlIHNjcm9sbGVkIHRvIHRoZSB0b3AuXG4gICAgICAgIGV2ZW50LnByZXZlbnREZWZhdWx0KCk7XG5cbiAgICAgICAgLy8gR2V0IHJvdyBkYXRhXG4gICAgICAgIGxldCBkYXRhID0gdGFnc19kYXRhdGFibGUucm93KCQoZXZlbnQudGFyZ2V0KS5wYXJlbnQoKSkuZGF0YSgpO1xuICAgICAgICBsZXQgcm93X2lkID0gdGFnc19kYXRhdGFibGUucm93KCQoZXZlbnQudGFyZ2V0KS5wYXJlbnQoKSkuaW5kZXgoKTtcblxuICAgICAgICAvLyBQcmVwYXJlIHRhZyBtb2RhbFxuICAgICAgICB0YWdfbW9kYWxfY29udGVudCA9ICQoJy5tb2RhbC1jb250ZW50Jyk7XG4gICAgICAgICQoJyN0YWdfbW9kYWwnKS5tb2RhbCgnc2hvdycpO1xuICAgICAgICAkKCcjbW9kYWxfYXNzb2NpYXRlZF9yb3dfaW5kZXgnKS52YWwocm93X2lkKTtcblxuICAgICAgICAvLyBNZXRhIGluZm9ybWF0aW9uXG4gICAgICAgICQoJyN0YWdfbmFtZV9vbGQnKS52YWwoZGF0YS5uYW1lKTtcbiAgICAgICAgJCgnI29jY3VyZW5jZXMnKS52YWwoZGF0YS51c2VkX2J5KTtcblxuICAgICAgICAvLyBWaXNpYmxlIGluZm9ybWF0aW9uXG4gICAgICAgICQoJyN0YWdfbW9kYWxfdGl0bGUnKS5odG1sKCdUYWc6ICcgKyBkYXRhLm5hbWUpO1xuICAgICAgICAkKCcjdGFnX25hbWUnKS52YWwoZGF0YS5uYW1lKTtcbiAgICAgICAgJCgnI3RhZ19jb2xvcicpLnZhbChkYXRhLmNvbG9yKTtcblxuICAgICAgICB0YWdfbW9kYWxfY29udGVudC5Mb2FkaW5nT3ZlcmxheSgnaGlkZScpO1xuICAgIH0pO1xuXG4gICAgLy8gU3RvcmUgY2hhbmdlcyBvbiB0YWcgb24gc2F2ZS5cbiAgICAkKCcjc2F2ZV90YWdfbW9kYWwnKS5jbGljayhmdW5jdGlvbiAoKSB7XG4gICAgICAgIHN0b3JlX3RhZyh0YWdzX2RhdGF0YWJsZSk7XG4gICAgfSk7XG5cbiAgICAkKCcuZGVsZXRlX3RhZycpLmNvbmZpcm1hdGlvbih7XG4gICAgICByb290U2VsZWN0b3I6ICcuZGVsZXRlX3RhZydcbiAgICB9KS5jbGljayhmdW5jdGlvbiAoKSB7XG4gICAgICAgIGRlbGV0ZV90YWcoICQodGhpcykuYXR0cignbmFtZScpICk7XG4gICAgfSk7XG59ICk7Il0sIm1hcHBpbmdzIjoiQUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0EiLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./js/tags.js\n");

/***/ })

/******/ });