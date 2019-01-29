!function(e){function t(t){for(var r,i,s=t[0],l=t[1],c=t[2],d=0,f=[];d<s.length;d++)i=s[d],a[i]&&f.push(a[i][0]),a[i]=0;for(r in l)Object.prototype.hasOwnProperty.call(l,r)&&(e[r]=l[r]);for(u&&u(t);f.length;)f.shift()();return o.push.apply(o,c||[]),n()}function n(){for(var e,t=0;t<o.length;t++){for(var n=o[t],r=!0,s=1;s<n.length;s++){var l=n[s];0!==a[l]&&(r=!1)}r&&(o.splice(t--,1),e=i(i.s=n[0]))}return e}var r={},a={5:0},o=[];function i(t){if(r[t])return r[t].exports;var n=r[t]={i:t,l:!1,exports:{}};return e[t].call(n.exports,n,n.exports,i),n.l=!0,n.exports}i.m=e,i.c=r,i.d=function(e,t,n){i.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:n})},i.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},i.t=function(e,t){if(1&t&&(e=i(e)),8&t)return e;if(4&t&&"object"==typeof e&&e&&e.__esModule)return e;var n=Object.create(null);if(i.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var r in e)i.d(n,r,function(t){return e[t]}.bind(null,r));return n},i.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return i.d(t,"a",t),t},i.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},i.p="";var s=window.webpackJsonp=window.webpackJsonp||[],l=s.push.bind(s);s.push=t,s=s.slice();for(var c=0;c<s.length;c++)t(s[c]);var u=l;o.push([224,0]),n()}({217:function(e,t){const n={":AND:":1,":OR:":1},r={":AND:":1,":OR:":1},a={},o={"(":1,")":1},i={":AND:":3,":OR:":2};class s{constructor(e){this.left=!1,this.value=e,this.right=!1,this.col_target=-1,this.update_target()}update_target(){const e=this.value.indexOf(":COL_INDEX_");if(e>=0){const t=parseInt(this.value.substring(e+11,e+13));t>=0&&(this.value=this.value.substring(e+14),this.col_target=t)}}evaluate(e,t){return function e(t,n,r){if(void 0===t)return!0;if(!1===t.left&&!1===t.right){let e="";if(-1!==t.col_target)e=n[t.col_target];else for(let t=0;t<r.length;t++)r[t]&&(e+=n[t]+" ");const a=t.value.indexOf(":NOT:");return a>=0?!l(t.value.substring(a+5),e):l(t.value,e)}let a=e(t.left,n,r);let o=e(t.right,n,r);if(":AND:"===t.value)return a&&o;if(":OR:"===t.value)return a||o}(this,e,t)}static is_search_string(e){return!(e in o||e in n)}static to_string(e){let t="";return!1!==e.left&&(t+=s.to_string(e.left)+" "),t+=e.value,!1!==e.right&&(t+=" "+s.to_string(e.right)),t}static peek(e){return e[e.length-1]}static searchArrayToTree(e){let t=[],o=[];for(let l=0,c=e.length;l<c;l++){const c=e[l];if(s.is_search_string(c))t.push(new s(c));else if(c in n){for(;o.length;){const e=s.peek(o);if(!(e in n&&(c in r&&i[c]<=i[e]||c in a&&i[c]<i[e])))break;{let e=t.pop(),n=t.pop(),r=new s(o.pop());r.left=n,r.right=e,t.push(r)}}o.push(c)}else if("("===c)o.push(c);else{if(")"!==c)throw"Error: Token unknown: "+c;{let e=!1;for(;o.length;){const n=o.pop();if("("===n){e=!0;break}{let e=t.pop(),r=t.pop(),a=new s(n);a.left=r,a.right=e,t.push(a)}}if(!e)throw"Error: parentheses mismatch."}}}for(;o.length;){const e=o.pop();if("("===e||")"===e)throw"Error: Parentheses mismatch.";let n=t.pop(),r=t.pop(),a=new s(e);a.left=r,a.right=n,t.push(a)}return 0===t.length&&t.push(new s("")),t[0]}static awesomeQuerySplitt0r(e,t){let r=e.split(/(:OR:|:AND:|\(|\))/g);if(r=r.filter(String),void 0!==t)for(let e=0,a=r.length;e<a;e++)r[e]in n||r[e]in o||(r[e]=":COL_INDEX_"+("00"+t).slice(-2)+":"+r[e]);return r}static fromQuery(e="",t){return s.searchArrayToTree(s.awesomeQuerySplitt0r(e,t))}}function l(e,t){return e=e.startsWith('""')&&e.endsWith('""')?"^\\s*"+e.substr(2,e.length-4)+"\\s*$":e.replace(/([^\\])?\"/g,"$1\\b"),new RegExp(e,"i").test(t)}e.exports={SearchNode:s}},218:function(e,t,n){var r,a,o;
/*!
	autosize 4.0.2
	license: MIT
	http://www.jacklmoore.com/autosize
*/a=[e,t],void 0===(o="function"==typeof(r=function(e,t){"use strict";var n,r,a="function"==typeof Map?new Map:(n=[],r=[],{has:function(e){return n.indexOf(e)>-1},get:function(e){return r[n.indexOf(e)]},set:function(e,t){-1===n.indexOf(e)&&(n.push(e),r.push(t))},delete:function(e){var t=n.indexOf(e);t>-1&&(n.splice(t,1),r.splice(t,1))}}),o=function(e){return new Event(e,{bubbles:!0})};try{new Event("test")}catch(e){o=function(e){var t=document.createEvent("Event");return t.initEvent(e,!0,!1),t}}function i(e){if(e&&e.nodeName&&"TEXTAREA"===e.nodeName&&!a.has(e)){var t=null,n=null,r=null,i=function(){e.clientWidth!==n&&d()},s=function(t){window.removeEventListener("resize",i,!1),e.removeEventListener("input",d,!1),e.removeEventListener("keyup",d,!1),e.removeEventListener("autosize:destroy",s,!1),e.removeEventListener("autosize:update",d,!1),Object.keys(t).forEach(function(n){e.style[n]=t[n]}),a.delete(e)}.bind(e,{height:e.style.height,resize:e.style.resize,overflowY:e.style.overflowY,overflowX:e.style.overflowX,wordWrap:e.style.wordWrap});e.addEventListener("autosize:destroy",s,!1),"onpropertychange"in e&&"oninput"in e&&e.addEventListener("keyup",d,!1),window.addEventListener("resize",i,!1),e.addEventListener("input",d,!1),e.addEventListener("autosize:update",d,!1),e.style.overflowX="hidden",e.style.wordWrap="break-word",a.set(e,{destroy:s,update:d}),"vertical"===(l=window.getComputedStyle(e,null)).resize?e.style.resize="none":"both"===l.resize&&(e.style.resize="horizontal"),t="content-box"===l.boxSizing?-(parseFloat(l.paddingTop)+parseFloat(l.paddingBottom)):parseFloat(l.borderTopWidth)+parseFloat(l.borderBottomWidth),isNaN(t)&&(t=0),d()}var l;function c(t){var n=e.style.width;e.style.width="0px",e.offsetWidth,e.style.width=n,e.style.overflowY=t}function u(){if(0!==e.scrollHeight){var r=function(e){for(var t=[];e&&e.parentNode&&e.parentNode instanceof Element;)e.parentNode.scrollTop&&t.push({node:e.parentNode,scrollTop:e.parentNode.scrollTop}),e=e.parentNode;return t}(e),a=document.documentElement&&document.documentElement.scrollTop;e.style.height="",e.style.height=e.scrollHeight+t+"px",n=e.clientWidth,r.forEach(function(e){e.node.scrollTop=e.scrollTop}),a&&(document.documentElement.scrollTop=a)}}function d(){u();var t=Math.round(parseFloat(e.style.height)),n=window.getComputedStyle(e,null),a="content-box"===n.boxSizing?Math.round(parseFloat(n.height)):e.offsetHeight;if(a<t?"hidden"===n.overflowY&&(c("scroll"),u(),a="content-box"===n.boxSizing?Math.round(parseFloat(window.getComputedStyle(e,null).height)):e.offsetHeight):"hidden"!==n.overflowY&&(c("hidden"),u(),a="content-box"===n.boxSizing?Math.round(parseFloat(window.getComputedStyle(e,null).height)):e.offsetHeight),r!==a){r=a;var i=o("autosize:resized");try{e.dispatchEvent(i)}catch(e){}}}}function s(e){var t=a.get(e);t&&t.destroy()}function l(e){var t=a.get(e);t&&t.update()}var c=null;"undefined"==typeof window||"function"!=typeof window.getComputedStyle?((c=function(e){return e}).destroy=function(e){return e},c.update=function(e){return e}):((c=function(e,t){return e&&Array.prototype.forEach.call(e.length?e:[e],function(e){return i(e)}),e}).destroy=function(e){return e&&Array.prototype.forEach.call(e.length?e:[e],s),e},c.update=function(e){return e&&Array.prototype.forEach.call(e.length?e:[e],l),e}),t.default=c,e.exports=t.default})?r.apply(t,a):r)||(e.exports=o)},219:function(e,t,n){var r,a;
/*!
 * JavaScript Cookie v2.2.0
 * https://github.com/js-cookie/js-cookie
 *
 * Copyright 2006, 2015 Klaus Hartl & Fagner Brack
 * Released under the MIT license
 */!function(o){if(void 0===(a="function"==typeof(r=o)?r.call(t,n,t,e):r)||(e.exports=a),!0,e.exports=o(),!!0){var i=window.Cookies,s=window.Cookies=o();s.noConflict=function(){return window.Cookies=i,s}}}(function(){function e(){for(var e=0,t={};e<arguments.length;e++){var n=arguments[e];for(var r in n)t[r]=n[r]}return t}return function t(n){function r(t,a,o){var i;if("undefined"!=typeof document){if(arguments.length>1){if("number"==typeof(o=e({path:"/"},r.defaults,o)).expires){var s=new Date;s.setMilliseconds(s.getMilliseconds()+864e5*o.expires),o.expires=s}o.expires=o.expires?o.expires.toUTCString():"";try{i=JSON.stringify(a),/^[\{\[]/.test(i)&&(a=i)}catch(e){}a=n.write?n.write(a,t):encodeURIComponent(String(a)).replace(/%(23|24|26|2B|3A|3C|3E|3D|2F|3F|40|5B|5D|5E|60|7B|7D|7C)/g,decodeURIComponent),t=(t=(t=encodeURIComponent(String(t))).replace(/%(23|24|26|2B|5E|60|7C)/g,decodeURIComponent)).replace(/[\(\)]/g,escape);var l="";for(var c in o)o[c]&&(l+="; "+c,!0!==o[c]&&(l+="="+o[c]));return document.cookie=t+"="+a+l}t||(i={});for(var u=document.cookie?document.cookie.split("; "):[],d=/(%[0-9A-Z]{2})+/g,f=0;f<u.length;f++){var p=u[f].split("="),h=p.slice(1).join("=");this.json||'"'!==h.charAt(0)||(h=h.slice(1,-1));try{var g=p[0].replace(d,decodeURIComponent);if(h=n.read?n.read(h,g):n(h,g)||h.replace(d,decodeURIComponent),this.json)try{h=JSON.parse(h)}catch(e){}if(t===g){i=h;break}t||(i[g]=h)}catch(e){}}return i}}return r.set=r,r.get=function(e){return r.call(r,e)},r.getJSON=function(){return r.apply({json:!0},[].slice.call(arguments))},r.defaults={},r.remove=function(t,n){r(t,"",e(n,{expires:-1}))},r.withConverter=t,r}(function(){})})},224:function(e,t,n){(function(e){n(17),n(10),n(15),n(14),n(20),n(13),n(149),n(12);n(219);const t=n(218),{SearchNode:r}=n(217);let a=n(157),{Textcomplete:o,Textarea:i}=n(156),s=new a([],{}),l=["","has_formalization"],c=["","Todo","Review","Done"],u=[""],d=[""],f=[],p=[""],h=[!0,!0,!0,!0,!0,!0],g=[],m=JSON.parse(search_query),_={},v=[],y=sessionStorage.getItem("req_search_string"),b=sessionStorage.getItem("filter_status_string"),w=sessionStorage.getItem("filter_tag_string"),q=sessionStorage.getItem("filter_type_string"),x=void 0,k=void 0;function O(){y=e("#search_bar").val().trim(),sessionStorage.setItem("req_search_string",y),x=r.fromQuery(y)}function z(){function t(e,t,n){return t.length>0&&(e.length>0&&(e=e.concat([":AND:"])),e=e.concat(function(e){return["("].concat(e,[")"])}(r.awesomeQuerySplitt0r(t,n)))),e}g=[],b=e("#status-filter-input").val(),w=e("#tag-filter-input").val(),q=e("#type-filter-input").val(),sessionStorage.setItem("filter_status_string",b),sessionStorage.setItem("filter_tag_string",w),sessionStorage.setItem("filter_type_string",q),g=t(g=t(g=t(g,q,4),w,5),b,6),k=r.searchArrayToTree(g)}function C(e){let t=[];return e.rows({selected:!0}).every(function(){let e=this.data();t.push(e.id)}),t}function E(){e(".requirement_var_group").each(function(){e(this).hide(),e(this).removeClass("type-error")}),e(".formalization_card").each(function(t){const n=e(this).attr("title"),r=e("#requirement_scope"+n).val(),a=e("#requirement_pattern"+n).val();let o=e("#formalization_heading"+n),i=e("#requirement_var_group_p"+n),s=e("#requirement_var_group_q"+n),l=e("#requirement_var_group_r"+n),c=e("#requirement_var_group_s"+n),u=e("#requirement_var_group_t"+n),d=e("#requirement_var_group_u"+n);if(n in v)for(let t=0;t<v[n].length;t++)e("#formalization_var_"+v[n][t]+n).addClass("type-error"),o.addClass("type-error-head");else o.removeClass("type-error-head");switch(r){case"BEFORE":case"AFTER":i.show();break;case"BETWEEN":case"AFTER_UNTIL":i.show(),s.show()}switch(a){case"Absence":case"Universality":case"Existence":case"BoundedExistence":l.show();break;case"Invariant":case"Precedence":case"Response":case"MinDuration":case"MaxDuration":case"BoundedRecurrence":l.show(),c.show();break;case"PrecedenceChain1-2":case"PrecedenceChain2-1":case"ResponseChain1-2":case"ResponseChain2-1":case"BoundedResponse":case"BoundedInvariance":case"TimeConstrainedInvariant":l.show(),c.show(),u.show();break;case"ConstrainedChain":case"TimeConstrainedMinDuration":case"ConstrainedTimedExistence":l.show(),c.show(),u.show(),d.show();break;case"NotFormalizable":i.hide(),s.hide()}})}function S(){e(".formalization_card").each(function(n){const r=e(this).attr("title");let a="",o=e("#current_formalization_textarea"+r);const i=e("#requirement_scope"+r).find("option:selected").text().replace(/\s\s+/g," "),s=e("#requirement_pattern"+r).find("option:selected").text().replace(/\s\s+/g," ");"None"!==i&&"None"!==s&&(a=i+", "+s+".");let l=e("#formalization_var_p"+r).val(),c=e("#formalization_var_q"+r).val(),u=e("#formalization_var_r"+r).val(),d=e("#formalization_var_s"+r).val(),f=e("#formalization_var_t"+r).val(),p=e("#formalization_var_u"+r).val();l.length>0&&(a=a.replace(/{P}/g,l)),c.length>0&&(a=a.replace(/{Q}/g,c)),u.length>0&&(a=a.replace(/{R}/g,u)),d.length>0&&(a=a.replace(/{S}/g,d)),f.length>0&&(a=a.replace(/{T}/g,f)),p.length>0&&(a=a.replace(/{U}/g,p)),o.val(a),t.update(o)}),e("#requirement_modal").data({unsaved_changes:!0,updated_formalization:!0})}function L(){e(".formalization_selector").change(function(){E(),S()}),e(".reqirement-variable, .req_var_type").change(function(){S()}),e(".delete_formalization").confirmation({rootSelector:".delete_formalization"}).click(function(){!function(t){let n=e(".modal-content");n.LoadingOverlay("show");const r=e("#requirement_id").val();e.post("api/req/del_formalization",{requirement_id:r,formalization_id:t},function(t){n.LoadingOverlay("hide",!0),!1===t.success?alert(t.errormsg):e("#formalization_accordion").html(t.html)}).done(function(){E(),S(),L(),T(),P()})}(e(this).attr("name"))})}function T(){e(".reqirement-variable").each(function(t){let n=new i(this),r=new o(n,{dropdown:{maxCount:10}});r.register([{match:/(^|\s|[!=&\|>]+)(\w+)$/,search:function(e,t){include_elems=function(e){return s.search(e)}(e),result=[];for(let e=0;e<Math.min(10,include_elems.length);e++)result.push(d[include_elems[e]]);t(result)},replace:function(e){return"$1"+e+" "}}]),e(this).on("blur click",function(e){r.dropdown.deactivate(),e.preventDefault()})})}function N(n){if(-1===n)return void alert("Requirement not found.");let r=e("#requirements_table").DataTable().row(n).data(),o=e(".modal-content");e("#requirement_modal").modal("show"),o.LoadingOverlay("show"),e("#formalization_accordion").html(""),e("#requirement_tag_field").data("bs.tokenfield").$input.autocomplete({source:l}),e.get("api/req/get",{id:r.id,row_idx:n},function(t){if(!1===t.success)return void alert("Could Not load the Requirement: "+t.errormsg);e("#requirement_id").val(t.id),e("#modal_associated_row_index").val(n),d=t.available_vars,v=t.type_inference_errors,s=new a(d,{shouldSort:!0,threshold:.6,location:0,distance:100,maxPatternLength:12,minMatchCharLength:1,keys:void 0}),e("#requirement_modal_title").html(t.id+": "+t.type),e("#description_textarea").text(t.desc),e("#add_guess_description").text(t.desc),e("#formalization_accordion").html(t.formalizations_html),e("#requirement_scope").val(t.scope),e("#requirement_pattern").val(t.pattern),e("#requirement_tag_field").tokenfield("setTokens",t.tags),e("#requirement_status").val(t.status);let r=e("#csv_content_accordion");r.html(""),r.collapse("hide");let o=t.csv_data;for(const e in o)if(o.hasOwnProperty(e)){const t=o[e];r.append("<p><strong>"+e+":</strong>"+t+"</p>")}let i=e("#show_revision_diff");e.isEmptyObject(t.revision_diff)?i.hide():i.show();let l=e("#revision_diff_accordion");l.html(""),l.collapse("hide");let c=t.revision_diff;for(const e in c)if(c.hasOwnProperty(e)){const t=c[e];l.append("<p><strong>"+e+":</strong><pre>"+t+"</pre></p>")}}).done(function(){E(),T(),L(),e("#requirement_tag_field").on("tokenfield:createtoken",function(t){let n=e(this).tokenfield("getTokens");e.each(n,function(e,n){n.value===t.attrs.value&&t.preventDefault()})}),e("#requirement_modal").data({unsaved_changes:!1,updated_formalization:!1}),e("textarea").each(function(){t(e(this)),t.update(e(this))}),o.LoadingOverlay("hide",!0)})}function D(){let t=e("#requirements_table").DataTable(),n=[];e.each(t.columns().visible(),function(t,r){!1===r?(e("#col_toggle_button_"+t).removeClass("btn-info").addClass("btn-secondary"),n.push(!1)):(e("#col_toggle_button_"+t).removeClass("btn-secondary").addClass("btn-info"),n.push(!0))}),h=n}function R(t){t.columns().every(function(e){e>0&&t.column(e).header().append(" ("+e+")")}),e("#save_requirement_modal").click(function(){!function(t){let n=e(".modal-content");n.LoadingOverlay("show");const r=e("#requirement_id").val(),a=e("#requirement_tag_field").val(),o=e("#requirement_status").val(),i=e("#requirement_modal").data("updated_formalization"),s=parseInt(e("#modal_associated_row_index").val());let l={};e(".formalization_card").each(function(t){let n={};n.id=e(this).attr("title"),e(this).find("select").each(function(){e(this).hasClass("scope_selector")&&(n.scope=e(this).val()),e(this).hasClass("pattern_selector")&&(n.pattern=e(this).val())}),n.expression_mapping={},e(this).find("textarea.reqirement-variable").each(function(){""!==e(this).attr("title")&&(n.expression_mapping[e(this).attr("title")]=e(this).val())}),l[n.id]=n}),e.post("api/req/update",{id:r,row_idx:s,update_formalization:i,tags:a,status:o,formalizations:JSON.stringify(l)},function(r){n.LoadingOverlay("hide",!0),!1===r.success?alert(r.errormsg):(t.row(s).data(r),e("#requirement_modal").data("unsaved_changes",!1).modal("hide"))}).done(function(){P()})}(t)}),e("#search_bar").keypress(function(e){13===e.which&&(O(),t.draw())}),e("#type-filter-input").autocomplete({minLength:0,source:u,delay:100}),e("#status-filter-input").autocomplete({minLength:0,source:c,delay:100}),e("#tag-filter-input").autocomplete({minLength:0,source:l,delay:100}),e("#tag-filter-input, #status-filter-input, #type-filter-input").on("focus",function(){e(this).keydown()}).on("keypress",function(e){13===e.which&&(z(),t.draw())}),e("#table-filter-toggle").click(function(){e("#tag-filter-input").autocomplete({source:l}),e("#type-filter-input").autocomplete({source:u})}),e(".clear-all-filters").click(function(){e("#status-filter-input").val("").effect("highlight",{color:"green"},500),e("#tag-filter-input").val("").effect("highlight",{color:"green"},500),e("#type-filter-input").val("").effect("highlight",{color:"green"},500),e("#search_bar").val("").effect("highlight",{color:"green"},500),z(),O(),t.draw()}),e("#gen-req-from-selection").click(function(){let n=[];t.rows({search:"applied"}).every(function(){let e=this.data();n.push(e.id)}),e("#selected_requirement_ids").val(JSON.stringify(n)),e("#generate_req_form").submit()}),e("#gen-csv-from-selection").click(function(){let n=[];t.rows({search:"applied"}).every(function(){let e=this.data();n.push(e.id)}),e("#selected_csv_requirement_ids").val(JSON.stringify(n)),e("#generate_csv_form").submit()}),e(".colum-toggle-button").on("click",function(n){n.preventDefault();let r=t.column(e(this).attr("data-column"));r.visible(!r.visible()),D()}),e(".reset-colum-toggle").on("click",function(e){e.preventDefault(),t.columns(".default-col").visible(!0),t.columns(".extra-col").visible(!1),D()}),D(),e(".select-all-button").on("click",function(n){e(this).hasClass("btn-secondary")?t.rows({page:"current"}).select():t.rows({page:"current"}).deselect(),e(".select-all-button").toggleClass("btn-secondary btn-primary")}),t.on("user-select",function(){let t=e(".select-all-button");t.removeClass("btn-primary"),t.addClass("btn-secondary ")}),e("#multi-add-tag-input, #multi-remove-tag-input").autocomplete({minLength:0,source:l,delay:100}).on("focus",function(){e(this).keydown()}).val(""),e("#multi-set-status-input").autocomplete({minLength:0,source:c,delay:100}).on("focus",function(){e(this).keydown()}).val(""),e(".apply-multi-edit").click(function(){!function(t){let n=e("body");n.LoadingOverlay("show");let r=e("#multi-add-tag-input").val().trim(),a=e("#multi-remove-tag-input").val().trim(),o=e("#multi-set-status-input").val().trim(),i=C(t);e.post("api/req/multi_update",{add_tag:r,remove_tag:a,set_status:o,selected_ids:JSON.stringify(i)},function(e){n.LoadingOverlay("hide",!0),!1===e.success?alert(e.errormsg):location.reload()})}(t)}),e(".add_top_guess_button").confirmation({rootSelector:".add_top_guess_button"}).click(function(){!function(t){let n=e("body");n.LoadingOverlay("show");let r=C(t),a=e("#top_guess_append_mode").val();e.post("api/req/multi_add_top_guess",{selected_ids:JSON.stringify(r),insert_mode:a},function(e){n.LoadingOverlay("hide",!0),!1===e.success?alert(e.errormsg):location.reload()})}(t)})}function I(t){let n=e("#requirements_table").DataTable({language:{emptyTable:"Loading data."},paging:!0,stateSave:!0,select:{style:"os",selector:"td:first-child"},pageLength:50,lengthMenu:[[10,50,100,500,-1],[10,50,100,500,"All"]],dom:'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',ajax:"api/req/gets",deferRender:!0,columnDefs:t,createdRow:function(t,n,r){"Heading"===n.type&&e(t).addClass("bg-primary"),"Information"===n.type&&e(t).addClass("table-info"),"Requirement"===n.type&&e(t).addClass("table-warning"),"not set"===n.type&&e(t).addClass("table-light")},infoCallback:function(t,n,r,a,o,i){var s=this.api().page.info();e("#clear-all-filters-text").html("Showing "+o+"/"+s.recordsTotal+". Clear all.");let l="Showing "+n+" to "+r+" of "+o+" entries";return l+=" (filtered from "+s.recordsTotal+" total entries)."},initComplete:function(){e("#search_bar").val(y),e("#type-filter-input").val(q),e("#tag-filter-input").val(w),e("#status-filter-input").val(b),function(t){e("#requirements_table").find("tbody").on("click","a",function(n){n.preventDefault(),N(t.row(e(n.target).parent()).index())})}(n),R(n),function(t){if(t.q.length>0){e("#status-filter-input").val(""),e("#tag-filter-input").val(""),e("#type-filter-input").val("");const n=":COL_INDEX_"+function(e){let t="00"+e;return t.substr(t.length-2)}(t.col).toString()+":"+t.q;e("#search_bar").val(n)}}(m),O(),z(),e.fn.dataTable.ext.search.push(function(e,t,n){return function(e){return x.evaluate(e,h)&&k.evaluate(e,h)}(t)}),this.api().draw()}})}function A(){let n=e("#requirement_guess_modal"),r=e("#available_guesses_cards"),a=e(".modal-content"),o=e("#requirement_id").val();function i(e){let t='<div class="card">                    <div class="pl-1 pr-1">                        <p>'+e.string+'                        </p>                    </div>                    <button type="button" class="btn btn-success btn-sm add_guess"                            title="Add formalization"                            data-scope="'+e.scope+'"                            data-pattern="'+e.pattern+"\"                            data-mapping='"+JSON.stringify(e.mapping)+"'>                        <strong>+ Add this formalization +</strong>                    </button>                </div>";r.append(t)}n.modal({keyboard:!1}),n.modal("show"),a.LoadingOverlay("show"),r.html(""),e.post("api/req/get_available_guesses",{requirement_id:o},function(e){if(!1===e.success)alert(e.errormsg);else for(let t=0;t<e.available_guesses.length;t++)i(e.available_guesses[t])}).done(function(){e(".add_guess").click(function(){!function(t,n,r){let a=e(".modal-content");a.LoadingOverlay("show");let o=e("#requirement_id").val();e.post("api/req/add_formalization_from_guess",{requirement_id:o,scope:t,pattern:n,mapping:JSON.stringify(r)},function(t){a.LoadingOverlay("hide",!0),!1===t.success?alert(t.errormsg):e("#formalization_accordion").append(t.html)}).done(function(){E(),S(),L(),T(),P()})}(e(this).data("scope"),e(this).data("pattern"),e(this).data("mapping"))}),t.update(e("#add_guess_description")),a.LoadingOverlay("hide",!0)})}function M(){let t=[{orderable:!1,className:"select-checkbox",targets:[0],data:null,defaultContent:""},{targets:[1],data:"pos"},{targets:[2],data:"id",render:function(e,t,n,r){return result='<a href="#">'+e+"</a>",result}},{targets:[3],data:"desc"},{targets:[4],data:"type",render:function(e,t,n,r){return u.indexOf(e)<=-1&&u.push(e),e}},{targets:[5],data:"tags",render:function(t,n,r,a){if(result="",e(t).each(function(e,t){var n;t.length>0&&(result+='<span class="badge" style="background-color: '+(n=t,_.hasOwnProperty(n)?_[n]:"#5bc0de")+'">'+t+"</span></br>",l.indexOf(t)<=-1&&l.push(t))}),r.formal.length>0){let t=!1,n=!1;e.each(r.formal,function(e,r){r.length>0&&"// None, // not formalizable"!==r?t||(t=!0,result+='<span class="badge badge-success">has_formalization</span></br>'):n||(n=!0,result+='<span class="badge badge-warning">incomplete_formalization</span></br>')})}return result}},{targets:[6],data:"status",render:function(e,t,n,r){return result='<span class="badge badge-info">'+e+"</span></br>",result}},{targets:[7],data:"formal",render:function(t,n,r,a){return result="",r.formal.length>0&&e(t).each(function(e,t){t.length>0&&(result+="<p>"+t+"</p>")}),result}}];e.get("api/table/colum_defs","",function(e){const n=e.col_defs.length;for(let r=0;r<n;r++)t.push({targets:[parseInt(e.col_defs[r].target)],data:e.col_defs[r].csv_name,visible:!1,searchable:!0})}).done(function(){I(t)})}function j(){let n=e("#requirement_modal");e("#requirement_tag_field").tokenfield({autocomplete:{source:l,delay:100},showAutocompleteOnFocus:!0}).change(function(e){n.data("unsaved_changes",!0)}),e("#requirement_status").change(function(){e("#requirement_modal").data("unsaved_changes",!0)}),n.on("hide.bs.modal",function(t){!function(t){!0===e("#requirement_modal").data("unsaved_changes")&&!0!==confirm("You have unsaved changes, do you really want to close?")&&t.preventDefault()}(t)}),e(document).keyup(function(t){if(e(".modal:visible").length&&27===t.keyCode){let t=e("input[type=text], textarea, select").filter(":focus");0===t.length?e("#requirement_guess_modal:visible").length?e("#requirement_guess_modal").modal("hide"):e("#requirement_modal").modal("hide"):t.each(function(t){e(this).blur()})}}),n.on("hidden.bs.modal",function(t){e("#requirement_tag_field").val(""),e("#requirement_tag_field-tokenfield").val("")}),e("#add_formalization").click(function(){!function(){let t=e(".modal-content");t.LoadingOverlay("show");const n=e("#requirement_id").val();e.post("api/req/new_formalization",{id:n},function(n){t.LoadingOverlay("hide",!0),!1===n.success?alert(n.errormsg):e("#formalization_accordion").append(n.html)}).done(function(){E(),S(),L(),T(),P()})}()}),e("#add_gussed_formalization").click(function(){A()}),e(".modal").on("hidden.bs.modal",function(t){e(".modal:visible").length&&e("body").addClass("modal-open")}),e("#formalization_accordion").on("shown.bs.collapse",".card",function(n){e(this).find("textarea").each(function(){t(e(this)),t.update(e(this))})}),E()}function F(){e.get("api/meta/get","",function(t){_=t.tag_colors,p=t.available_search_strings,e("#search_bar").autocomplete({source:p})})}function P(){e.get("api/logs/get","",function(t){e("#log_textarea").html(t)}).done(function(){e(".req_direct_link").click(function(){N(function(t){let n=-1;return e("#requirements_table").DataTable().column(2).data().filter(function(e,r){return e===t&&(n=r,!0)}),n}(e(this).data("rid")))}),e("#log_textarea").scrollTop(1e5)})}function J(){e.get("api/report/get",{},function(t){if(!1===t.success)alert(t.errormsg);else{let n="";f=t.data,e.each(t.data,function(e,t){n+=`<div class="card border-primary">\n                              <div class="card-body">\n                                <h5 class="card-title">Report ${e}</h5>\n                                <h6 class="card-subtitle mb-2 text-muted">Query</h6>\n                                <p class="card-text report-results">${t.queries}</p>\n                                <h6 class="card-subtitle mb-2 text-muted">Results</h6>\n                                <p class="card-text report-results">${t.results}</p>\n                                <a href="#" class="card-link open-report" data-id="${e}">\n                                    Edit (reevaluate) Report.\n                                </a>\n                                <a href="#" class="card-link delete-report" data-id="${e}">Delete Report.</a>\n                              </div>\n                            </div>`}),e("#available_reports").html(n)}})}function B(t=!1){let n=e("#report_query_textarea"),r=e("#report_results_textarea"),a="",o="",i=-1,s=e("#report_modal");!1!==t&&(i=t.attr("data-id"),a=f[i].queries,o=f[i].results),n.val(a),r.val(o),e("#save_report").attr("data-id",i),s.modal("show")}function $(){e("#add-new-report").click(function(){B()}),e("#eval_report").click(function(){!function(){let t=e("body");t.LoadingOverlay("show");const n=e("#report_query_textarea").val().split("\n");let a=e("#requirements_table").DataTable(),o="";try{e.each(n,function(e,t){x=r.fromQuery(t),a.draw();let n=a.page.info();o+=`Eval of query No. ${e} => ${n.recordsDisplay} results.\n`}),e("#report_results_textarea").val(o),O(),a.draw()}catch(e){alert(e)}t.LoadingOverlay("hide",!0)}()}),e("#save_report").click(function(){!function(){let t=e("body");t.LoadingOverlay("show"),e.post("api/report/set",{report_querys:e("#report_query_textarea").val(),report_results:e("#report_results_textarea").val(),report_id:e("#save_report").attr("data-id")},function(e){t.LoadingOverlay("hide",!0),!1===e.success&&alert(e.errormsg),J()})}()});let t=e("#available_reports");t.on("click",".open-report",function(t){B(e(this))}),t.on("click",".delete-report",function(t){var n;n=e(this).attr("data-id"),e.ajax({type:"DELETE",url:"api/report/delete",data:{report_id:n},success:function(e){!1===e.success&&alert(e.errormsg),J()}})}),J()}e(document).ready(function(){F(),M(),j(),function(){let t=e("#search_bar");e("#store_search").click(function(){let n=e("body");n.LoadingOverlay("show");const r=t.val();e.post("api/req_search/update",{query:r},function(e){n.LoadingOverlay("hide",!0),!1===e.success?alert(e.errormsg):(t.effect("highlight",{color:"green"},500),F())})}),t.on("keypress",function(n){if("Delete"===n.originalEvent.key){const n=t.val();if(p.includes(n)){let r=e("body");e.post("api/req_search/delete",{query:n},function(e){r.LoadingOverlay("hide",!0),!1===e.success?alert(e.errormsg):(t.effect("highlight",{color:"green"},500),F())})}}})}(),P(),$()})}).call(this,n(3))}});