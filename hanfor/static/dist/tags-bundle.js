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

eval("/* provided dependency */ var $ = __webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\");\n__webpack_require__(/*! gasparesganga-jquery-loading-overlay */ \"./node_modules/gasparesganga-jquery-loading-overlay/dist/loadingoverlay.min.js\")\r\nconst { Modal } = __webpack_require__(/*! bootstrap */ \"./node_modules/bootstrap/dist/js/bootstrap.esm.js\")\r\n__webpack_require__(/*! datatables.net-bs5 */ \"./node_modules/datatables.net-bs5/js/dataTables.bootstrap5.mjs\")\r\n__webpack_require__(/*! datatables.net-colreorder-bs5 */ \"./node_modules/datatables.net-colreorder-bs5/js/colReorder.bootstrap5.mjs\")\r\n__webpack_require__(/*! jquery-ui/ui/widgets/autocomplete */ \"./node_modules/jquery-ui/ui/widgets/autocomplete.js\")\r\n__webpack_require__(/*! ../../static/js/bootstrap-tokenfield.js */ \"./js/bootstrap-tokenfield.js\")\r\n__webpack_require__(/*! jquery-ui/ui/effects/effect-highlight */ \"./node_modules/jquery-ui/ui/effects/effect-highlight.js\")\r\n__webpack_require__(/*! awesomplete */ \"./node_modules/awesomplete/awesomplete.js\")\r\n__webpack_require__(/*! awesomplete/awesomplete.css */ \"./node_modules/awesomplete/awesomplete.css\")\r\n__webpack_require__(/*! ../../static/js/bootstrap-confirm-button */ \"./js/bootstrap-confirm-button.js\")\r\n\r\nconst autosize = __webpack_require__(/*! autosize/dist/autosize */ \"./node_modules/autosize/dist/autosize.js\")\r\nconst { SearchNode } = __webpack_require__(/*! ../../static/js/datatables-advanced-search.js */ \"./js/datatables-advanced-search.js\")\r\n\r\nconst { sendTelemetry } = __webpack_require__(/*! ../../telemetry/static/telemetry */ \"../telemetry/static/telemetry.js\")\r\n\r\nconst searchAutocomplete = [\":AND:\", \":OR:\", \":NOT:\", \":COL_INDEX_00:\", \":COL_INDEX_01:\", \":COL_INDEX_02:\"]\r\nconst tagsSearchString = sessionStorage.getItem(\"tagsSearchString\")\r\nlet search_tree = undefined\r\n\r\n$(document).ajaxStart(function () {\r\n  $.LoadingOverlay(\"show\")\r\n})\r\n\r\n$(document).ajaxStop(function () {\r\n  $.LoadingOverlay(\"hide\")\r\n})\r\n\r\n// init page\r\n$(function () {\r\n  initModal()\r\n  initDatatable()\r\n  initSearch()\r\n  initTabs()\r\n})\r\n\r\nfunction initModal() {\r\n  let modal = $(\"#tag-modal\")\r\n\r\n  modal[0].addEventListener(\"shown.bs.modal\", function () {\r\n    // resize tag-description text input on modal.show\r\n    autosize.update($(\"#tag-description\"))\r\n  })\r\n\r\n  modal[0].addEventListener(\"hide.bs.modal\", function (event) {\r\n    // catch unsaved changes on close\r\n    modalClosingRoutine(event)\r\n  })\r\n\r\n  $(\"#tag-name\").on(\"change\", function () {\r\n    $(\"#tag-modal\").data(\"unsavedChanges\", true)\r\n  })\r\n\r\n  $(\"#tag-color\").on(\"change\", function () {\r\n    $(\"#tag-modal\").data(\"unsavedChanges\", true)\r\n  })\r\n\r\n  $(\"#tag-internal\").on(\"change\", function () {\r\n    $(\"#tag-modal\").data(\"unsavedChanges\", true)\r\n  })\r\n\r\n  let tagDescr = $(\"#tag-description\")\r\n  tagDescr.on(\"change\", function () {\r\n    $(\"#tag-modal\").data(\"unsavedChanges\", true)\r\n  })\r\n  autosize(tagDescr)\r\n\r\n  $(\"#save-tag-modal\").on(\"click\", function () {\r\n    modalSaveTag()\r\n  })\r\n\r\n  $(\".delete-tag\").bootstrapConfirmButton({\r\n    onConfirm: function () {\r\n      modalDeleteTag()\r\n    },\r\n  })\r\n}\r\n\r\nfunction initDatatable() {\r\n  const tagsTable = $(\"#tags-table\")\r\n  const searchInput = $(\"#search_bar\")\r\n\r\n  // noinspection JSCheckFunctionSignatures\r\n  const tagsDataTable = tagsTable.DataTable({\r\n    paging: true,\r\n    stateSave: true,\r\n    pageLength: 50,\r\n    responsive: true,\r\n    lengthMenu: [\r\n      [10, 50, 100, 500, -1],\r\n      [10, 50, 100, 500, \"All\"],\r\n    ],\r\n    dom: 'rt<\"container\"<\"row\"<\"col-md-6\"li><\"col-md-6\"p>>>',\r\n    ajax: {\r\n      url: \"api/v1/tags\",\r\n      dataSrc: \"\",\r\n    },\r\n    deferRender: true,\r\n    colReorder: true,\r\n    columns: dataTableColumns,\r\n    initComplete: function () {\r\n      searchInput.val(tagsSearchString)\r\n      updateSearch((searchInput.val() || \"\").trim())\r\n\r\n      // Enable Hanfor specific table filtering.\r\n      $.fn.dataTable.ext.search.push(function (settings, data) {\r\n        // data contains the row. data[0] is the content of the first column in the actual row.\r\n        // Return true to include the row into the data. false to exclude.\r\n        return evaluateSearch(data)\r\n      })\r\n      this.api().draw()\r\n    },\r\n  })\r\n\r\n  // Add listener for tag link to modal.\r\n  tagsTable.find(\"tbody\").on(\"click\", \"a.modal-opener\", function (event) {\r\n    // prevent body to be scrolled to the top.\r\n    event.preventDefault()\r\n\r\n    // Get row data\r\n    const data = tagsDataTable.row($(event.target).parent().parent()).data()\r\n\r\n    const tagModal = $(\"#tag-modal\")\r\n    Modal.getOrCreateInstance(tagModal[0]).show()\r\n\r\n    // Add uuid to modal\r\n    $(\"#modal-uuid\").val(data[\"uuid\"])\r\n\r\n    // Visible information\r\n    $(\"#tag-modal-title\").html(\"Tag: \" + data.name)\r\n    let nameInput = $(\"#tag-name\")\r\n    nameInput.val(data.name)\r\n    nameInput.prop(\"disabled\", !data.mutable)\r\n    $(\"#tag-color\").val(data.color)\r\n    $(\"#tag-description\").val(data.description)\r\n    $(\"#tag-internal\").prop(\"checked\", data.internal)\r\n    const deleteBtn = $(\".delete-tag\")\r\n    deleteBtn.prop(\"disabled\", !data.mutable)\r\n    if (deleteBtn.data(\"html\")) {\r\n      deleteBtn.html(deleteBtn.data(\"html\")).removeData(\"html\")\r\n    }\r\n    tagModal.data(\"unsavedChanges\", false)\r\n    sendTelemetry(\"tag\", data[\"uuid\"], \"open\")\r\n  })\r\n\r\n  // Add listener to the internal checkbox\r\n  tagsDataTable.on(\"click\", \".internal-checkbox\", function (event) {\r\n    event.preventDefault()\r\n\r\n    const checkbox = event.currentTarget\r\n    const data = tagsDataTable.row(checkbox.parentNode).data()\r\n\r\n    $.ajax({\r\n      type: \"PATCH\",\r\n      contentType: \"application/json\",\r\n      url: `api/v1/tags/${data[\"uuid\"]}`,\r\n      data: JSON.stringify({\r\n        internal: checkbox.checked,\r\n      }),\r\n    })\r\n      .done(function () {\r\n        tagsDataTable.ajax.reload(null, false)\r\n      })\r\n      .fail(function (jqXHR, textStatus, errorThrown) {\r\n        alert(errorThrown + \"\\n\\n\" + jqXHR[\"responseText\"])\r\n      })\r\n  })\r\n}\r\n\r\nfunction initSearch() {\r\n  const tagsDataTable = $(\"#tags-table\").DataTable()\r\n  const searchInput = $(\"#search_bar\")\r\n\r\n  // Bind big custom searchbar to search the table.\r\n  searchInput.on(\"keydown\", function (e) {\r\n    if (e.which === 13) {\r\n      // Search on enter.\r\n      updateSearch((searchInput.val() || \"\").trim())\r\n      tagsDataTable.draw()\r\n    }\r\n  })\r\n\r\n  new Awesomplete(searchInput[0], {\r\n    filter: function (text, input) {\r\n      let result = false\r\n      // If we have an uneven number of \":\"\r\n      // We check if we have a match in the input tail starting from the last \":\"\r\n      if ((input.split(\":\").length - 1) % 2 === 1) {\r\n        result = Awesomplete.FILTER_CONTAINS(text, input.match(/[^:]*$/)[0])\r\n      }\r\n      return result\r\n    },\r\n    item: function (text, input) {\r\n      // Match inside \":\" enclosed item.\r\n      return Awesomplete.ITEM(text, input.match(/(:)(\\S*$)/)[2])\r\n    },\r\n    replace: function (text) {\r\n      // Cut of the tail starting from the last \":\" and replace by item text.\r\n      const before = this.input.value.match(/(.*)(:(?!.*:).*$)/)[1]\r\n      this.input.value = before + text\r\n    },\r\n    list: searchAutocomplete,\r\n    minChars: 1,\r\n    autoFirst: true,\r\n  })\r\n\r\n  $(\".clear-all-filters\").on(\"click\", function () {\r\n    searchInput.val(\"\").effect(\"highlight\", { color: \"green\" }, 500)\r\n    updateSearch((searchInput.val() || \"\").trim())\r\n    tagsDataTable.draw()\r\n  })\r\n}\r\n\r\nfunction initTabs() {\r\n  $(\"#add-standard-tags\").on(\"click\", function () {\r\n    $.ajax({\r\n      type: \"POST\",\r\n      url: \"api/v1/tags/add_standard\",\r\n    })\r\n      .done(function () {\r\n        location.reload()\r\n      })\r\n      .fail(function (jqXHR, textStatus, errorThrown) {\r\n        alert(errorThrown + \"\\n\\n\" + jqXHR[\"responseText\"])\r\n      })\r\n  })\r\n}\r\n\r\nfunction modalClosingRoutine(event) {\r\n  const unsavedChanges = $(\"#tag-modal\").data(\"unsavedChanges\")\r\n  const uuid = $(\"#modal-uuid\").val()\r\n  if (unsavedChanges === true) {\r\n    const forceClose = confirm(\"You have unsaved changes, do you really want to close?\")\r\n    if (forceClose !== true) {\r\n      event.preventDefault()\r\n    } else {\r\n      sendTelemetry(\"tag\", uuid, \"close_without_save\")\r\n    }\r\n  } else {\r\n    sendTelemetry(\"tag\", uuid, \"close\")\r\n  }\r\n}\r\n\r\n/**\r\n * Update the search expression tree.\r\n */\r\nfunction updateSearch(string) {\r\n  sessionStorage.setItem(\"tagsSearchString\", string)\r\n  search_tree = SearchNode.fromQuery(string)\r\n}\r\n\r\nfunction evaluateSearch(data) {\r\n  return search_tree.evaluate(data, [true, true, true])\r\n}\r\n\r\nfunction modalSaveTag() {\r\n  // Get data.\r\n  let uuid = $(\"#modal-uuid\").val()\r\n  let name = $(\"#tag-name\").val()\r\n  let color = $(\"#tag-color\").val()\r\n  let description = $(\"#tag-description\").val()\r\n  let internal = $(\"#tag-internal\").prop(\"checked\")\r\n\r\n  sendTelemetry(\"tag\", uuid, \"save\")\r\n\r\n  $.ajax({\r\n    type: \"PUT\",\r\n    url: `api/v1/tags/${uuid}`,\r\n    contentType: \"application/json\",\r\n    data: JSON.stringify({\r\n      name: name,\r\n      color: color,\r\n      description: description,\r\n      internal: internal,\r\n    }),\r\n  })\r\n    .done(function () {\r\n      let modal = $(\"#tag-modal\")\r\n      modal.data(\"unsavedChanges\", false)\r\n      $(\"#tags-table\").DataTable().ajax.reload(null, false)\r\n      Modal.getOrCreateInstance(modal).hide()\r\n    })\r\n    .fail(function (jqXHR, textStatus, errorThrown) {\r\n      alert(errorThrown + \"\\n\\n\" + jqXHR[\"responseText\"])\r\n    })\r\n}\r\n\r\nfunction modalDeleteTag() {\r\n  const uuid = $(\"#modal-uuid\").val()\r\n  sendTelemetry(\"tag\", uuid, \"delete\")\r\n\r\n  $.ajax({\r\n    type: \"DELETE\",\r\n    url: `api/v1/tags/${uuid}`,\r\n  })\r\n    .done(function () {\r\n      let modal = $(\"#tag-modal\")\r\n      modal.data(\"unsavedChanges\", false)\r\n      $(\"#tags-table\").DataTable().ajax.reload(null, false)\r\n      Modal.getOrCreateInstance(modal).hide()\r\n    })\r\n    .fail(function (jqXHR, textStatus, errorThrown) {\r\n      alert(errorThrown + \"\\n\\n\" + jqXHR[\"responseText\"])\r\n    })\r\n}\r\n\r\nconst dataTableColumns = [\r\n  {\r\n    data: \"name\",\r\n    render: function (data, type, row) {\r\n      return `<a class=\"modal-opener\" href=\"#\"><span class=\"badge\" style=\"background-color: ${row.color}\" >${data}</span></a>`\r\n    },\r\n  },\r\n  {\r\n    data: \"description\",\r\n    render: function (data) {\r\n      return `<div class=\"white-space-pre\">${data}</div>`\r\n    },\r\n  },\r\n  {\r\n    data: \"used_by\",\r\n    render: function (data, type, row) {\r\n      let result = \"\"\r\n      $(data).each(function (id, name) {\r\n        if (name.length > 0) {\r\n          const searchQuery = `?command=search&col=2&q=%5C%22${name}%5C%22`\r\n          result += `<span class=\"badge bg-info\"><a href=\"${base_url}${searchQuery}\" target=\"_blank\" class=\"link-light\">${name}</a></span> `\r\n        }\r\n      })\r\n      if (data.length > 1 && result.length > 0) {\r\n        const searchQuery = `?command=search&col=5&q=%5C%22${row.name}%5C%22`\r\n        result += `<span class=\"badge bg-info\"><a href=\"${base_url}${searchQuery}\" target=\"_blank\" class=\"link-light\">Show all</a></span> `\r\n      }\r\n      return result\r\n    },\r\n  },\r\n  {\r\n    data: \"internal\",\r\n    render: function (data) {\r\n      return `<input class=\"form-check-input internal-checkbox\" type=\"checkbox\" ${data ? \"checked\" : \"\"}>`\r\n    },\r\n  },\r\n  {\r\n    data: \"used_by\",\r\n    visible: false,\r\n    searchable: false,\r\n    render: function (data) {\r\n      return data.filter((e) => e && e !== \"\").join(\", \")\r\n    },\r\n  },\r\n]\r\n\n\n//# sourceURL=webpack://hanfor/../tags/static/tags.js?");

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