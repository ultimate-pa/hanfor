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
/******/ 		"ultimate": 0
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
/******/ 	deferredModules.push(["./js/ultimate.js","commons"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "./js/ultimate.js":
/*!************************!*\
  !*** ./js/ultimate.js ***!
  \************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("/* WEBPACK VAR INJECTION */(function($) {__webpack_require__(/*! gasparesganga-jquery-loading-overlay */ \"./node_modules/gasparesganga-jquery-loading-overlay/src/loadingoverlay.js\");\n__webpack_require__(/*! bootstrap */ \"./node_modules/bootstrap/dist/js/bootstrap.js\");\n__webpack_require__(/*! bootstrap-confirmation2 */ \"./node_modules/bootstrap-confirmation2/dist/bootstrap-confirmation.js\");\n__webpack_require__(/*! datatables.net-bs4 */ \"./node_modules/datatables.net-bs4/js/dataTables.bootstrap4.js\");\n__webpack_require__(/*! jquery-ui/ui/widgets/autocomplete */ \"./node_modules/jquery-ui/ui/widgets/autocomplete.js\");\n__webpack_require__(/*! jquery-ui/ui/effects/effect-highlight */ \"./node_modules/jquery-ui/ui/effects/effect-highlight.js\");\n__webpack_require__(/*! ./bootstrap-tokenfield.js */ \"./js/bootstrap-tokenfield.js\");\n__webpack_require__(/*! awesomplete */ \"./node_modules/awesomplete/awesomplete.js\");\n__webpack_require__(/*! awesomplete/awesomplete.css */ \"./node_modules/awesomplete/awesomplete.css\");\n__webpack_require__(/*! ./colResizable-1.6.min.js */ \"./js/colResizable-1.6.min.js\");\n\n$(document).ready(function() {\n    let runs_table = $('#ultimate_runs_table');\n    let runs_datatable = runs_table.DataTable({\n        \"paging\": true,\n        \"stateSave\": true,\n        \"pageLength\": 50,\n        \"responsive\": true,\n        \"lengthMenu\": [[10, 50, 100, 500, -1], [10, 50, 100, 500, \"All\"]],\n        \"dom\": 'rt<\"container\"<\"row\"<\"col-md-6\"li><\"col-md-6\"p>>>',\n        \"ajax\": \"api/ultimate/runs\",\n        \"deferRender\": true,\n        \"columns\": [\n            {\n                \"data\": \"id\",\n                \"render\": function ( data, type, row, meta ) {\n                  console.log(data);\n                    result = '<a class=\"modal-opener\" href=\"#\">' + data + '</span></br>';\n                    return result;\n                }\n            },\n            {\n                \"data\": \"queued_human\",\n                \"render\": function ( data, type, row, meta ) {\n                    result = '<div class=\"white-space-pre\">' + data + '</div>';\n                    return result;\n                }\n\n            },\n            {\n                \"data\": \"status\",\n                \"render\": function ( data, type, row, meta ) {\n                    result = '<div class=\"white-space-pre\">' + data + '</div>';\n                    return result;\n                }\n\n            }\n        ],\n        initComplete : function() {\n        }\n    });\n\n    // Add listener for tag link to modal.\n    runs_table.find('tbody').on('click', 'a.modal-opener', function (event) {\n        // prevent body to be scrolled to the top.\n        event.preventDefault();\n\n        // Get row data\n        let data = runs_datatable.row($(event.target).parent()).data();\n        let row_id = runs_datatable.row($(event.target).parent()).index();\n\n        // Prepare modal\n        let modal_content = $('.modal-content');\n        $('#ultimate_run_modal').modal('show');\n        // modal_content.LoadingOverlay('show');\n        $('#modal_associated_row_index').val(row_id);\n\n        // Meta information\n        $('#tag_name_old').val(data.name);\n        $('#occurences').val(data.used_by);\n\n        // Visible information\n        $('#tag_modal_title').html('Ultimate run: ' + data.id);\n\n        modal_content.LoadingOverlay('hide');\n    });\n\n    $('#stop_ultimate_run').confirmation({\n      rootSelector: '#stop_ultimate_run'\n    }).click(function () {\n        alert('stopping ultimate run not implemented yet.')\n    });\n\n    $('#delete_ultimate_run').confirmation({\n      rootSelector: '#delete_ultimate_run'\n    }).click(function () {\n        alert('deleting ultimate run not implemented yet.')\n    });\n});\n\n/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\")))//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9qcy91bHRpbWF0ZS5qcy5qcyIsInNvdXJjZXMiOlsid2VicGFjazovLy8uL2pzL3VsdGltYXRlLmpzP2U1NzYiXSwic291cmNlc0NvbnRlbnQiOlsicmVxdWlyZSgnZ2FzcGFyZXNnYW5nYS1qcXVlcnktbG9hZGluZy1vdmVybGF5Jyk7XG5yZXF1aXJlKCdib290c3RyYXAnKTtcbnJlcXVpcmUoJ2Jvb3RzdHJhcC1jb25maXJtYXRpb24yJyk7XG5yZXF1aXJlKCdkYXRhdGFibGVzLm5ldC1iczQnKTtcbnJlcXVpcmUoJ2pxdWVyeS11aS91aS93aWRnZXRzL2F1dG9jb21wbGV0ZScpO1xucmVxdWlyZSgnanF1ZXJ5LXVpL3VpL2VmZmVjdHMvZWZmZWN0LWhpZ2hsaWdodCcpO1xucmVxdWlyZSgnLi9ib290c3RyYXAtdG9rZW5maWVsZC5qcycpO1xucmVxdWlyZSgnYXdlc29tcGxldGUnKTtcbnJlcXVpcmUoJ2F3ZXNvbXBsZXRlL2F3ZXNvbXBsZXRlLmNzcycpO1xucmVxdWlyZSgnLi9jb2xSZXNpemFibGUtMS42Lm1pbi5qcycpO1xuXG4kKGRvY3VtZW50KS5yZWFkeShmdW5jdGlvbigpIHtcbiAgICBsZXQgcnVuc190YWJsZSA9ICQoJyN1bHRpbWF0ZV9ydW5zX3RhYmxlJyk7XG4gICAgbGV0IHJ1bnNfZGF0YXRhYmxlID0gcnVuc190YWJsZS5EYXRhVGFibGUoe1xuICAgICAgICBcInBhZ2luZ1wiOiB0cnVlLFxuICAgICAgICBcInN0YXRlU2F2ZVwiOiB0cnVlLFxuICAgICAgICBcInBhZ2VMZW5ndGhcIjogNTAsXG4gICAgICAgIFwicmVzcG9uc2l2ZVwiOiB0cnVlLFxuICAgICAgICBcImxlbmd0aE1lbnVcIjogW1sxMCwgNTAsIDEwMCwgNTAwLCAtMV0sIFsxMCwgNTAsIDEwMCwgNTAwLCBcIkFsbFwiXV0sXG4gICAgICAgIFwiZG9tXCI6ICdydDxcImNvbnRhaW5lclwiPFwicm93XCI8XCJjb2wtbWQtNlwibGk+PFwiY29sLW1kLTZcInA+Pj4nLFxuICAgICAgICBcImFqYXhcIjogXCJhcGkvdWx0aW1hdGUvcnVuc1wiLFxuICAgICAgICBcImRlZmVyUmVuZGVyXCI6IHRydWUsXG4gICAgICAgIFwiY29sdW1uc1wiOiBbXG4gICAgICAgICAgICB7XG4gICAgICAgICAgICAgICAgXCJkYXRhXCI6IFwiaWRcIixcbiAgICAgICAgICAgICAgICBcInJlbmRlclwiOiBmdW5jdGlvbiAoIGRhdGEsIHR5cGUsIHJvdywgbWV0YSApIHtcbiAgICAgICAgICAgICAgICAgIGNvbnNvbGUubG9nKGRhdGEpO1xuICAgICAgICAgICAgICAgICAgICByZXN1bHQgPSAnPGEgY2xhc3M9XCJtb2RhbC1vcGVuZXJcIiBocmVmPVwiI1wiPicgKyBkYXRhICsgJzwvc3Bhbj48L2JyPic7XG4gICAgICAgICAgICAgICAgICAgIHJldHVybiByZXN1bHQ7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgICBcImRhdGFcIjogXCJxdWV1ZWRfaHVtYW5cIixcbiAgICAgICAgICAgICAgICBcInJlbmRlclwiOiBmdW5jdGlvbiAoIGRhdGEsIHR5cGUsIHJvdywgbWV0YSApIHtcbiAgICAgICAgICAgICAgICAgICAgcmVzdWx0ID0gJzxkaXYgY2xhc3M9XCJ3aGl0ZS1zcGFjZS1wcmVcIj4nICsgZGF0YSArICc8L2Rpdj4nO1xuICAgICAgICAgICAgICAgICAgICByZXR1cm4gcmVzdWx0O1xuICAgICAgICAgICAgICAgIH1cblxuICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgICBcImRhdGFcIjogXCJzdGF0dXNcIixcbiAgICAgICAgICAgICAgICBcInJlbmRlclwiOiBmdW5jdGlvbiAoIGRhdGEsIHR5cGUsIHJvdywgbWV0YSApIHtcbiAgICAgICAgICAgICAgICAgICAgcmVzdWx0ID0gJzxkaXYgY2xhc3M9XCJ3aGl0ZS1zcGFjZS1wcmVcIj4nICsgZGF0YSArICc8L2Rpdj4nO1xuICAgICAgICAgICAgICAgICAgICByZXR1cm4gcmVzdWx0O1xuICAgICAgICAgICAgICAgIH1cblxuICAgICAgICAgICAgfVxuICAgICAgICBdLFxuICAgICAgICBpbml0Q29tcGxldGUgOiBmdW5jdGlvbigpIHtcbiAgICAgICAgfVxuICAgIH0pO1xuXG4gICAgLy8gQWRkIGxpc3RlbmVyIGZvciB0YWcgbGluayB0byBtb2RhbC5cbiAgICBydW5zX3RhYmxlLmZpbmQoJ3Rib2R5Jykub24oJ2NsaWNrJywgJ2EubW9kYWwtb3BlbmVyJywgZnVuY3Rpb24gKGV2ZW50KSB7XG4gICAgICAgIC8vIHByZXZlbnQgYm9keSB0byBiZSBzY3JvbGxlZCB0byB0aGUgdG9wLlxuICAgICAgICBldmVudC5wcmV2ZW50RGVmYXVsdCgpO1xuXG4gICAgICAgIC8vIEdldCByb3cgZGF0YVxuICAgICAgICBsZXQgZGF0YSA9IHJ1bnNfZGF0YXRhYmxlLnJvdygkKGV2ZW50LnRhcmdldCkucGFyZW50KCkpLmRhdGEoKTtcbiAgICAgICAgbGV0IHJvd19pZCA9IHJ1bnNfZGF0YXRhYmxlLnJvdygkKGV2ZW50LnRhcmdldCkucGFyZW50KCkpLmluZGV4KCk7XG5cbiAgICAgICAgLy8gUHJlcGFyZSBtb2RhbFxuICAgICAgICBsZXQgbW9kYWxfY29udGVudCA9ICQoJy5tb2RhbC1jb250ZW50Jyk7XG4gICAgICAgICQoJyN1bHRpbWF0ZV9ydW5fbW9kYWwnKS5tb2RhbCgnc2hvdycpO1xuICAgICAgICAvLyBtb2RhbF9jb250ZW50LkxvYWRpbmdPdmVybGF5KCdzaG93Jyk7XG4gICAgICAgICQoJyNtb2RhbF9hc3NvY2lhdGVkX3Jvd19pbmRleCcpLnZhbChyb3dfaWQpO1xuXG4gICAgICAgIC8vIE1ldGEgaW5mb3JtYXRpb25cbiAgICAgICAgJCgnI3RhZ19uYW1lX29sZCcpLnZhbChkYXRhLm5hbWUpO1xuICAgICAgICAkKCcjb2NjdXJlbmNlcycpLnZhbChkYXRhLnVzZWRfYnkpO1xuXG4gICAgICAgIC8vIFZpc2libGUgaW5mb3JtYXRpb25cbiAgICAgICAgJCgnI3RhZ19tb2RhbF90aXRsZScpLmh0bWwoJ1VsdGltYXRlIHJ1bjogJyArIGRhdGEuaWQpO1xuXG4gICAgICAgIG1vZGFsX2NvbnRlbnQuTG9hZGluZ092ZXJsYXkoJ2hpZGUnKTtcbiAgICB9KTtcblxuICAgICQoJyNzdG9wX3VsdGltYXRlX3J1bicpLmNvbmZpcm1hdGlvbih7XG4gICAgICByb290U2VsZWN0b3I6ICcjc3RvcF91bHRpbWF0ZV9ydW4nXG4gICAgfSkuY2xpY2soZnVuY3Rpb24gKCkge1xuICAgICAgICBhbGVydCgnc3RvcHBpbmcgdWx0aW1hdGUgcnVuIG5vdCBpbXBsZW1lbnRlZCB5ZXQuJylcbiAgICB9KTtcblxuICAgICQoJyNkZWxldGVfdWx0aW1hdGVfcnVuJykuY29uZmlybWF0aW9uKHtcbiAgICAgIHJvb3RTZWxlY3RvcjogJyNkZWxldGVfdWx0aW1hdGVfcnVuJ1xuICAgIH0pLmNsaWNrKGZ1bmN0aW9uICgpIHtcbiAgICAgICAgYWxlcnQoJ2RlbGV0aW5nIHVsdGltYXRlIHJ1biBub3QgaW1wbGVtZW50ZWQgeWV0LicpXG4gICAgfSk7XG59KTtcbiJdLCJtYXBwaW5ncyI6IkFBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QSIsInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./js/ultimate.js\n");

/***/ })

/******/ });