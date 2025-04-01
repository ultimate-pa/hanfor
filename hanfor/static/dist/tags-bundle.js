(()=>{var e,a={1541:(e,a,t)=>{var n=t(4692);t(7081),t(9875),t(5194),t(97),t(7776),t(4371),t(5219),t(9145),t(1453),t(8131);const r=t(9692),{SearchNode:o}=t(1108),{Modal:c}=t(9875);t(6719);const i=[":AND:",":OR:",":NOT:",":COL_INDEX_00:",":COL_INDEX_01:",":COL_INDEX_02:"],l=sessionStorage.getItem("tagsSearchString");function s(e){sessionStorage.setItem("tagsSearchString",e),search_tree=o.fromQuery(e)}n(document).ajaxStart((function(){n.LoadingOverlay("show")})),n(document).ajaxStop((function(){n.LoadingOverlay("hide")})),n(document).ready((function(){const e=n("#search_bar"),a=n("#tags-table"),t=a.DataTable({paging:!0,stateSave:!0,pageLength:50,responsive:!0,lengthMenu:[[10,50,100,500,-1],[10,50,100,500,"All"]],dom:'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',ajax:{url:"../api/tags/",dataSrc:""},deferRender:!0,columns:d,initComplete:function(){e.val(l),s(e.val().trim()),n.fn.dataTable.ext.search.push((function(e,a,t){return function(e){return search_tree.evaluate(e,[!0,!0,!0])}(a)})),this.api().draw()}});new n.fn.dataTable.ColReorder(t,{}),e.keypress((function(a){13===a.which&&(s(e.val().trim()),t.draw())})),new Awesomplete(e[0],{filter:function(e,a){let t=!1;return(a.split(":").length-1)%2==1&&(t=Awesomplete.FILTER_CONTAINS(e,a.match(/[^:]*$/)[0])),t},item:function(e,a){return Awesomplete.ITEM(e,a.match(/(:)([\S]*$)/)[2])},replace:function(e){const a=this.input.value.match(/(.*)(:(?!.*:).*$)/)[1];this.input.value=a+e},list:i,minChars:1,autoFirst:!0}),a.find("tbody").on("click","a.modal-opener",(function(e){e.preventDefault();let a=t.row(n(e.target).parent()).data(),r=t.row(n(e.target).parent()).index();c.getOrCreateInstance(n("#tag-modal")).show(),n("#modal-associated-row-index").val(r),n("#tag-name-old").val(a.name),n("#occurences").val(a.used_by),n("#tag-modal-title").html("Tag: "+a.name),n("#tag-name").val(a.name),n("#tag-color").val(a.color),n("#tag-description").val(a.description),n("#tag-internal").prop("checked",a.internal)})),n("#save-tag-modal").click((function(){!function(){let e=n("#tag-name-old").val(),a=n("#tag-name").val(),t=n("#occurences").val().split(","),r=n("#tag-color").val(),o=n("#tag-description").val(),c=n("#tag-internal").prop("checked");n.ajax({type:"PATCH",url:`../api/tags/${e}`,contentType:"application/json",data:JSON.stringify({name_new:a,occurrences:t,color:r,description:o,internal:c})}).done((function(e){location.reload()})).fail((function(e,a,t){alert(t+"\n\n"+e.responseText)}))}()})),t.on("click",".internal-checkbox",(function(e){e.preventDefault();let a=e.currentTarget,r=t.row(a.parentNode).data();n.ajax({type:"POST",url:"../api/tags/update",data:{name:r.name,name_old:r.name,occurences:r.used_by,color:r.color,description:r.description,internal:a.checked},success:function(e){!1!==e.success?(a.checked=e.data.internal,r.internal=e.data.internal):alert(e.errormsg)}})})),n(".delete-tag").bootstrapConfirmButton({onConfirm:function(){!function(){const e=n("#tag-name").val(),a=n("#occurences").val().split(",");n.ajax({type:"DELETE",url:`../api/tags/${e}`,contentType:"application/json",data:JSON.stringify({occurrences:a})}).done((function(e){location.reload()})).fail((function(e,a,t){alert(t+"\n\n"+e.responseText)}))}()}}),r(n("#tag-description")),n("#tag-modal").on("shown.bs.modal",(function(e){r.update(n("#tag-description"))})),n(".clear-all-filters").click((function(){e.val("").effect("highlight",{color:"green"},500),s(e.val().trim()),t.draw()})),n("#add-standard-tags").click((function(){n.ajax({type:"POST",url:"../api/tags/add_standard"}).done((function(e){location.reload()})).fail((function(e,a,t){alert(t+"\n\n"+e.responseText)}))}))}));const d=[{data:"name",render:function(e,a,t,n){return`<a class="modal-opener" href="#">${e}</a>`}},{data:"description",render:function(e,a,t,n){return`<div class="white-space-pre">${e}</div>`}},{data:"used_by",render:function(e,a,t,r){let o="";if(n(e).each((function(e,a){a.length>0&&(o+=`<span class="badge bg-info"><a href="${base_url}?command=search&col=2&q=%5C%22${a}%5C%22" target="_blank" class="link-light">${a}</a></span> `)})),e.length>1&&o.length>0){const e=`?command=search&col=5&q=%5C%22${t.name}%5C%22`;o+=`<span class="badge bg-info"><a href="${base_url}${e}" target="_blank" class="link-light">Show all</a></span> `}return o}},{data:"internal",render:function(e,a,t,n){return`<input class="form-check-input internal-checkbox" type="checkbox" ${e?"checked":""}>`}},{data:"used_by",visible:!1,searchable:!1,render:function(e,a,t,n){return e.filter((e=>e&&""!==e)).join(", ")}}]}},t={};function n(e){var r=t[e];if(void 0!==r)return r.exports;var o=t[e]={id:e,exports:{}};return a[e].call(o.exports,o,o.exports,n),o.exports}n.m=a,e=[],n.O=(a,t,r,o)=>{if(!t){var c=1/0;for(d=0;d<e.length;d++){for(var[t,r,o]=e[d],i=!0,l=0;l<t.length;l++)(!1&o||c>=o)&&Object.keys(n.O).every((e=>n.O[e](t[l])))?t.splice(l--,1):(i=!1,o<c&&(c=o));if(i){e.splice(d--,1);var s=r();void 0!==s&&(a=s)}}return a}o=o||0;for(var d=e.length;d>0&&e[d-1][2]>o;d--)e[d]=e[d-1];e[d]=[t,r,o]},n.n=e=>{var a=e&&e.__esModule?()=>e.default:()=>e;return n.d(a,{a}),a},n.d=(e,a)=>{for(var t in a)n.o(a,t)&&!n.o(e,t)&&Object.defineProperty(e,t,{enumerable:!0,get:a[t]})},n.o=(e,a)=>Object.prototype.hasOwnProperty.call(e,a),n.r=e=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},n.j=192,(()=>{var e={192:0};n.O.j=a=>0===e[a];var a=(a,t)=>{var r,o,[c,i,l]=t,s=0;if(c.some((a=>0!==e[a]))){for(r in i)n.o(i,r)&&(n.m[r]=i[r]);if(l)var d=l(n)}for(a&&a(t);s<c.length;s++)o=c[s],n.o(e,o)&&e[o]&&e[o][0](),e[o]=0;return n.O(d)},t=self.webpackChunkhanfor=self.webpackChunkhanfor||[];t.forEach(a.bind(null,0)),t.push=a.bind(null,t.push.bind(t))})(),n.nc=void 0;var r=n.O(void 0,[223],(()=>n(1541)));r=n.O(r)})();