(()=>{var e,t={5406:(e,t,r)=>{var o=r(9755);r(4712);const n=r(4712),a=o("#awesome-message-button");n.Button.getOrCreateInstance("#awesome-message-button"),o(document).ready((function(){a.click((function(){o.ajax({type:"POST",url:"/api/example-blueprint",contentType:"application/json",data:JSON.stringify({id:123,data:"some data"})}).done((function(e,t,r){console.log("data:",e,"textStatus:",t,"jqXHR:",r),alert(e)})).fail((function(e,t,r){console.log("jqXHR:",e,"textStatus:",t,"errorThrown:",r),alert(r+"\n\n"+e.responseText)}))}))}))}},r={};function o(e){var n=r[e];if(void 0!==n)return n.exports;var a=r[e]={id:e,exports:{}};return t[e].call(a.exports,a,a.exports,o),a.exports}o.m=t,e=[],o.O=(t,r,n,a)=>{if(!r){var l=1/0;for(f=0;f<e.length;f++){for(var[r,n,a]=e[f],i=!0,s=0;s<r.length;s++)(!1&a||l>=a)&&Object.keys(o.O).every((e=>o.O[e](r[s])))?r.splice(s--,1):(i=!1,a<l&&(l=a));if(i){e.splice(f--,1);var u=n();void 0!==u&&(t=u)}}return t}a=a||0;for(var f=e.length;f>0&&e[f-1][2]>a;f--)e[f]=e[f-1];e[f]=[r,n,a]},o.n=e=>{var t=e&&e.__esModule?()=>e.default:()=>e;return o.d(t,{a:t}),t},o.d=(e,t)=>{for(var r in t)o.o(t,r)&&!o.o(e,r)&&Object.defineProperty(e,r,{enumerable:!0,get:t[r]})},o.o=(e,t)=>Object.prototype.hasOwnProperty.call(e,t),o.r=e=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},o.j=299,(()=>{var e={299:0};o.O.j=t=>0===e[t];var t=(t,r)=>{var n,a,[l,i,s]=r,u=0;if(l.some((t=>0!==e[t]))){for(n in i)o.o(i,n)&&(o.m[n]=i[n]);if(s)var f=s(o)}for(t&&t(r);u<l.length;u++)a=l[u],o.o(e,a)&&e[a]&&e[a][0](),e[a]=0;return o.O(f)},r=self.webpackChunkhanfor=self.webpackChunkhanfor||[];r.forEach(t.bind(null,0)),r.push=t.bind(null,r.push.bind(r))})(),o.nc=void 0;var n=o.O(void 0,[351],(()=>o(5406)));n=o.O(n)})();