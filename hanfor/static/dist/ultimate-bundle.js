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

/***/ "../ultimate/static/ultimate.js":
/*!**************************************!*\
  !*** ../ultimate/static/ultimate.js ***!
  \**************************************/
/***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {

eval("/* provided dependency */ var $ = __webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\");\n__webpack_require__(/*! gasparesganga-jquery-loading-overlay */ \"./node_modules/gasparesganga-jquery-loading-overlay/dist/loadingoverlay.min.js\")\r\n__webpack_require__(/*! bootstrap */ \"./node_modules/bootstrap/dist/js/bootstrap.esm.js\")\r\n__webpack_require__(/*! datatables.net-bs5 */ \"./node_modules/datatables.net-bs5/js/dataTables.bootstrap5.mjs\")\r\n__webpack_require__(/*! jquery-ui/ui/effects/effect-highlight */ \"./node_modules/jquery-ui/ui/effects/effect-highlight.js\")\r\n__webpack_require__(/*! ../../static/js/bootstrap-tokenfield.js */ \"./js/bootstrap-tokenfield.js\")\r\n__webpack_require__(/*! ../../static/js/bootstrap-confirm-button */ \"./js/bootstrap-confirm-button.js\")\r\n__webpack_require__(/*! datatables.net-colreorder-bs5 */ \"./node_modules/datatables.net-colreorder-bs5/js/colReorder.bootstrap5.mjs\")\r\n__webpack_require__(/*! ../../telemetry/static/telemetry */ \"../telemetry/static/telemetry.js\")\r\n\r\nconst {SearchNode} = __webpack_require__(/*! ../../static/js/datatables-advanced-search */ \"./js/datatables-advanced-search.js\");\r\nconst ultimateSearchString = sessionStorage.getItem('ultimateSearchString')\r\nconst {Modal} = __webpack_require__(/*! bootstrap */ \"./node_modules/bootstrap/dist/js/bootstrap.esm.js\")\r\n\r\nlet search_tree\r\nlet reload_timer\r\n\r\n$(document).ready(function () {\r\n    const searchInput = $('#search_bar')\r\n    const ultimateJobsTable = $('#ultimate-jobs-tbl')\r\n    const ultimateJobsDataTable = ultimateJobsTable.DataTable({\r\n        paging: true,\r\n        stateSave: true,\r\n        pageLength: 50,\r\n        responsive: true,\r\n        lengthMenu: [[10, 50, 100, 500, -1], [10, 50, 100, 500, 'All']],\r\n        dom: 'rt<\"container\"<\"row\"<\"col-md-6\"li><\"col-md-6\"p>>>',\r\n        ajax: {\r\n            url: 'api/v1/ultimate/jobs'\r\n        },\r\n        deferRender: true,\r\n        columns: dataTableColumns,\r\n        initComplete: function () {\r\n            searchInput.val(ultimateSearchString);\r\n            update_search(searchInput.val().trim());\r\n\r\n            // Enable Hanfor specific table filtering.\r\n            $.fn.dataTable.ext.search.push(function (settings, data) {\r\n                // data contains the row. data[0] is the content of the first column in the actual row.\r\n                // Return true to include the row into the data. false to exclude.\r\n                return evaluate_search(data);\r\n            })\r\n            this.api().draw();\r\n            updateTableData()\r\n        }\r\n    });\r\n\r\n    // Bind big custom searchbar to search the table.\r\n    searchInput.keypress(function (e) {\r\n        if (e.which === 13) { // Search on enter.\r\n            update_search(searchInput.val().trim());\r\n            ultimateJobsDataTable.draw();\r\n        }\r\n    });\r\n\r\n    $('.clear-all-filters').click(function () {\r\n        searchInput.val('').effect('highlight', {color: 'green'}, 500);\r\n        update_search(searchInput.val().trim());\r\n        ultimateJobsDataTable.draw();\r\n    });\r\n\r\n    const ultimateResultTable = $('#ultimate-job-modal-result-tbl')\r\n    const ultimateResultDataTable = ultimateResultTable.DataTable({\r\n        paging: true,\r\n        stateSave: true,\r\n        pageLength: 50,\r\n        responsive: true,\r\n        lengthMenu: [[10, 50, 100, 500, -1], [10, 50, 100, 500, 'All']],\r\n        dom: 'rt<\"container\"<\"row\"<\"col-md-6\"li><\"col-md-6\"p>>>',\r\n        deferRender: true,\r\n        columns: resultDataTableColumns,\r\n        initComplete: function () {\r\n            this.api().draw()\r\n        }\r\n    });\r\n\r\n    // Add listener for job_link link to modal.\r\n    ultimateJobsTable.find('tbody').on('click', 'a.modal-opener', function (event) {\r\n        // prevent body to be scrolled to the top.\r\n        event.preventDefault();\r\n\r\n        // Get row data\r\n        let data = ultimateJobsDataTable.row($(event.target).parent()).data();\r\n\r\n        Modal.getOrCreateInstance($('#ultimate-job-modal')).show();\r\n        $('#ultimate-job-modal-title').html('Job ID: ' + data['requestId']);\r\n\r\n        $('#ultimate-job-modal-request-time').text(data['request_time']);\r\n        $('#ultimate-job-modal-last-update').text(data['last_update']);\r\n        $('#ultimate-job-modal-request-status').text(data['status']);\r\n        ultimateResultDataTable.clear();\r\n        ultimateResultDataTable.rows.add(data['result']);\r\n        ultimateResultDataTable.draw();\r\n\r\n        $('#ultimate-tag-modal-download-btn').click(function () {\r\n            download_req(data['requestId']);\r\n        });\r\n\r\n        $('#ultimate-tag-modal-cancel-btn').click(function () {\r\n            cancel_job(data['requestId']);\r\n        });\r\n\r\n    })\r\n});\r\n\r\nconst dataTableColumns = [\r\n    {\r\n        data: 'requestId',\r\n        render: function (data) {\r\n            return `<a class=\"modal-opener\" href=\"#\">${data}</a>`\r\n        }\r\n    }, {\r\n        data: 'request_time',\r\n        order: 'asc',\r\n        render: function (data) {\r\n            return `<div class=\"white-space-pre\">${data}</div>`\r\n        }\r\n    }, {\r\n        data: 'last_update',\r\n        render: function (data) {\r\n            return `<div class=\"white-space-pre\">${data}</div>`\r\n        }\r\n    }, {\r\n        data: 'status',\r\n        render: function (data) {\r\n            return `<div class=\"white-space-pre\">${data}</div>`\r\n        }\r\n    }, {\r\n        data: 'selected_requirements',\r\n        render: function (data) {\r\n            let result = ''\r\n            for (let name in data) {\r\n                let count = data[name]\r\n                if (display_req_without_formalisation !== \"True\" && count === 0) continue;\r\n                const searchQuery = `?command=search&col=2&q=%5C%22${name}%5C%22`\r\n                const color = count === 0 ? 'bg-light' : 'bg-info'\r\n                result += `<span class=\"badge ${color}\"><a href=\"${base_url}${searchQuery}\" target=\"_blank\" class=\"link-light text-muted\">${name} (${count})</a></span> `\r\n            }\r\n            return result;\r\n        }\r\n    }, {\r\n        data: 'result_requirements',\r\n        render: function (data) {\r\n            let result = ''\r\n            for (let name in data) {\r\n                let count = data[name]\r\n                const searchQuery = `?command=search&col=2&q=%5C%22${name}%5C%22`\r\n                const color = count === 0 ? 'bg-light' : 'bg-info'\r\n                result += `<span class=\"badge ${color}\"><a href=\"${base_url}${searchQuery}\" target=\"_blank\" class=\"link-light text-muted\">${name} (${count})</a></span> `\r\n            }\r\n            return result;\r\n        }\r\n    }\r\n]\r\n\r\nconst resultDataTableColumns = [\r\n    {\r\n        data: 'logLvl'\r\n    }, {\r\n        data: 'type'\r\n    }, {\r\n        data: 'shortDesc',\r\n        render: function (data) {\r\n            return `${data.replaceAll(\"\\n\", \"<br/>\")}`\r\n        }\r\n    }, {\r\n        data: 'longDesc',\r\n        render: function (data) {\r\n            return `${data.replaceAll(\"\\n\", \"<br/>\")}`\r\n        }\r\n    }\r\n]\r\n\r\nfunction update_search(string) {\r\n    sessionStorage.setItem('ultimateSearchString', string)\r\n    search_tree = SearchNode.fromQuery(string)\r\n}\r\n\r\nfunction evaluate_search(data) {\r\n    return search_tree.evaluate(data, [true, true, true])\r\n}\r\n\r\nfunction download_req(req_id) {\r\n    $.ajax({\r\n        type: 'GET',\r\n        url: 'api/v1/ultimate/jobs/' + req_id + '?download=true',\r\n    }).done(function (data) {\r\n        download(data['job_id'] + '.json', JSON.stringify(data, null, 4))\r\n        updateTableData()\r\n    }).fail(function (jqXHR, textStatus, errorThrown) {\r\n        alert(errorThrown + '\\n\\n' + jqXHR['responseText'])\r\n    })\r\n}\r\n\r\nfunction cancel_job(job_id) {\r\n    console.log(\"cancel\")\r\n    $.ajax({\r\n        type: 'POST',\r\n        url: 'api/v1/ultimate/jobs/' + job_id +'/abort',\r\n    }).done(function (data) {\r\n        updateTableData()\r\n    }).fail(function (jqXHR, textStatus, errorThrown) {\r\n        alert(errorThrown + '\\n\\n' + jqXHR['responseText'])\r\n    })\r\n}\r\n\r\nfunction download(filename, text) {\r\n    let element = document.createElement('a');\r\n    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));\r\n    element.setAttribute('download', filename);\r\n\r\n    element.style.display = 'none';\r\n    document.body.appendChild(element);\r\n\r\n    element.click();\r\n\r\n    document.body.removeChild(element);\r\n}\r\n\r\nfunction updateTableData() {\r\n    stoppReloadTimer()\r\n    $.ajax({\r\n        type: 'POST',\r\n        url: 'api/v1/ultimate/update-all'\r\n    }).done(function (data) {\r\n        if (data['status'] === 'done') {\r\n            const ultimateJobsTable = $('#ultimate-jobs-tbl')\r\n            ultimateJobsTable.DataTable().ajax.reload()\r\n        }\r\n        startReloadTimer()\r\n    }).fail(function (jqXHR, textStatus, errorThrown) {\r\n        alert(errorThrown + '\\n\\n' + jqXHR['responseText']);\r\n    })\r\n}\r\n\r\nfunction startReloadTimer(){\r\n    reload_timer = setTimeout(updateTableData, 60000)\r\n}\r\n\r\nfunction stoppReloadTimer() {\r\n    clearInterval(reload_timer)\r\n}\n\n//# sourceURL=webpack://hanfor/../ultimate/static/ultimate.js?");

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
/******/ 			"ultimate": 0
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
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, ["commons"], () => (__webpack_require__("../ultimate/static/ultimate.js")))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;