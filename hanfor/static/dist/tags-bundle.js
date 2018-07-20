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

eval("/* WEBPACK VAR INJECTION */(function($) {__webpack_require__(/*! gasparesganga-jquery-loading-overlay */ \"./node_modules/gasparesganga-jquery-loading-overlay/src/loadingoverlay.js\");\r\n__webpack_require__(/*! bootstrap */ \"./node_modules/bootstrap/dist/js/bootstrap.js\");\r\n__webpack_require__(/*! bootstrap-confirmation2 */ \"./node_modules/bootstrap-confirmation2/dist/bootstrap-confirmation.js\");\r\n__webpack_require__(/*! datatables.net-bs4 */ \"./node_modules/datatables.net-bs4/js/dataTables.bootstrap4.js\");\r\n__webpack_require__(/*! jquery-ui/ui/widgets/autocomplete */ \"./node_modules/jquery-ui/ui/widgets/autocomplete.js\");\r\n__webpack_require__(/*! ./bootstrap-tokenfield.js */ \"./js/bootstrap-tokenfield.js\");\r\n\r\nlet tag_search_string = sessionStorage.getItem('tag_search_string');\r\n\r\n/**\r\n * Store the currently active (in the modal) tag.\r\n * @param tags_datatable\r\n */\r\nfunction store_tag(tags_datatable) {\r\n    tag_modal_content = $('.modal-content');\r\n    tag_modal_content.LoadingOverlay('show');\r\n\r\n    // Get data.\r\n    tag_name = $('#tag_name').val();\r\n    tag_name_old = $('#tag_name_old').val();\r\n    occurences = $('#occurences').val();\r\n    tag_color = $('#tag_color').val();\r\n    associated_row_id = parseInt($('#modal_associated_row_index').val());\r\n\r\n    // Store the tag.\r\n    $.post( \"api/tag/update\",\r\n        {\r\n            name: tag_name,\r\n            name_old: tag_name_old,\r\n            occurences: occurences,\r\n            color: tag_color\r\n        },\r\n        // Update tag table on success or show an error message.\r\n        function( data ) {\r\n            tag_modal_content.LoadingOverlay('hide', true);\r\n            if (data['success'] === false) {\r\n                alert(data['errormsg']);\r\n            } else {\r\n                if (data.rebuild_table) {\r\n                    location.reload();\r\n                } else {\r\n                    tags_datatable.row(associated_row_id).data(data.data).draw();\r\n                    $('#tag_modal').modal('hide');\r\n                }\r\n            }\r\n    });\r\n}\r\n\r\n\r\nfunction delete_tag(name) {\r\n    tag_modal_content = $('.modal-content');\r\n    tag_modal_content.LoadingOverlay('show');\r\n\r\n    tag_name = $('#tag_name').val();\r\n    occurences = $('#occurences').val();\r\n    $.post( \"api/tag/del_tag\",\r\n        {\r\n            name: tag_name,\r\n            occurences: occurences\r\n        },\r\n        // Update tag table on success or show an error message.\r\n        function( data ) {\r\n            tag_modal_content.LoadingOverlay('hide', true);\r\n            if (data['success'] === false) {\r\n                alert(data['errormsg']);\r\n            } else {\r\n                if (data.rebuild_table) {\r\n                    location.reload();\r\n                } else {\r\n                    tags_datatable.row(associated_row_id).data(data.data).draw();\r\n                    $('#tag_modal').modal('hide');\r\n                }\r\n            }\r\n    });\r\n}\r\n\r\n$(document).ready(function() {\r\n    // Prepare and load the tags table.\r\n    tags_table = $('#tags_table');\r\n    tags_datatable = tags_table.DataTable({\r\n        \"paging\": true,\r\n        \"stateSave\": true,\r\n        \"pageLength\": 50,\r\n        \"responsive\": true,\r\n        \"lengthMenu\": [[10, 50, 100, 500, -1], [10, 50, 100, 500, \"All\"]],\r\n        \"dom\": 'rt<\"container\"<\"row\"<\"col-md-6\"li><\"col-md-6\"p>>>',\r\n        \"ajax\": \"api/tag/gets\",\r\n        \"deferRender\": true,\r\n        \"columns\": [\r\n            {\r\n                \"data\": \"name\",\r\n                \"render\": function ( data, type, row, meta ) {\r\n                    result = '<a class=\"modal-opener\" href=\"#\">' + data + '</span></br>';\r\n                    return result;\r\n                }\r\n            },\r\n            {\r\n                \"data\": \"used_by\",\r\n                \"render\": function ( data, type, row, meta ) {\r\n                    result = '';\r\n                    $(data).each(function (id, name) {\r\n                        if (name.length > 0) {\r\n                            search_query = '?command=search&col=2&q=' + name;\r\n                            result += '<span class=\"badge\" style=\"background-color: ' + row.color +'\">' +\r\n                                '<a href=\"' + base_url + search_query + '\" target=\"_blank\">' + name + '</a>' +\r\n                                '</span>';\r\n                        }\r\n                    });\r\n                    return result;\r\n                }\r\n\r\n            },\r\n            {\r\n                \"data\": \"used_by\",\r\n                \"visible\": false,\r\n                \"searchable\": false,\r\n                \"render\": function ( data, type, row, meta ) {\r\n                    result = '';\r\n                    $(data).each(function (id, name) {\r\n                        if (name.length > 0) {\r\n                            if (result.length > 1) {\r\n                                result += ', '\r\n                            }\r\n                            result += name;\r\n                        }\r\n                    });\r\n                    return result;\r\n                }\r\n            }\r\n        ],\r\n        initComplete : function() {\r\n            $('#search_bar').val(tag_search_string);\r\n        }\r\n    });\r\n    tags_datatable.column(2).visible(false);\r\n\r\n    // Bind big custom searchbar to search the table.\r\n    $('#search_bar').keyup(function(){\r\n      tags_datatable.search($(this).val()).draw();\r\n      sessionStorage.setItem('tag_search_string', $(this).val());\r\n    });\r\n\r\n    // Add listener for tag link to modal.\r\n    tags_table.find('tbody').on('click', 'a.modal-opener', function (event) {\r\n        // prevent body to be scrolled to the top.\r\n        event.preventDefault();\r\n\r\n        // Get row data\r\n        let data = tags_datatable.row($(event.target).parent()).data();\r\n        let row_id = tags_datatable.row($(event.target).parent()).index();\r\n\r\n        // Prepare tag modal\r\n        tag_modal_content = $('.modal-content');\r\n        $('#tag_modal').modal('show');\r\n        $('#modal_associated_row_index').val(row_id);\r\n\r\n        // Meta information\r\n        $('#tag_name_old').val(data.name);\r\n        $('#occurences').val(data.used_by);\r\n\r\n        // Visible information\r\n        $('#tag_modal_title').html('Tag: ' + data.name);\r\n        $('#tag_name').val(data.name);\r\n        $('#tag_color').val(data.color);\r\n\r\n        tag_modal_content.LoadingOverlay('hide');\r\n    });\r\n\r\n    // Store changes on tag on save.\r\n    $('#save_tag_modal').click(function () {\r\n        store_tag(tags_datatable);\r\n    });\r\n\r\n    $('.delete_tag').confirmation({\r\n      rootSelector: '.delete_tag'\r\n    }).click(function () {\r\n        delete_tag( $(this).attr('name') );\r\n    });\r\n} );\n/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\")))//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9qcy90YWdzLmpzLmpzIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vLy4vanMvdGFncy5qcz80MWEzIl0sInNvdXJjZXNDb250ZW50IjpbInJlcXVpcmUoJ2dhc3BhcmVzZ2FuZ2EtanF1ZXJ5LWxvYWRpbmctb3ZlcmxheScpO1xyXG5yZXF1aXJlKCdib290c3RyYXAnKTtcclxucmVxdWlyZSgnYm9vdHN0cmFwLWNvbmZpcm1hdGlvbjInKTtcclxucmVxdWlyZSgnZGF0YXRhYmxlcy5uZXQtYnM0Jyk7XHJcbnJlcXVpcmUoJ2pxdWVyeS11aS91aS93aWRnZXRzL2F1dG9jb21wbGV0ZScpO1xyXG5yZXF1aXJlKCcuL2Jvb3RzdHJhcC10b2tlbmZpZWxkLmpzJyk7XHJcblxyXG5sZXQgdGFnX3NlYXJjaF9zdHJpbmcgPSBzZXNzaW9uU3RvcmFnZS5nZXRJdGVtKCd0YWdfc2VhcmNoX3N0cmluZycpO1xyXG5cclxuLyoqXHJcbiAqIFN0b3JlIHRoZSBjdXJyZW50bHkgYWN0aXZlIChpbiB0aGUgbW9kYWwpIHRhZy5cclxuICogQHBhcmFtIHRhZ3NfZGF0YXRhYmxlXHJcbiAqL1xyXG5mdW5jdGlvbiBzdG9yZV90YWcodGFnc19kYXRhdGFibGUpIHtcclxuICAgIHRhZ19tb2RhbF9jb250ZW50ID0gJCgnLm1vZGFsLWNvbnRlbnQnKTtcclxuICAgIHRhZ19tb2RhbF9jb250ZW50LkxvYWRpbmdPdmVybGF5KCdzaG93Jyk7XHJcblxyXG4gICAgLy8gR2V0IGRhdGEuXHJcbiAgICB0YWdfbmFtZSA9ICQoJyN0YWdfbmFtZScpLnZhbCgpO1xyXG4gICAgdGFnX25hbWVfb2xkID0gJCgnI3RhZ19uYW1lX29sZCcpLnZhbCgpO1xyXG4gICAgb2NjdXJlbmNlcyA9ICQoJyNvY2N1cmVuY2VzJykudmFsKCk7XHJcbiAgICB0YWdfY29sb3IgPSAkKCcjdGFnX2NvbG9yJykudmFsKCk7XHJcbiAgICBhc3NvY2lhdGVkX3Jvd19pZCA9IHBhcnNlSW50KCQoJyNtb2RhbF9hc3NvY2lhdGVkX3Jvd19pbmRleCcpLnZhbCgpKTtcclxuXHJcbiAgICAvLyBTdG9yZSB0aGUgdGFnLlxyXG4gICAgJC5wb3N0KCBcImFwaS90YWcvdXBkYXRlXCIsXHJcbiAgICAgICAge1xyXG4gICAgICAgICAgICBuYW1lOiB0YWdfbmFtZSxcclxuICAgICAgICAgICAgbmFtZV9vbGQ6IHRhZ19uYW1lX29sZCxcclxuICAgICAgICAgICAgb2NjdXJlbmNlczogb2NjdXJlbmNlcyxcclxuICAgICAgICAgICAgY29sb3I6IHRhZ19jb2xvclxyXG4gICAgICAgIH0sXHJcbiAgICAgICAgLy8gVXBkYXRlIHRhZyB0YWJsZSBvbiBzdWNjZXNzIG9yIHNob3cgYW4gZXJyb3IgbWVzc2FnZS5cclxuICAgICAgICBmdW5jdGlvbiggZGF0YSApIHtcclxuICAgICAgICAgICAgdGFnX21vZGFsX2NvbnRlbnQuTG9hZGluZ092ZXJsYXkoJ2hpZGUnLCB0cnVlKTtcclxuICAgICAgICAgICAgaWYgKGRhdGFbJ3N1Y2Nlc3MnXSA9PT0gZmFsc2UpIHtcclxuICAgICAgICAgICAgICAgIGFsZXJ0KGRhdGFbJ2Vycm9ybXNnJ10pO1xyXG4gICAgICAgICAgICB9IGVsc2Uge1xyXG4gICAgICAgICAgICAgICAgaWYgKGRhdGEucmVidWlsZF90YWJsZSkge1xyXG4gICAgICAgICAgICAgICAgICAgIGxvY2F0aW9uLnJlbG9hZCgpO1xyXG4gICAgICAgICAgICAgICAgfSBlbHNlIHtcclxuICAgICAgICAgICAgICAgICAgICB0YWdzX2RhdGF0YWJsZS5yb3coYXNzb2NpYXRlZF9yb3dfaWQpLmRhdGEoZGF0YS5kYXRhKS5kcmF3KCk7XHJcbiAgICAgICAgICAgICAgICAgICAgJCgnI3RhZ19tb2RhbCcpLm1vZGFsKCdoaWRlJyk7XHJcbiAgICAgICAgICAgICAgICB9XHJcbiAgICAgICAgICAgIH1cclxuICAgIH0pO1xyXG59XHJcblxyXG5cclxuZnVuY3Rpb24gZGVsZXRlX3RhZyhuYW1lKSB7XHJcbiAgICB0YWdfbW9kYWxfY29udGVudCA9ICQoJy5tb2RhbC1jb250ZW50Jyk7XHJcbiAgICB0YWdfbW9kYWxfY29udGVudC5Mb2FkaW5nT3ZlcmxheSgnc2hvdycpO1xyXG5cclxuICAgIHRhZ19uYW1lID0gJCgnI3RhZ19uYW1lJykudmFsKCk7XHJcbiAgICBvY2N1cmVuY2VzID0gJCgnI29jY3VyZW5jZXMnKS52YWwoKTtcclxuICAgICQucG9zdCggXCJhcGkvdGFnL2RlbF90YWdcIixcclxuICAgICAgICB7XHJcbiAgICAgICAgICAgIG5hbWU6IHRhZ19uYW1lLFxyXG4gICAgICAgICAgICBvY2N1cmVuY2VzOiBvY2N1cmVuY2VzXHJcbiAgICAgICAgfSxcclxuICAgICAgICAvLyBVcGRhdGUgdGFnIHRhYmxlIG9uIHN1Y2Nlc3Mgb3Igc2hvdyBhbiBlcnJvciBtZXNzYWdlLlxyXG4gICAgICAgIGZ1bmN0aW9uKCBkYXRhICkge1xyXG4gICAgICAgICAgICB0YWdfbW9kYWxfY29udGVudC5Mb2FkaW5nT3ZlcmxheSgnaGlkZScsIHRydWUpO1xyXG4gICAgICAgICAgICBpZiAoZGF0YVsnc3VjY2VzcyddID09PSBmYWxzZSkge1xyXG4gICAgICAgICAgICAgICAgYWxlcnQoZGF0YVsnZXJyb3Jtc2cnXSk7XHJcbiAgICAgICAgICAgIH0gZWxzZSB7XHJcbiAgICAgICAgICAgICAgICBpZiAoZGF0YS5yZWJ1aWxkX3RhYmxlKSB7XHJcbiAgICAgICAgICAgICAgICAgICAgbG9jYXRpb24ucmVsb2FkKCk7XHJcbiAgICAgICAgICAgICAgICB9IGVsc2Uge1xyXG4gICAgICAgICAgICAgICAgICAgIHRhZ3NfZGF0YXRhYmxlLnJvdyhhc3NvY2lhdGVkX3Jvd19pZCkuZGF0YShkYXRhLmRhdGEpLmRyYXcoKTtcclxuICAgICAgICAgICAgICAgICAgICAkKCcjdGFnX21vZGFsJykubW9kYWwoJ2hpZGUnKTtcclxuICAgICAgICAgICAgICAgIH1cclxuICAgICAgICAgICAgfVxyXG4gICAgfSk7XHJcbn1cclxuXHJcbiQoZG9jdW1lbnQpLnJlYWR5KGZ1bmN0aW9uKCkge1xyXG4gICAgLy8gUHJlcGFyZSBhbmQgbG9hZCB0aGUgdGFncyB0YWJsZS5cclxuICAgIHRhZ3NfdGFibGUgPSAkKCcjdGFnc190YWJsZScpO1xyXG4gICAgdGFnc19kYXRhdGFibGUgPSB0YWdzX3RhYmxlLkRhdGFUYWJsZSh7XHJcbiAgICAgICAgXCJwYWdpbmdcIjogdHJ1ZSxcclxuICAgICAgICBcInN0YXRlU2F2ZVwiOiB0cnVlLFxyXG4gICAgICAgIFwicGFnZUxlbmd0aFwiOiA1MCxcclxuICAgICAgICBcInJlc3BvbnNpdmVcIjogdHJ1ZSxcclxuICAgICAgICBcImxlbmd0aE1lbnVcIjogW1sxMCwgNTAsIDEwMCwgNTAwLCAtMV0sIFsxMCwgNTAsIDEwMCwgNTAwLCBcIkFsbFwiXV0sXHJcbiAgICAgICAgXCJkb21cIjogJ3J0PFwiY29udGFpbmVyXCI8XCJyb3dcIjxcImNvbC1tZC02XCJsaT48XCJjb2wtbWQtNlwicD4+PicsXHJcbiAgICAgICAgXCJhamF4XCI6IFwiYXBpL3RhZy9nZXRzXCIsXHJcbiAgICAgICAgXCJkZWZlclJlbmRlclwiOiB0cnVlLFxyXG4gICAgICAgIFwiY29sdW1uc1wiOiBbXHJcbiAgICAgICAgICAgIHtcclxuICAgICAgICAgICAgICAgIFwiZGF0YVwiOiBcIm5hbWVcIixcclxuICAgICAgICAgICAgICAgIFwicmVuZGVyXCI6IGZ1bmN0aW9uICggZGF0YSwgdHlwZSwgcm93LCBtZXRhICkge1xyXG4gICAgICAgICAgICAgICAgICAgIHJlc3VsdCA9ICc8YSBjbGFzcz1cIm1vZGFsLW9wZW5lclwiIGhyZWY9XCIjXCI+JyArIGRhdGEgKyAnPC9zcGFuPjwvYnI+JztcclxuICAgICAgICAgICAgICAgICAgICByZXR1cm4gcmVzdWx0O1xyXG4gICAgICAgICAgICAgICAgfVxyXG4gICAgICAgICAgICB9LFxyXG4gICAgICAgICAgICB7XHJcbiAgICAgICAgICAgICAgICBcImRhdGFcIjogXCJ1c2VkX2J5XCIsXHJcbiAgICAgICAgICAgICAgICBcInJlbmRlclwiOiBmdW5jdGlvbiAoIGRhdGEsIHR5cGUsIHJvdywgbWV0YSApIHtcclxuICAgICAgICAgICAgICAgICAgICByZXN1bHQgPSAnJztcclxuICAgICAgICAgICAgICAgICAgICAkKGRhdGEpLmVhY2goZnVuY3Rpb24gKGlkLCBuYW1lKSB7XHJcbiAgICAgICAgICAgICAgICAgICAgICAgIGlmIChuYW1lLmxlbmd0aCA+IDApIHtcclxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIHNlYXJjaF9xdWVyeSA9ICc/Y29tbWFuZD1zZWFyY2gmY29sPTImcT0nICsgbmFtZTtcclxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIHJlc3VsdCArPSAnPHNwYW4gY2xhc3M9XCJiYWRnZVwiIHN0eWxlPVwiYmFja2dyb3VuZC1jb2xvcjogJyArIHJvdy5jb2xvciArJ1wiPicgK1xyXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICc8YSBocmVmPVwiJyArIGJhc2VfdXJsICsgc2VhcmNoX3F1ZXJ5ICsgJ1wiIHRhcmdldD1cIl9ibGFua1wiPicgKyBuYW1lICsgJzwvYT4nICtcclxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAnPC9zcGFuPic7XHJcbiAgICAgICAgICAgICAgICAgICAgICAgIH1cclxuICAgICAgICAgICAgICAgICAgICB9KTtcclxuICAgICAgICAgICAgICAgICAgICByZXR1cm4gcmVzdWx0O1xyXG4gICAgICAgICAgICAgICAgfVxyXG5cclxuICAgICAgICAgICAgfSxcclxuICAgICAgICAgICAge1xyXG4gICAgICAgICAgICAgICAgXCJkYXRhXCI6IFwidXNlZF9ieVwiLFxyXG4gICAgICAgICAgICAgICAgXCJ2aXNpYmxlXCI6IGZhbHNlLFxyXG4gICAgICAgICAgICAgICAgXCJzZWFyY2hhYmxlXCI6IGZhbHNlLFxyXG4gICAgICAgICAgICAgICAgXCJyZW5kZXJcIjogZnVuY3Rpb24gKCBkYXRhLCB0eXBlLCByb3csIG1ldGEgKSB7XHJcbiAgICAgICAgICAgICAgICAgICAgcmVzdWx0ID0gJyc7XHJcbiAgICAgICAgICAgICAgICAgICAgJChkYXRhKS5lYWNoKGZ1bmN0aW9uIChpZCwgbmFtZSkge1xyXG4gICAgICAgICAgICAgICAgICAgICAgICBpZiAobmFtZS5sZW5ndGggPiAwKSB7XHJcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICBpZiAocmVzdWx0Lmxlbmd0aCA+IDEpIHtcclxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICByZXN1bHQgKz0gJywgJ1xyXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgfVxyXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgcmVzdWx0ICs9IG5hbWU7XHJcbiAgICAgICAgICAgICAgICAgICAgICAgIH1cclxuICAgICAgICAgICAgICAgICAgICB9KTtcclxuICAgICAgICAgICAgICAgICAgICByZXR1cm4gcmVzdWx0O1xyXG4gICAgICAgICAgICAgICAgfVxyXG4gICAgICAgICAgICB9XHJcbiAgICAgICAgXSxcclxuICAgICAgICBpbml0Q29tcGxldGUgOiBmdW5jdGlvbigpIHtcclxuICAgICAgICAgICAgJCgnI3NlYXJjaF9iYXInKS52YWwodGFnX3NlYXJjaF9zdHJpbmcpO1xyXG4gICAgICAgIH1cclxuICAgIH0pO1xyXG4gICAgdGFnc19kYXRhdGFibGUuY29sdW1uKDIpLnZpc2libGUoZmFsc2UpO1xyXG5cclxuICAgIC8vIEJpbmQgYmlnIGN1c3RvbSBzZWFyY2hiYXIgdG8gc2VhcmNoIHRoZSB0YWJsZS5cclxuICAgICQoJyNzZWFyY2hfYmFyJykua2V5dXAoZnVuY3Rpb24oKXtcclxuICAgICAgdGFnc19kYXRhdGFibGUuc2VhcmNoKCQodGhpcykudmFsKCkpLmRyYXcoKTtcclxuICAgICAgc2Vzc2lvblN0b3JhZ2Uuc2V0SXRlbSgndGFnX3NlYXJjaF9zdHJpbmcnLCAkKHRoaXMpLnZhbCgpKTtcclxuICAgIH0pO1xyXG5cclxuICAgIC8vIEFkZCBsaXN0ZW5lciBmb3IgdGFnIGxpbmsgdG8gbW9kYWwuXHJcbiAgICB0YWdzX3RhYmxlLmZpbmQoJ3Rib2R5Jykub24oJ2NsaWNrJywgJ2EubW9kYWwtb3BlbmVyJywgZnVuY3Rpb24gKGV2ZW50KSB7XHJcbiAgICAgICAgLy8gcHJldmVudCBib2R5IHRvIGJlIHNjcm9sbGVkIHRvIHRoZSB0b3AuXHJcbiAgICAgICAgZXZlbnQucHJldmVudERlZmF1bHQoKTtcclxuXHJcbiAgICAgICAgLy8gR2V0IHJvdyBkYXRhXHJcbiAgICAgICAgbGV0IGRhdGEgPSB0YWdzX2RhdGF0YWJsZS5yb3coJChldmVudC50YXJnZXQpLnBhcmVudCgpKS5kYXRhKCk7XHJcbiAgICAgICAgbGV0IHJvd19pZCA9IHRhZ3NfZGF0YXRhYmxlLnJvdygkKGV2ZW50LnRhcmdldCkucGFyZW50KCkpLmluZGV4KCk7XHJcblxyXG4gICAgICAgIC8vIFByZXBhcmUgdGFnIG1vZGFsXHJcbiAgICAgICAgdGFnX21vZGFsX2NvbnRlbnQgPSAkKCcubW9kYWwtY29udGVudCcpO1xyXG4gICAgICAgICQoJyN0YWdfbW9kYWwnKS5tb2RhbCgnc2hvdycpO1xyXG4gICAgICAgICQoJyNtb2RhbF9hc3NvY2lhdGVkX3Jvd19pbmRleCcpLnZhbChyb3dfaWQpO1xyXG5cclxuICAgICAgICAvLyBNZXRhIGluZm9ybWF0aW9uXHJcbiAgICAgICAgJCgnI3RhZ19uYW1lX29sZCcpLnZhbChkYXRhLm5hbWUpO1xyXG4gICAgICAgICQoJyNvY2N1cmVuY2VzJykudmFsKGRhdGEudXNlZF9ieSk7XHJcblxyXG4gICAgICAgIC8vIFZpc2libGUgaW5mb3JtYXRpb25cclxuICAgICAgICAkKCcjdGFnX21vZGFsX3RpdGxlJykuaHRtbCgnVGFnOiAnICsgZGF0YS5uYW1lKTtcclxuICAgICAgICAkKCcjdGFnX25hbWUnKS52YWwoZGF0YS5uYW1lKTtcclxuICAgICAgICAkKCcjdGFnX2NvbG9yJykudmFsKGRhdGEuY29sb3IpO1xyXG5cclxuICAgICAgICB0YWdfbW9kYWxfY29udGVudC5Mb2FkaW5nT3ZlcmxheSgnaGlkZScpO1xyXG4gICAgfSk7XHJcblxyXG4gICAgLy8gU3RvcmUgY2hhbmdlcyBvbiB0YWcgb24gc2F2ZS5cclxuICAgICQoJyNzYXZlX3RhZ19tb2RhbCcpLmNsaWNrKGZ1bmN0aW9uICgpIHtcclxuICAgICAgICBzdG9yZV90YWcodGFnc19kYXRhdGFibGUpO1xyXG4gICAgfSk7XHJcblxyXG4gICAgJCgnLmRlbGV0ZV90YWcnKS5jb25maXJtYXRpb24oe1xyXG4gICAgICByb290U2VsZWN0b3I6ICcuZGVsZXRlX3RhZydcclxuICAgIH0pLmNsaWNrKGZ1bmN0aW9uICgpIHtcclxuICAgICAgICBkZWxldGVfdGFnKCAkKHRoaXMpLmF0dHIoJ25hbWUnKSApO1xyXG4gICAgfSk7XHJcbn0gKTsiXSwibWFwcGluZ3MiOiJBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QSIsInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./js/tags.js\n");

/***/ })

/******/ });