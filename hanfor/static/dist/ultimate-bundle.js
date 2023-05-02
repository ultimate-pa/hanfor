(()=>{var e,t={5931:(e,t,a)=>{var r=a(9755);a(1388),a(4712),a(5700),a(944),a(3889),a(7175),a(6824);const{SearchNode:n}=a(3024),l=sessionStorage.getItem("ultimateSearchString"),{Modal:o}=a(4712);let i;r(document).ready((function(){const e=r("#search_bar"),t=r("#ultimate-jobs-tbl"),a=t.DataTable({paging:!0,stateSave:!0,pageLength:50,responsive:!0,lengthMenu:[[10,50,100,500,-1],[10,50,100,500,"All"]],dom:'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',ajax:{url:"../api/ultimate/jobs"},deferRender:!0,columns:d,initComplete:function(){e.val(l),u(e.val().trim()),r.fn.dataTable.ext.search.push((function(e,t){return function(e){return i.evaluate(e,[!0,!0,!0])}(t)})),this.api().draw()}});new r.fn.dataTable.ColReorder(a,{}),e.keypress((function(t){13===t.which&&(u(e.val().trim()),a.draw())})),r(".clear-all-filters").click((function(){e.val("").effect("highlight",{color:"green"},500),u(e.val().trim()),a.draw()}));const n=r("#ultimate-job-modal-result-tbl").DataTable({paging:!0,stateSave:!0,pageLength:50,responsive:!0,lengthMenu:[[10,50,100,500,-1],[10,50,100,500,"All"]],dom:'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',deferRender:!0,columns:s,initComplete:function(){this.api().draw()}});t.find("tbody").on("click","a.modal-opener",(function(e){e.preventDefault();let t=a.row(r(e.target).parent()).data();o.getOrCreateInstance(r("#ultimate-job-modal")).show(),r("#ultimate-job-modal-title").html("Job ID: "+t.requestId),r("#ultimate-job-modal-request-time").text(t.request_time),r("#ultimate-job-modal-last-update").text(t.last_update),r("#ultimate-job-modal-request-status").text(t.status),n.clear(),n.rows.add(t.result),n.draw(),r("#ultimate-tag-modal-download-btn").click((function(){var e;e=t.requestId,r.ajax({type:"GET",url:"../api/ultimate/job/"+e+"?download=true"}).done((function(e){!function(e,t){let a=document.createElement("a");a.setAttribute("href","data:text/plain;charset=utf-8,"+encodeURIComponent(t)),a.setAttribute("download",e),a.style.display="none",document.body.appendChild(a),a.click(),document.body.removeChild(a)}(e.job_id+".json",JSON.stringify(e,null,4))})).fail((function(e,t,a){alert(a+"\n\n"+e.responseText)}))}))}))}));const d=[{data:"requestId",render:function(e){return`<a class="modal-opener" href="#">${e}</a>`}},{data:"request_time",order:"asc",render:function(e){return`<div class="white-space-pre">${e}</div>`}},{data:"last_update",render:function(e){return`<div class="white-space-pre">${e}</div>`}},{data:"status",render:function(e){return`<div class="white-space-pre">${e}</div>`}},{data:"selected_requirements",render:function(e){let t="";for(let a=0;a<e.length;a++){let r=e[a][0],n=e[a][1];"True"!==display_req_without_formalisation&&0===n||(t+=`<span class="badge ${0===n?"bg-light":"bg-info"}"><a href="${base_url}?command=search&col=2&q=%5C%22${r}%5C%22" target="_blank" class="link-light text-muted">${r} (${n})</a></span> `)}return t}},{data:"result_requirements",render:function(e){let t="";for(let a=0;a<e.length;a++){let r=e[a][0],n=e[a][1];t+=`<span class="badge ${0===n?"bg-light":"bg-info"}"><a href="${base_url}?command=search&col=2&q=%5C%22${r}%5C%22" target="_blank" class="link-light text-muted">${r} (${n})</a></span> `}return t}}],s=[{data:"logLvl"},{data:"type"},{data:"shortDesc",render:function(e){return`${e.replaceAll("\n","<br/>")}`}},{data:"longDesc",render:function(e){return`${e.replaceAll("\n","<br/>")}`}}];function u(e){sessionStorage.setItem("ultimateSearchString",e),i=n.fromQuery(e)}}},a={};function r(e){var n=a[e];if(void 0!==n)return n.exports;var l=a[e]={id:e,exports:{}};return t[e].call(l.exports,l,l.exports,r),l.exports}r.m=t,e=[],r.O=(t,a,n,l)=>{if(!a){var o=1/0;for(u=0;u<e.length;u++){for(var[a,n,l]=e[u],i=!0,d=0;d<a.length;d++)(!1&l||o>=l)&&Object.keys(r.O).every((e=>r.O[e](a[d])))?a.splice(d--,1):(i=!1,l<o&&(o=l));if(i){e.splice(u--,1);var s=n();void 0!==s&&(t=s)}}return t}l=l||0;for(var u=e.length;u>0&&e[u-1][2]>l;u--)e[u]=e[u-1];e[u]=[a,n,l]},r.n=e=>{var t=e&&e.__esModule?()=>e.default:()=>e;return r.d(t,{a:t}),t},r.d=(e,t)=>{for(var a in t)r.o(t,a)&&!r.o(e,a)&&Object.defineProperty(e,a,{enumerable:!0,get:t[a]})},r.o=(e,t)=>Object.prototype.hasOwnProperty.call(e,t),r.r=e=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},r.j=304,(()=>{var e={304:0};r.O.j=t=>0===e[t];var t=(t,a)=>{var n,l,[o,i,d]=a,s=0;if(o.some((t=>0!==e[t]))){for(n in i)r.o(i,n)&&(r.m[n]=i[n]);if(d)var u=d(r)}for(t&&t(a);s<o.length;s++)l=o[s],r.o(e,l)&&e[l]&&e[l][0](),e[l]=0;return r.O(u)},a=self.webpackChunkhanfor=self.webpackChunkhanfor||[];a.forEach(t.bind(null,0)),a.push=t.bind(null,a.push.bind(a))})(),r.nc=void 0;var n=r.O(void 0,[351],(()=>r(5931)));n=r.O(n)})();