(()=>{var e,t={6849:(e,t,n)=>{var r=n(4692);n(7081),n(5194),n(9875),n(6719);const o=n(9875),a=r("#check-completeness-button");o.Button.getOrCreateInstance("#check-completeness-button"),r(document).ready((function(){const e=r("#completeness-table").DataTable({paging:!0,stateSave:!0,pageLength:50,responsive:!0,lengthMenu:[[10,50,100,500,-1],[10,50,100,500,"All"]],dom:'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',ajax:{url:"api/quickchecks/results",dataSrc:""},deferRender:!0,columns:l,initComplete:function(){this.api().draw()}});a.click((function(){r.ajax({type:"POST",url:"api/quickchecks",contentType:"application/json"}).done((function(t,n,r){e.ajax.reload(null,!1)})).fail((function(e,t,n){console.log("jqXHR:",e,"textStatus:",t,"errorThrown:",n),alert(n+"\n\n"+e.responseText)}))}))}));const l=[{title:"ID"},{title:"Check"},{title:"Result"},{title:"Description",render:function(e){return`${e.replaceAll("\n","<br/>")}`}}]}},n={};function r(e){var o=n[e];if(void 0!==o)return o.exports;var a=n[e]={id:e,exports:{}};return t[e].call(a.exports,a,a.exports,r),a.exports}r.m=t,e=[],r.O=(t,n,o,a)=>{if(!n){var l=1/0;for(u=0;u<e.length;u++){for(var[n,o,a]=e[u],i=!0,c=0;c<n.length;c++)(!1&a||l>=a)&&Object.keys(r.O).every((e=>r.O[e](n[c])))?n.splice(c--,1):(i=!1,a<l&&(l=a));if(i){e.splice(u--,1);var s=o();void 0!==s&&(t=s)}}return t}a=a||0;for(var u=e.length;u>0&&e[u-1][2]>a;u--)e[u]=e[u-1];e[u]=[n,o,a]},r.n=e=>{var t=e&&e.__esModule?()=>e.default:()=>e;return r.d(t,{a:t}),t},r.d=(e,t)=>{for(var n in t)r.o(t,n)&&!r.o(e,n)&&Object.defineProperty(e,n,{enumerable:!0,get:t[n]})},r.o=(e,t)=>Object.prototype.hasOwnProperty.call(e,t),r.r=e=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},r.j=663,(()=>{var e={663:0};r.O.j=t=>0===e[t];var t=(t,n)=>{var o,a,[l,i,c]=n,s=0;if(l.some((t=>0!==e[t]))){for(o in i)r.o(i,o)&&(r.m[o]=i[o]);if(c)var u=c(r)}for(t&&t(n);s<l.length;s++)a=l[s],r.o(e,a)&&e[a]&&e[a][0](),e[a]=0;return r.O(u)},n=self.webpackChunkhanfor=self.webpackChunkhanfor||[];n.forEach(t.bind(null,0)),n.push=t.bind(null,n.push.bind(n))})(),r.nc=void 0;var o=r.O(void 0,[223],(()=>r(6849)));o=r.O(o)})();