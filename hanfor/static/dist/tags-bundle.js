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

/***/ "../tags/static/tags.js":
/*!******************************!*\
  !*** ../tags/static/tags.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {

eval("/* provided dependency */ var $ = __webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\");\n__webpack_require__(/*! gasparesganga-jquery-loading-overlay */ \"./node_modules/gasparesganga-jquery-loading-overlay/src/loadingoverlay.js\")\n__webpack_require__(/*! bootstrap */ \"./node_modules/bootstrap/dist/js/bootstrap.esm.js\")\n__webpack_require__(/*! datatables.net-bs5 */ \"./node_modules/datatables.net-bs5/js/dataTables.bootstrap5.mjs\")\n__webpack_require__(/*! jquery-ui/ui/widgets/autocomplete */ \"./node_modules/jquery-ui/ui/widgets/autocomplete.js\")\n__webpack_require__(/*! jquery-ui/ui/effects/effect-highlight */ \"./node_modules/jquery-ui/ui/effects/effect-highlight.js\")\n__webpack_require__(/*! ../../static/js/bootstrap-tokenfield.js */ \"./js/bootstrap-tokenfield.js\")\n__webpack_require__(/*! awesomplete */ \"./node_modules/awesomplete/awesomplete.js\")\n__webpack_require__(/*! awesomplete/awesomplete.css */ \"./node_modules/awesomplete/awesomplete.css\")\n__webpack_require__(/*! datatables.net-colreorder-bs5 */ \"./node_modules/datatables.net-colreorder-bs5/js/colReorder.bootstrap5.mjs\")\n__webpack_require__(/*! ../../static/js/bootstrap-confirm-button */ \"./js/bootstrap-confirm-button.js\")\n\nconst autosize = __webpack_require__(/*! autosize/dist/autosize */ \"./node_modules/autosize/dist/autosize.js\")\nconst {SearchNode} = __webpack_require__(/*! ../../static/js/datatables-advanced-search.js */ \"./js/datatables-advanced-search.js\")\nconst {Modal} = __webpack_require__(/*! bootstrap */ \"./node_modules/bootstrap/dist/js/bootstrap.esm.js\")\n\nconst searchAutocomplete = [':AND:', ':OR:', ':NOT:', ':COL_INDEX_00:', ':COL_INDEX_01:', ':COL_INDEX_02:']\nconst tagsSearchString = sessionStorage.getItem('tagsSearchString')\n\n$(document).ajaxStart(function () {\n    $.LoadingOverlay('show')\n})\n\n$(document).ajaxStop(function () {\n    $.LoadingOverlay('hide')\n})\n\n$(document).ready(function () {\n    const searchInput = $('#search_bar')\n\n    const tagsTable = $('#tags-table')\n    const tagsDataTable = tagsTable.DataTable({\n        paging: true,\n        stateSave: true,\n        pageLength: 50,\n        responsive: true,\n        lengthMenu: [[10, 50, 100, 500, -1], [10, 50, 100, 500, 'All']],\n        dom: 'rt<\"container\"<\"row\"<\"col-md-6\"li><\"col-md-6\"p>>>',\n        ajax: {url: '../api/tags/', dataSrc: ''},\n        deferRender: true,\n        columns: dataTableColumns,\n        initComplete: function () {\n            searchInput.val(tagsSearchString)\n            update_search(searchInput.val().trim())\n\n            // Enable Hanfor specific table filtering.\n            $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {\n                // data contains the row. data[0] is the content of the first column in the actual row.\n                // Return true to include the row into the data. false to exclude.\n                return evaluate_search(data)\n            })\n            this.api().draw()\n        }\n    })\n\n    new $.fn.dataTable.ColReorder(tagsDataTable, {})\n\n    // Bind big custom searchbar to search the table.\n    searchInput.keypress(function (e) {\n        if (e.which === 13) { // Search on enter.\n            update_search(searchInput.val().trim())\n            tagsDataTable.draw()\n        }\n    })\n\n    new Awesomplete(searchInput[0], {\n        filter: function (text, input) {\n            let result = false\n            // If we have an uneven number of \":\"\n            // We check if we have a match in the input tail starting from the last \":\"\n            if ((input.split(':').length - 1) % 2 === 1) {\n                result = Awesomplete.FILTER_CONTAINS(text, input.match(/[^:]*$/)[0])\n            }\n            return result\n        }, item: function (text, input) {\n            // Match inside \":\" enclosed item.\n            return Awesomplete.ITEM(text, input.match(/(:)([\\S]*$)/)[2])\n        }, replace: function (text) {\n            // Cut of the tail starting from the last \":\" and replace by item text.\n            const before = this.input.value.match(/(.*)(:(?!.*:).*$)/)[1]\n            this.input.value = before + text\n        }, list: searchAutocomplete, minChars: 1, autoFirst: true\n    })\n\n    // Add listener for tag link to modal.\n    tagsTable.find('tbody').on('click', 'a.modal-opener', function (event) {\n        // prevent body to be scrolled to the top.\n        event.preventDefault()\n\n        // Get row data\n        let data = tagsDataTable.row($(event.target).parent()).data()\n        let row_id = tagsDataTable.row($(event.target).parent()).index()\n\n        Modal.getOrCreateInstance($('#tag-modal')).show()\n        $('#modal-associated-row-index').val(row_id)\n\n        // Meta information\n        $('#tag-name-old').val(data.name)\n        $('#occurences').val(data.used_by)\n\n        // Visible information\n        $('#tag-modal-title').html('Tag: ' + data.name)\n        $('#tag-name').val(data.name)\n        $('#tag-color').val(data.color)\n        $('#tag-description').val(data.description)\n        $('#tag-internal').prop('checked', data.internal)\n    })\n\n    // Store changes on tag on save.\n    $('#save-tag-modal').click(function () {\n        store_tag(tagsDataTable)\n    })\n\n    tagsDataTable.on('click', '.internal-checkbox', function (event) {\n        event.preventDefault()\n\n        let checkbox = event.currentTarget\n        let data = tagsDataTable.row(checkbox.parentNode).data()\n\n        $.ajax({\n            type: 'POST',\n            url: '../api/tags/update',\n            data: {\n                name: data.name,\n                name_old: data.name,\n                occurences: data.used_by,\n                color: data.color,\n                description: data.description,\n                internal: checkbox.checked\n            },\n            success: function (response) {\n                if (response['success'] === false) {\n                    alert(response['errormsg'])\n                    return\n                }\n\n                checkbox.checked = response.data.internal\n                data.internal = response.data.internal\n            }\n        })\n    })\n\n    $('.delete-tag').bootstrapConfirmButton({\n        onConfirm: function () {\n            deleteTag()\n        }\n    })\n\n    autosize($('#tag-description'))\n\n    $('#tag-modal').on('shown.bs.modal', function (e) {\n        autosize.update($('#tag-description'))\n    })\n\n    $('.clear-all-filters').click(function () {\n        searchInput.val('').effect('highlight', {color: 'green'}, 500)\n        update_search(searchInput.val().trim())\n        tagsDataTable.draw()\n    })\n\n    $('#add-standard-tags').click(function () {\n        $.ajax({\n            type: 'POST', url: '../api/tags/add_standard',\n        }).done(function (data) {\n            location.reload()\n        }).fail(function (jqXHR, textStatus, errorThrown) {\n            alert(errorThrown + '\\n\\n' + jqXHR['responseText'])\n        })\n    })\n})\n\n/**\n * Update the search expression tree.\n */\nfunction update_search(string) {\n    sessionStorage.setItem('tagsSearchString', string)\n    search_tree = SearchNode.fromQuery(string)\n}\n\n\nfunction evaluate_search(data) {\n    return search_tree.evaluate(data, [true, true, true])\n}\n\n\n/**\n * Store the currently active (in the modal) tag.\n * @param tagsDataTable\n */\nfunction store_tag(tagsDataTable) {\n    // Get data.\n    let name = $('#tag-name-old').val()\n    let nameNew = $('#tag-name').val()\n    let occurrences = $('#occurences').val().split(',')\n    let color = $('#tag-color').val()\n    let description = $('#tag-description').val()\n    let internal = $('#tag-internal').prop('checked')\n\n    $.ajax({\n        type: 'PATCH', url: `../api/tags/${name}`, contentType: 'application/json',\n        data: JSON.stringify({\n            name_new: nameNew,\n            occurrences: occurrences,\n            color: color,\n            description: description,\n            internal: internal\n        }),\n    }).done(function (data) {\n        location.reload()\n    }).fail(function (jqXHR, textStatus, errorThrown) {\n        alert(errorThrown + '\\n\\n' + jqXHR['responseText'])\n    })\n}\n\nfunction deleteTag() {\n    const tagName = $('#tag-name').val()\n    const occurrences = $('#occurences').val().split(',')\n\n    $.ajax({\n        type: 'DELETE', url: `../api/tags/${tagName}`, contentType: 'application/json',\n        data: JSON.stringify({\n            occurrences: occurrences\n        }),\n    }).done(function (data) {\n        location.reload()\n    }).fail(function (jqXHR, textStatus, errorThrown) {\n        alert(errorThrown + '\\n\\n' + jqXHR['responseText'])\n    })\n}\n\nconst dataTableColumns = [\n    {\n        data: 'name',\n        render: function (data, type, row, meta) {\n            return `<a class=\"modal-opener\" href=\"#\">${data}</a>`\n        }\n    }, {\n        data: 'description',\n        render: function (data, type, row, meta) {\n            return `<div class=\"white-space-pre\">${data}</div>`\n        }\n    }, {\n        data: 'used_by',\n        render: function (data, type, row, meta) {\n            let result = ''\n            $(data).each(function (id, name) {\n                if (name.length > 0) {\n                    const searchQuery = `?command=search&col=2&q=%5C%22${name}%5C%22`\n                    result += `<span class=\"badge bg-info\"><a href=\"${base_url}${searchQuery}\" target=\"_blank\" class=\"link-light\">${name}</a></span> `\n                }\n            })\n            if (data.length > 1 && result.length > 0) {\n                const searchQuery = `?command=search&col=5&q=%5C%22${row.name}%5C%22`\n                result += `<span class=\"badge bg-info\"><a href=\"${base_url}${searchQuery}\" target=\"_blank\" class=\"link-light\">Show all</a></span> `\n            }\n            return result\n        }\n    }, {\n        data: 'internal',\n        render: function (data, type, row, meta) {\n            return `<input class=\"form-check-input internal-checkbox\" type=\"checkbox\" ${data ? 'checked' : ''}>`\n        }\n    }, {\n        data: 'used_by',\n        visible: false,\n        searchable: false,\n        render: function (data, type, row, meta) {\n            return data.filter(e => e && e !== '').join(', ')\n        }\n    }\n]\n\n//# sourceURL=webpack://hanfor/../tags/static/tags.js?");

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
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, ["commons"], () => (__webpack_require__("../tags/static/tags.js")))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;