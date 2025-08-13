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

/***/ "../example_blueprint/static/example_blueprint.js":
/*!********************************************************!*\
  !*** ../example_blueprint/static/example_blueprint.js ***!
  \********************************************************/
/***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {

eval("/* provided dependency */ var $ = __webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\");\n__webpack_require__(/*! bootstrap */ \"./node_modules/bootstrap/dist/js/bootstrap.esm.js\")\r\n__webpack_require__(/*! datatables.net-bs5 */ \"./node_modules/datatables.net-bs5/js/dataTables.bootstrap5.mjs\")\r\n__webpack_require__(/*! datatables.net-colreorder-bs5 */ \"./node_modules/datatables.net-colreorder-bs5/js/colReorder.bootstrap5.mjs\")\r\n__webpack_require__(/*! ../../telemetry/static/telemetry */ \"../telemetry/static/telemetry.js\")  // To enable telemetry pause functions\r\n\r\nconst {SearchNode} = __webpack_require__(/*! ../../static/js/datatables-advanced-search */ \"./js/datatables-advanced-search.js\");\r\n\r\nconst exampleSearchString = sessionStorage.getItem('exampleSearchString')\r\n\r\nlet search_tree\r\n\r\nconst dataTableColumns = [\r\n    {\r\n        data: 'id',\r\n        render: function (data) {\r\n            return `<div class=\"white-space-pre\">${data}</div>`\r\n        }\r\n    }, {\r\n        data: 'name',\r\n        render: function (data) {\r\n            return `<div class=\"white-space-pre\">${data}</div>`\r\n        }\r\n    }, {\r\n        data: 'age',\r\n        render: function (data) {\r\n            return `<div class=\"white-space-pre\">${data}</div>`\r\n        }\r\n    }, {\r\n        data: 'city',\r\n        render: function (data) {\r\n            return `<div class=\"white-space-pre\">${data}</div>`\r\n        }\r\n    }\r\n]\r\n\r\n$(document).ready(function () {\r\n    const searchInput = $('#search_bar')\r\n    const table = $('#example-blueprint-tbl')\r\n    const dataTable = table.DataTable({\r\n        paging: true,\r\n        stateSave: true,\r\n        pageLength: 50,\r\n        responsive: true,\r\n        lengthMenu: [[10, 50, 100, 500, -1], [10, 50, 100, 500, 'All']],\r\n        dom: 'rt<\"container\"<\"row\"<\"col-md-6\"li><\"col-md-6\"p>>>',\r\n        ajax: {\r\n            url: 'api/v1/example-blueprint/',\r\n            dataSrc: function (json) {\r\n                // Convert dictionary to array\r\n                return Object.keys(json[\"data\"]).map(id => ({\r\n                    id: id, // Extract the ID as a field\r\n                    ...json[\"data\"][id] // Spread the actual data fields\r\n                }));\r\n            }\r\n        },\r\n        deferRender: true,\r\n        columns: dataTableColumns,\r\n        initComplete: function () {\r\n            searchInput.val(exampleSearchString);\r\n            update_search(searchInput.val().trim());\r\n\r\n            // Enable Hanfor specific table filtering.\r\n            $.fn.dataTable.ext.search.push(function (settings, data) {\r\n                // data contains the row. data[0] is the content of the first column in the actual row.\r\n                // Return true to include the row into the data. false to exclude.\r\n                return evaluate_search(data);\r\n            })\r\n            this.api().draw();\r\n        }\r\n    });\r\n\r\n    // Bind big custom searchbar to search the table.\r\n    searchInput.keypress(function (e) {\r\n        if (e.which === 13) { // Search on enter.\r\n            update_search(searchInput.val().trim());\r\n            dataTable.draw();\r\n        }\r\n    });\r\n\r\n    $('.clear-all-filters').click(function () {\r\n        searchInput.val('').effect('highlight', {color: 'green'}, 500);\r\n        update_search(searchInput.val().trim());\r\n        dataTable.draw();\r\n    });\r\n\r\n    $(\"#userForm\").submit(function (event) {\r\n        event.preventDefault(); // Prevent page reload\r\n\r\n        let userData = {\r\n            name: $(\"#name\").val().trim(),\r\n            age: parseInt($(\"#age\").val()),\r\n            city: $(\"#city\").val().trim()\r\n        };\r\n\r\n        $.ajax({\r\n            url: \"api/v1/example-blueprint/\",\r\n            type: \"POST\",\r\n            contentType: \"application/json\",\r\n            data: JSON.stringify(userData),\r\n            success: function (response) {\r\n                console.log(response)\r\n                $(\"#message\").html('<div class=\"alert alert-success\">User added successfully!</div>');\r\n                $(\"#userForm\")[0].reset(); // Reset form\r\n                dataTable.ajax.reload(null, false); // 'false' prevents page reset\r\n            },\r\n            error: function (xhr) {\r\n                $(\"#message\").html('<div class=\"alert alert-danger\">Error: ' + xhr.responseText + '</div>');\r\n            }\r\n        });\r\n    });\r\n\r\n    $(\"#deleteForm\").submit(function (event) {\r\n        event.preventDefault(); // Prevent page reload\r\n\r\n        let userId = $(\"#userId\").val().trim();\r\n\r\n        $.ajax({\r\n            url: `api/v1/example-blueprint/${userId}`, // Use the entered ID in the URL\r\n            type: \"DELETE\",\r\n            success: function (response) {\r\n                $(\"#deleteMessage\").html('<div class=\"alert alert-success\">User deleted successfully!</div>');\r\n                $(\"#deleteForm\")[0].reset(); // Reset form\r\n\r\n                // Reload the DataTable to reflect the changes\r\n                dataTable.ajax.reload(null, false); // 'false' prevents page reset\r\n            },\r\n            error: function (xhr) {\r\n                $(\"#deleteMessage\").html('<div class=\"alert alert-danger\">Error: ' + xhr.responseText + '</div>');\r\n            }\r\n        });\r\n    });\r\n})\r\n\r\nfunction update_search(string) {\r\n    sessionStorage.setItem('ultimateSearchString', string)\r\n    search_tree = SearchNode.fromQuery(string)\r\n}\r\n\r\nfunction evaluate_search(data) {\r\n    return search_tree.evaluate(data, [true, true, true])\r\n}\n\n//# sourceURL=webpack://hanfor/../example_blueprint/static/example_blueprint.js?");

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
/******/ 			"example_blueprint": 0
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
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, ["commons"], () => (__webpack_require__("../example_blueprint/static/example_blueprint.js")))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;