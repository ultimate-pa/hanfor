!function(t){function e(e){for(var a,s,c=e[0],i=e[1],l=e[2],d=0,p=[];d<c.length;d++)s=c[d],r[s]&&p.push(r[s][0]),r[s]=0;for(a in i)Object.prototype.hasOwnProperty.call(i,a)&&(t[a]=i[a]);for(u&&u(e);p.length;)p.shift()();return o.push.apply(o,l||[]),n()}function n(){for(var t,e=0;e<o.length;e++){for(var n=o[e],a=!0,c=1;c<n.length;c++){var i=n[c];0!==r[i]&&(a=!1)}a&&(o.splice(e--,1),t=s(s.s=n[0]))}return t}var a={},r={3:0},o=[];function s(e){if(a[e])return a[e].exports;var n=a[e]={i:e,l:!1,exports:{}};return t[e].call(n.exports,n,n.exports,s),n.l=!0,n.exports}s.m=t,s.c=a,s.d=function(t,e,n){s.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:n})},s.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},s.t=function(t,e){if(1&e&&(t=s(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var n=Object.create(null);if(s.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var a in t)s.d(n,a,function(e){return t[e]}.bind(null,a));return n},s.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return s.d(e,"a",e),e},s.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},s.p="";var c=window.webpackJsonp=window.webpackJsonp||[],i=c.push.bind(c);c.push=e,c=c.slice();for(var l=0;l<c.length;l++)e(c[l]);var u=i;o.push([214,0]),n()}({214:function(t,e,n){(function(t){n(17),n(10),n(15),n(14),n(20),n(13),n(12);let e=sessionStorage.getItem("var_search_string");t(document).ready(function(){let n=t("#var_import_table").DataTable({paging:!0,stateSave:!0,select:{style:"os",selector:"td:first-child"},pageLength:200,responsive:!0,lengthMenu:[[10,50,100,500,-1],[10,50,100,500,"All"]],dom:'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',ajax:"api/"+session_id+"/get_table_data",deferRender:!0,columns:[{orderable:!1,className:"select-checkbox",targets:[0],data:null,defaultContent:""},{data:function(t,e,n,a){return t},targets:[1],render:function(t,e,n,a){return'<div class="btn-group" role="group" aria-label="Basic example"><button type="button" data-action="skip" class="skip-btn btn btn-secondary'+("skipped"===t.action?" active":"")+'">Skip</button><button type="button" data-action="source" class="source-btn btn btn-secondary'+("source"===t.action?" active":"")+'">Source</button><button type="button" data-action="target" class="target-btn btn btn-secondary'+("target"===t.action?" active":"")+'">Target</button><button type="button" data-action="custom" class="custom-btn btn btn-secondary'+("custom"===t.action?" active":"")+'">Custom</button></div>'}},{data:function(t,e,n,a){return t},targets:[1],render:function(t,e,n,a){let r="";return void 0!==t.source.name&&void 0!==t.target.name?(r+='<span class="badge badge-info">match_in_source_and_target</span>',t.source.type!==t.target.type?r+='<span class="badge badge-info">unmatched_types</span>':r+='<span class="badge badge-info">same_types</span>'):void 0===t.source.type?r+='<span class="badge badge-info">no_match_in_source</span>':void 0===t.target.name&&(r+='<span class="badge badge-info">no_match_in_target</span>'),r}},{data:function(t,e,n,a){return t.source},targets:[3],render:function(t,e,n,a){let r="";return r=void 0!==t.name?'<p class="source_link" style="cursor: pointer"><code>'+t.name+'</code><span class="badge badge-info">'+t.type+"</span></p>":"No match."}},{data:function(t,e,n,a){return t.target},targets:[4],render:function(t,e,n,a){let r="";return r=void 0!==t.name?'<p class="target_link" style="cursor: pointer"><code>'+t.name+'</code><span class="badge badge-info">'+t.type+"</span>":"No match."}},{data:function(t,e,n,a){return t.result},targets:[5],render:function(t,e,n,a){let r="";return r=void 0!==t.name?'<p class="result_link" style="cursor: pointer"><code>'+t.name+'</code><span class="badge badge-info">'+t.type+"</span>":"Skipped."}}],initComplete:function(){t("#search_bar").val(e)}});t("#search_bar").keyup(function(){n.search(t(this).val()).draw(),sessionStorage.setItem("var_search_string",t(this).val())});let a=t("#var_import_table tbody");a.on("click",".source_link, .target_link",function(e){e.preventDefault(),function(e,n){let a,r=t("#variable_view_modal");t("#variable_view_modal_title").html("Name: <code>"+e.name+"</code>"),"source_link"===n?a=e.source:"target_link"===n&&(a=e.target);let o="<h5>Type</h5><code>"+a.type+"</code>";"CONST"===a.type&&(o+="<h5>Const value</h5><code>"+a.const_val+"</code>"),t("#var_view_modal_body").html(o),r.modal("show")}(n.row(t(this).parents("tr")).data(),t(this)[0].className)}),a.on("click",".target-btn, .source-btn, .skip-btn",function(e){e.preventDefault();let a=n.row(t(this).parents("tr"));console.log(a.data()),function(t,e){let n=t.data();"source"===e?void 0!==n.source.name&&(n.result=n.source,n.action="source"):"target"===e?void 0!==n.target.name&&(n.result=n.target,n.action="target"):"skip"===e&&(n.result=n.target,n.action=void 0!==n.target.name?"target":"skipped"),t.data(n).draw("full-hold")}(a,t(this).attr("data-action"))}),t(".select-all-button").on("click",function(e){t(this).hasClass("btn-secondary")?n.rows({page:"current"}).select():n.rows({page:"current"}).deselect(),t(".select-all-button").toggleClass("btn-secondary btn-primary")}),n.on("user-select",function(){let e=t(".select-all-button");e.removeClass("btn-primary"),e.addClass("btn-secondary ")})})}).call(this,n(3))}});