(()=>{var e,t={1585:(e,t,a)=>{var n=a(4692);a(1403),a(9875),a(5194),a(7776),a(4371),a(8131),a(1453);const{SearchNode:r}=a(1108),l=sessionStorage.getItem("ultimateSearchString"),{Modal:o}=a(9875);let i,s;n(document).ready((function(){const e=n("#search_bar"),t=n("#ultimate-jobs-tbl"),a=t.DataTable({paging:!0,stateSave:!0,pageLength:50,responsive:!0,lengthMenu:[[10,50,100,500,-1],[10,50,100,500,"All"]],dom:'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',ajax:{url:"../api/ultimate/jobs"},deferRender:!0,columns:u,initComplete:function(){e.val(l),c(e.val().trim()),n.fn.dataTable.ext.search.push((function(e,t){return function(e){return i.evaluate(e,[!0,!0,!0])}(t)})),this.api().draw(),f()}});e.keypress((function(t){13===t.which&&(c(e.val().trim()),a.draw())})),n(".clear-all-filters").click((function(){e.val("").effect("highlight",{color:"green"},500),c(e.val().trim()),a.draw()}));const r=n("#ultimate-job-modal-result-tbl").DataTable({paging:!0,stateSave:!0,pageLength:50,responsive:!0,lengthMenu:[[10,50,100,500,-1],[10,50,100,500,"All"]],dom:'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',deferRender:!0,columns:d,initComplete:function(){this.api().draw()}});t.find("tbody").on("click","a.modal-opener",(function(e){e.preventDefault();let t=a.row(n(e.target).parent()).data();o.getOrCreateInstance(n("#ultimate-job-modal")).show(),n("#ultimate-job-modal-title").html("Job ID: "+t.requestId),n("#ultimate-job-modal-request-time").text(t.request_time),n("#ultimate-job-modal-last-update").text(t.last_update),n("#ultimate-job-modal-request-status").text(t.status),r.clear(),r.rows.add(t.result),r.draw(),n("#ultimate-tag-modal-download-btn").click((function(){var e;e=t.requestId,n.ajax({type:"GET",url:"../api/ultimate/job/"+e+"?download=true"}).done((function(e){!function(e,t){let a=document.createElement("a");a.setAttribute("href","data:text/plain;charset=utf-8,"+encodeURIComponent(t)),a.setAttribute("download",e),a.style.display="none",document.body.appendChild(a),a.click(),document.body.removeChild(a)}(e.job_id+".json",JSON.stringify(e,null,4)),f()})).fail((function(e,t,a){alert(a+"\n\n"+e.responseText)}))})),n("#ultimate-tag-modal-cancel-btn").click((function(){var e;e=t.requestId,console.log("delete"),n.ajax({type:"DELETE",url:"../api/ultimate/job/"+e}).done((function(e){f()})).fail((function(e,t,a){alert(a+"\n\n"+e.responseText)}))}))}))}));const u=[{data:"requestId",render:function(e){return`<a class="modal-opener" href="#">${e}</a>`}},{data:"request_time",order:"asc",render:function(e){return`<div class="white-space-pre">${e}</div>`}},{data:"last_update",render:function(e){return`<div class="white-space-pre">${e}</div>`}},{data:"status",render:function(e){return`<div class="white-space-pre">${e}</div>`}},{data:"selected_requirements",render:function(e){let t="";for(let a=0;a<e.length;a++){let n=e[a][0],r=e[a][1];"True"!==display_req_without_formalisation&&0===r||(t+=`<span class="badge ${0===r?"bg-light":"bg-info"}"><a href="${base_url}?command=search&col=2&q=%5C%22${n}%5C%22" target="_blank" class="link-light text-muted">${n} (${r})</a></span> `)}return t}},{data:"result_requirements",render:function(e){let t="";for(let a=0;a<e.length;a++){let n=e[a][0],r=e[a][1];t+=`<span class="badge ${0===r?"bg-light":"bg-info"}"><a href="${base_url}?command=search&col=2&q=%5C%22${n}%5C%22" target="_blank" class="link-light text-muted">${n} (${r})</a></span> `}return t}}],d=[{data:"logLvl"},{data:"type"},{data:"shortDesc",render:function(e){return`${e.replaceAll("\n","<br/>")}`}},{data:"longDesc",render:function(e){return`${e.replaceAll("\n","<br/>")}`}}];function c(e){sessionStorage.setItem("ultimateSearchString",e),i=r.fromQuery(e)}function f(){clearInterval(s),n.ajax({type:"GET",url:"../api/ultimate/update-all"}).done((function(e){"done"===e.status&&n("#ultimate-jobs-tbl").DataTable().ajax.reload(),s=setTimeout(f,6e4)})).fail((function(e,t,a){alert(a+"\n\n"+e.responseText)}))}}},a={};function n(e){var r=a[e];if(void 0!==r)return r.exports;var l=a[e]={id:e,exports:{}};return t[e].call(l.exports,l,l.exports,n),l.exports}n.m=t,e=[],n.O=(t,a,r,l)=>{if(!a){var o=1/0;for(d=0;d<e.length;d++){for(var[a,r,l]=e[d],i=!0,s=0;s<a.length;s++)(!1&l||o>=l)&&Object.keys(n.O).every((e=>n.O[e](a[s])))?a.splice(s--,1):(i=!1,l<o&&(o=l));if(i){e.splice(d--,1);var u=r();void 0!==u&&(t=u)}}return t}l=l||0;for(var d=e.length;d>0&&e[d-1][2]>l;d--)e[d]=e[d-1];e[d]=[a,r,l]},n.n=e=>{var t=e&&e.__esModule?()=>e.default:()=>e;return n.d(t,{a:t}),t},n.d=(e,t)=>{for(var a in t)n.o(t,a)&&!n.o(e,a)&&Object.defineProperty(e,a,{enumerable:!0,get:t[a]})},n.o=(e,t)=>Object.prototype.hasOwnProperty.call(e,t),n.r=e=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},n.j=330,(()=>{var e={330:0};n.O.j=t=>0===e[t];var t=(t,a)=>{var r,l,[o,i,s]=a,u=0;if(o.some((t=>0!==e[t]))){for(r in i)n.o(i,r)&&(n.m[r]=i[r]);if(s)var d=s(n)}for(t&&t(a);u<o.length;u++)l=o[u],n.o(e,l)&&e[l]&&e[l][0](),e[l]=0;return n.O(d)},a=self.webpackChunkhanfor=self.webpackChunkhanfor||[];a.forEach(t.bind(null,0)),a.push=t.bind(null,a.push.bind(a))})(),n.nc=void 0;var r=n.O(void 0,[223],(()=>n(1585)));r=n.O(r)})();