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

/***/ "../ultimate/static/ultimate-tab.js":
/*!******************************************!*\
  !*** ../ultimate/static/ultimate-tab.js ***!
  \******************************************/
/***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {

eval("/* provided dependency */ var $ = __webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\");\n$(document).ready(function () {\r\n    init_ultimate_tab()\r\n});\r\n\r\nfunction init_ultimate_tab() {\r\n    init_table_connection_functions.push(init_ultimate_requirements_table_connection)\r\n    check_ultimate_version();\r\n    update_configurations();\r\n\r\n    $('#ultimate-tab-create-unfiltered-btn').click(function () {\r\n        let btn = $('#ultimate-tab-create-unfiltered-btn')\r\n        create_ultimate_analysis(btn, \"all\");\r\n    });\r\n}\r\n\r\nfunction init_ultimate_requirements_table_connection (requirements_table) {\r\n    $('#ultimate-tab-create-filtered-btn').click(function () {\r\n        let req_ids = [];\r\n        requirements_table.rows({search: 'applied'}).every(function () {\r\n            let d = this.data();\r\n            req_ids.push(d['id']);\r\n        });\r\n\r\n        let btn = $('#ultimate-tab-create-filtered-btn')\r\n        create_ultimate_analysis(btn, req_ids);\r\n    });\r\n\r\n    $('#ultimate-tab-create-selected-btn').click(function () {\r\n        let req_ids = [];\r\n        requirements_table.rows({selected: true}).every(function () {\r\n            let d = this.data();\r\n            req_ids.push(d['id']);\r\n        });\r\n\r\n        let btn = $('#ultimate-tab-create-selected-btn')\r\n        create_ultimate_analysis(btn, req_ids);\r\n    });\r\n}\r\n\r\nfunction check_ultimate_version() {\r\n    $.ajax({\r\n        type: 'GET',\r\n        url: 'api/v1/ultimate/version'\r\n    }).done(function (data) {\r\n        if (data['version'] !== '') {\r\n            let img = $('#ultimate-tab-ultimate-status-img')\r\n            let img_src = img.attr(\"src\");\r\n            img.attr(\"src\", img_src.replace('/disconnected.svg', '/connected.svg'));\r\n            img.attr('title', 'Ultimate Api connected: ' + data['version'])\r\n            $('#ultimate-tab-create-unfiltered-btn').prop(\"disabled\",false);\r\n            $('#ultimate-tab-create-filtered-btn').prop(\"disabled\",false);\r\n            $('#ultimate-tab-create-selected-btn').prop(\"disabled\",false);\r\n        } else {\r\n            console.log('no ultimate connection found!');\r\n        }\r\n    }).fail(function (jqXHR, textStatus, errorThrown) {\r\n        alert(errorThrown + '\\n\\n' + jqXHR['responseText']);\r\n    });\r\n}\r\n\r\nfunction update_configurations() {\r\n    $.ajax({\r\n        type: 'GET',\r\n        url: 'api/v1/ultimate/configurations'\r\n    }).done(function (data) {\r\n        let select = $('#ultimate-tab-configuration-select');\r\n        select.empty();\r\n        let configurations = Object.keys(data);\r\n        for (let i = 0; i < configurations.length; i++) {\r\n            let displayed_name = configurations[i];\r\n            displayed_name += ' (Toolchain: ' + data[configurations[i]]['toolchain'];\r\n            displayed_name += ', User Settings: ' + data[configurations[i]]['user_settings'] + ')';\r\n            select.append($('<option></option>').val(configurations[i]).text(displayed_name));\r\n        }\r\n    }).fail(function (jqXHR, textStatus, errorThrown) {\r\n        alert(errorThrown + '\\n\\n' + jqXHR['responseText']);\r\n    });\r\n}\r\n\r\nfunction create_ultimate_analysis(btn, req_ids) {\r\n    let old_text = btn.text()\r\n    btn.text(\"Processing Request\")\r\n    let request_data = {'selected_requirement_ids': JSON.stringify(req_ids)}\r\n    if (req_ids === \"all\") {\r\n        request_data = {}\r\n    }\r\n    $.ajax({\r\n        type: 'POST',\r\n        url: 'api/tools/req_file',\r\n        data: request_data\r\n    }).done(function (data) {\r\n        let select = $('#ultimate-tab-configuration-select');\r\n        let configuration = select.val();\r\n        $.ajax({\r\n            type: 'POST',\r\n            url: 'api/v1/ultimate/jobs',\r\n            data: JSON.stringify({\"configuration\": configuration,\r\n                   \"req_file\": data,\r\n                   \"req_ids\": req_ids})\r\n        }).done(function (data) {\r\n            console.log(data['requestId'])\r\n            // TODO inform user about new analysis\r\n            btn.text(old_text);\r\n        }).fail(function (jqXHR, textStatus, errorThrown) {\r\n            alert(errorThrown + '\\n\\n' + jqXHR['responseText']);\r\n        })\r\n    }).fail(function (jqXHR, textStatus, errorThrown) {\r\n        alert(errorThrown + '\\n\\n' + jqXHR['responseText']);\r\n    });\r\n}\r\n\n\n//# sourceURL=webpack://hanfor/../ultimate/static/ultimate-tab.js?");

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
/******/ 			"ultimate_tab": 0
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
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, ["commons"], () => (__webpack_require__("../ultimate/static/ultimate-tab.js")))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;