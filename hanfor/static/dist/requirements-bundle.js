!function(e){function t(t){for(var r,o,s=t[0],l=t[1],c=t[2],f=0,d=[];f<s.length;f++)o=s[f],a[o]&&d.push(a[o][0]),a[o]=0;for(r in l)Object.prototype.hasOwnProperty.call(l,r)&&(e[r]=l[r]);for(u&&u(t);d.length;)d.shift()();return i.push.apply(i,c||[]),n()}function n(){for(var e,t=0;t<i.length;t++){for(var n=i[t],r=!0,s=1;s<n.length;s++){var l=n[s];0!==a[l]&&(r=!1)}r&&(i.splice(t--,1),e=o(o.s=n[0]))}return e}var r={},a={4:0},i=[];function o(t){if(r[t])return r[t].exports;var n=r[t]={i:t,l:!1,exports:{}};return e[t].call(n.exports,n,n.exports,o),n.l=!0,n.exports}o.m=e,o.c=r,o.d=function(e,t,n){o.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:n})},o.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},o.t=function(e,t){if(1&t&&(e=o(e)),8&t)return e;if(4&t&&"object"==typeof e&&e&&e.__esModule)return e;var n=Object.create(null);if(o.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var r in e)o.d(n,r,function(t){return e[t]}.bind(null,r));return n},o.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return o.d(t,"a",t),t},o.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},o.p="";var s=window.webpackJsonp=window.webpackJsonp||[],l=s.push.bind(s);s.push=t,s=s.slice();for(var c=0;c<s.length;c++)t(s[c]);var u=l;i.push([221,0]),n()}({215:function(e,t){const n={":AND:":1,":OR:":1},r={":AND:":1,":OR:":1},a={},i={"(":1,")":1},o={":AND:":3,":OR:":2};class s{constructor(e){this.left=!1,this.value=e,this.right=!1,this.col_target=-1,this.update_target()}update_target(){const e=this.value.indexOf(":COL_INDEX_");if(e>=0){const t=parseInt(this.value.substring(e+11,e+13));t>=0&&(this.value=this.value.substring(e+14),this.col_target=t)}}evaluate(e,t){return function e(t,n,r){if(void 0===t)return!0;if(!1===t.left&&!1===t.right){let e="";if(-1!==t.col_target)e=n[t.col_target];else for(let t=0;t<r.length;t++)r[t]&&(e+=n[t]+" ");const a=t.value.indexOf(":NOT:");return a>=0?!l(t.value.substring(a+5),e):l(t.value,e)}let a=e(t.left,n,r);let i=e(t.right,n,r);if(":AND:"===t.value)return a&&i;if(":OR:"===t.value)return a||i}(this,e,t)}static is_search_string(e){return!(e in i||e in n)}static to_string(e){let t="";return!1!==e.left&&(t+=s.to_string(e.left)+" "),t+=e.value,!1!==e.right&&(t+=" "+s.to_string(e.right)),t}static peek(e){return e[e.length-1]}static searchArrayToTree(e){let t=[],i=[];for(let l=0,c=e.length;l<c;l++){const c=e[l];if(s.is_search_string(c))t.push(new s(c));else if(c in n){for(;i.length;){const e=s.peek(i);if(!(e in n&&(c in r&&o[c]<=o[e]||c in a&&o[c]<o[e])))break;{let e=t.pop(),n=t.pop(),r=new s(i.pop());r.left=n,r.right=e,t.push(r)}}i.push(c)}else if("("===c)i.push(c);else{if(")"!==c)throw"Error: Token unknown: "+c;{let e=!1;for(;i.length;){const n=i.pop();if("("===n){e=!0;break}{let e=t.pop(),r=t.pop(),a=new s(n);a.left=r,a.right=e,t.push(a)}}if(!e)throw"Error: parentheses mismatch."}}}for(;i.length;){const e=i.pop();if("("===e||")"===e)throw"Error: Parentheses mismatch.";let n=t.pop(),r=t.pop(),a=new s(e);a.left=r,a.right=n,t.push(a)}return 0===t.length&&t.push(new s("")),t[0]}static awesomeQuerySplitt0r(e,t){let r=e.split(/(:OR:|:AND:|\(|\))/g);if(r=r.filter(String),void 0!==t)for(let e=0,a=r.length;e<a;e++)r[e]in n||r[e]in i||(r[e]=":COL_INDEX_"+("00"+t).slice(-2)+":"+r[e]);return r}static fromQuery(e="",t){return s.searchArrayToTree(s.awesomeQuerySplitt0r(e,t))}}function l(e,t){return e=e.startsWith('""')&&e.endsWith('""')?"^\\s*"+e.substr(2,e.length-4)+"\\s*$":e.replace(/([^\\])?\"/g,"$1\\b"),new RegExp(e,"i").test(t)}e.exports={SearchNode:s}},216:function(e,t,n){var r,a,i;
/*!
 * jQuery UI Effects 1.12.1
 * http://jqueryui.com
 *
 * Copyright jQuery Foundation and other contributors
 * Released under the MIT license.
 * http://jquery.org/license
 */a=[n(3),n(5)],void 0===(i="function"==typeof(r=function(e){var t,n="ui-effects-animated",r=e;return e.effects={effect:{}},
/*!
 * jQuery Color Animations v2.1.2
 * https://github.com/jquery/jquery-color
 *
 * Copyright 2014 jQuery Foundation and other contributors
 * Released under the MIT license.
 * http://jquery.org/license
 *
 * Date: Wed Jan 16 08:47:09 2013 -0600
 */
function(e,t){var n,r=/^([\-+])=\s*(\d+\.?\d*)/,a=[{re:/rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,\s*(\d?(?:\.\d+)?)\s*)?\)/,parse:function(e){return[e[1],e[2],e[3],e[4]]}},{re:/rgba?\(\s*(\d+(?:\.\d+)?)\%\s*,\s*(\d+(?:\.\d+)?)\%\s*,\s*(\d+(?:\.\d+)?)\%\s*(?:,\s*(\d?(?:\.\d+)?)\s*)?\)/,parse:function(e){return[2.55*e[1],2.55*e[2],2.55*e[3],e[4]]}},{re:/#([a-f0-9]{2})([a-f0-9]{2})([a-f0-9]{2})/,parse:function(e){return[parseInt(e[1],16),parseInt(e[2],16),parseInt(e[3],16)]}},{re:/#([a-f0-9])([a-f0-9])([a-f0-9])/,parse:function(e){return[parseInt(e[1]+e[1],16),parseInt(e[2]+e[2],16),parseInt(e[3]+e[3],16)]}},{re:/hsla?\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\%\s*,\s*(\d+(?:\.\d+)?)\%\s*(?:,\s*(\d?(?:\.\d+)?)\s*)?\)/,space:"hsla",parse:function(e){return[e[1],e[2]/100,e[3]/100,e[4]]}}],i=e.Color=function(t,n,r,a){return new e.Color.fn.parse(t,n,r,a)},o={rgba:{props:{red:{idx:0,type:"byte"},green:{idx:1,type:"byte"},blue:{idx:2,type:"byte"}}},hsla:{props:{hue:{idx:0,type:"degrees"},saturation:{idx:1,type:"percent"},lightness:{idx:2,type:"percent"}}}},s={byte:{floor:!0,max:255},percent:{max:1},degrees:{mod:360,floor:!0}},l=i.support={},c=e("<p>")[0],u=e.each;function f(e,t,n){var r=s[t.type]||{};return null==e?n||!t.def?null:t.def:(e=r.floor?~~e:parseFloat(e),isNaN(e)?t.def:r.mod?(e+r.mod)%r.mod:0>e?0:r.max<e?r.max:e)}function d(t){var r=i(),s=r._rgba=[];return t=t.toLowerCase(),u(a,function(e,n){var a,i=n.re.exec(t),l=i&&n.parse(i),c=n.space||"rgba";if(l)return a=r[c](l),r[o[c].cache]=a[o[c].cache],s=r._rgba=a._rgba,!1}),s.length?("0,0,0,0"===s.join()&&e.extend(s,n.transparent),r):n[t]}function p(e,t,n){return 6*(n=(n+1)%1)<1?e+(t-e)*n*6:2*n<1?t:3*n<2?e+(t-e)*(2/3-n)*6:e}c.style.cssText="background-color:rgba(1,1,1,.5)",l.rgba=c.style.backgroundColor.indexOf("rgba")>-1,u(o,function(e,t){t.cache="_"+e,t.props.alpha={idx:3,type:"percent",def:1}}),i.fn=e.extend(i.prototype,{parse:function(t,r,a,s){if(void 0===t)return this._rgba=[null,null,null,null],this;(t.jquery||t.nodeType)&&(t=e(t).css(r),r=void 0);var l=this,c=e.type(t),p=this._rgba=[];return void 0!==r&&(t=[t,r,a,s],c="array"),"string"===c?this.parse(d(t)||n._default):"array"===c?(u(o.rgba.props,function(e,n){p[n.idx]=f(t[n.idx],n)}),this):"object"===c?(u(o,t instanceof i?function(e,n){t[n.cache]&&(l[n.cache]=t[n.cache].slice())}:function(n,r){var a=r.cache;u(r.props,function(e,n){if(!l[a]&&r.to){if("alpha"===e||null==t[e])return;l[a]=r.to(l._rgba)}l[a][n.idx]=f(t[e],n,!0)}),l[a]&&e.inArray(null,l[a].slice(0,3))<0&&(l[a][3]=1,r.from&&(l._rgba=r.from(l[a])))}),this):void 0},is:function(e){var t=i(e),n=!0,r=this;return u(o,function(e,a){var i,o=t[a.cache];return o&&(i=r[a.cache]||a.to&&a.to(r._rgba)||[],u(a.props,function(e,t){if(null!=o[t.idx])return n=o[t.idx]===i[t.idx]})),n}),n},_space:function(){var e=[],t=this;return u(o,function(n,r){t[r.cache]&&e.push(n)}),e.pop()},transition:function(e,t){var n=i(e),r=n._space(),a=o[r],l=0===this.alpha()?i("transparent"):this,c=l[a.cache]||a.to(l._rgba),d=c.slice();return n=n[a.cache],u(a.props,function(e,r){var a=r.idx,i=c[a],o=n[a],l=s[r.type]||{};null!==o&&(null===i?d[a]=o:(l.mod&&(o-i>l.mod/2?i+=l.mod:i-o>l.mod/2&&(i-=l.mod)),d[a]=f((o-i)*t+i,r)))}),this[r](d)},blend:function(t){if(1===this._rgba[3])return this;var n=this._rgba.slice(),r=n.pop(),a=i(t)._rgba;return i(e.map(n,function(e,t){return(1-r)*a[t]+r*e}))},toRgbaString:function(){var t="rgba(",n=e.map(this._rgba,function(e,t){return null==e?t>2?1:0:e});return 1===n[3]&&(n.pop(),t="rgb("),t+n.join()+")"},toHslaString:function(){var t="hsla(",n=e.map(this.hsla(),function(e,t){return null==e&&(e=t>2?1:0),t&&t<3&&(e=Math.round(100*e)+"%"),e});return 1===n[3]&&(n.pop(),t="hsl("),t+n.join()+")"},toHexString:function(t){var n=this._rgba.slice(),r=n.pop();return t&&n.push(~~(255*r)),"#"+e.map(n,function(e){return 1===(e=(e||0).toString(16)).length?"0"+e:e}).join("")},toString:function(){return 0===this._rgba[3]?"transparent":this.toRgbaString()}}),i.fn.parse.prototype=i.fn,o.hsla.to=function(e){if(null==e[0]||null==e[1]||null==e[2])return[null,null,null,e[3]];var t,n,r=e[0]/255,a=e[1]/255,i=e[2]/255,o=e[3],s=Math.max(r,a,i),l=Math.min(r,a,i),c=s-l,u=s+l,f=.5*u;return t=l===s?0:r===s?60*(a-i)/c+360:a===s?60*(i-r)/c+120:60*(r-a)/c+240,n=0===c?0:f<=.5?c/u:c/(2-u),[Math.round(t)%360,n,f,null==o?1:o]},o.hsla.from=function(e){if(null==e[0]||null==e[1]||null==e[2])return[null,null,null,e[3]];var t=e[0]/360,n=e[1],r=e[2],a=e[3],i=r<=.5?r*(1+n):r+n-r*n,o=2*r-i;return[Math.round(255*p(o,i,t+1/3)),Math.round(255*p(o,i,t)),Math.round(255*p(o,i,t-1/3)),a]},u(o,function(t,n){var a=n.props,o=n.cache,s=n.to,l=n.from;i.fn[t]=function(t){if(s&&!this[o]&&(this[o]=s(this._rgba)),void 0===t)return this[o].slice();var n,r=e.type(t),c="array"===r||"object"===r?t:arguments,d=this[o].slice();return u(a,function(e,t){var n=c["object"===r?e:t.idx];null==n&&(n=d[t.idx]),d[t.idx]=f(n,t)}),l?((n=i(l(d)))[o]=d,n):i(d)},u(a,function(n,a){i.fn[n]||(i.fn[n]=function(i){var o,s=e.type(i),l="alpha"===n?this._hsla?"hsla":"rgba":t,c=this[l](),u=c[a.idx];return"undefined"===s?u:("function"===s&&(i=i.call(this,u),s=e.type(i)),null==i&&a.empty?this:("string"===s&&(o=r.exec(i))&&(i=u+parseFloat(o[2])*("+"===o[1]?1:-1)),c[a.idx]=i,this[l](c)))})})}),i.hook=function(t){var n=t.split(" ");u(n,function(t,n){e.cssHooks[n]={set:function(t,r){var a,o,s="";if("transparent"!==r&&("string"!==e.type(r)||(a=d(r)))){if(r=i(a||r),!l.rgba&&1!==r._rgba[3]){for(o="backgroundColor"===n?t.parentNode:t;(""===s||"transparent"===s)&&o&&o.style;)try{s=e.css(o,"backgroundColor"),o=o.parentNode}catch(e){}r=r.blend(s&&"transparent"!==s?s:"_default")}r=r.toRgbaString()}try{t.style[n]=r}catch(e){}}},e.fx.step[n]=function(t){t.colorInit||(t.start=i(t.elem,n),t.end=i(t.end),t.colorInit=!0),e.cssHooks[n].set(t.elem,t.start.transition(t.end,t.pos))}})},i.hook("backgroundColor borderBottomColor borderLeftColor borderRightColor borderTopColor color columnRuleColor outlineColor textDecorationColor textEmphasisColor"),e.cssHooks.borderColor={expand:function(e){var t={};return u(["Top","Right","Bottom","Left"],function(n,r){t["border"+r+"Color"]=e}),t}},n=e.Color.names={aqua:"#00ffff",black:"#000000",blue:"#0000ff",fuchsia:"#ff00ff",gray:"#808080",green:"#008000",lime:"#00ff00",maroon:"#800000",navy:"#000080",olive:"#808000",purple:"#800080",red:"#ff0000",silver:"#c0c0c0",teal:"#008080",white:"#ffffff",yellow:"#ffff00",transparent:[null,null,null,0],_default:"#ffffff"}}(r),function(){var t,n=["add","remove","toggle"],a={border:1,borderBottom:1,borderColor:1,borderLeft:1,borderRight:1,borderTop:1,borderWidth:1,margin:1,padding:1};function i(t){var n,r,a=t.ownerDocument.defaultView?t.ownerDocument.defaultView.getComputedStyle(t,null):t.currentStyle,i={};if(a&&a.length&&a[0]&&a[a[0]])for(r=a.length;r--;)"string"==typeof a[n=a[r]]&&(i[e.camelCase(n)]=a[n]);else for(n in a)"string"==typeof a[n]&&(i[n]=a[n]);return i}e.each(["borderLeftStyle","borderRightStyle","borderBottomStyle","borderTopStyle"],function(t,n){e.fx.step[n]=function(e){("none"!==e.end&&!e.setAttr||1===e.pos&&!e.setAttr)&&(r.style(e.elem,n,e.end),e.setAttr=!0)}}),e.fn.addBack||(e.fn.addBack=function(e){return this.add(null==e?this.prevObject:this.prevObject.filter(e))}),e.effects.animateClass=function(t,r,o,s){var l=e.speed(r,o,s);return this.queue(function(){var r,o=e(this),s=o.attr("class")||"",c=l.children?o.find("*").addBack():o;c=c.map(function(){return{el:e(this),start:i(this)}}),(r=function(){e.each(n,function(e,n){t[n]&&o[n+"Class"](t[n])})})(),c=c.map(function(){return this.end=i(this.el[0]),this.diff=function(t,n){var r,i,o={};for(r in n)i=n[r],t[r]!==i&&(a[r]||!e.fx.step[r]&&isNaN(parseFloat(i))||(o[r]=i));return o}(this.start,this.end),this}),o.attr("class",s),c=c.map(function(){var t=this,n=e.Deferred(),r=e.extend({},l,{queue:!1,complete:function(){n.resolve(t)}});return this.el.animate(this.diff,r),n.promise()}),e.when.apply(e,c.get()).done(function(){r(),e.each(arguments,function(){var t=this.el;e.each(this.diff,function(e){t.css(e,"")})}),l.complete.call(o[0])})})},e.fn.extend({addClass:(t=e.fn.addClass,function(n,r,a,i){return r?e.effects.animateClass.call(this,{add:n},r,a,i):t.apply(this,arguments)}),removeClass:function(t){return function(n,r,a,i){return arguments.length>1?e.effects.animateClass.call(this,{remove:n},r,a,i):t.apply(this,arguments)}}(e.fn.removeClass),toggleClass:function(t){return function(n,r,a,i,o){return"boolean"==typeof r||void 0===r?a?e.effects.animateClass.call(this,r?{add:n}:{remove:n},a,i,o):t.apply(this,arguments):e.effects.animateClass.call(this,{toggle:n},r,a,i)}}(e.fn.toggleClass),switchClass:function(t,n,r,a,i){return e.effects.animateClass.call(this,{add:n,remove:t},r,a,i)}})}(),function(){var t;function r(t,n,r,a){return e.isPlainObject(t)&&(n=t,t=t.effect),t={effect:t},null==n&&(n={}),e.isFunction(n)&&(a=n,r=null,n={}),("number"==typeof n||e.fx.speeds[n])&&(a=r,r=n,n={}),e.isFunction(r)&&(a=r,r=null),n&&e.extend(t,n),r=r||n.duration,t.duration=e.fx.off?0:"number"==typeof r?r:r in e.fx.speeds?e.fx.speeds[r]:e.fx.speeds._default,t.complete=a||n.complete,t}function a(t){return!(t&&"number"!=typeof t&&!e.fx.speeds[t])||"string"==typeof t&&!e.effects.effect[t]||!!e.isFunction(t)||"object"==typeof t&&!t.effect}function i(e,t){var n=t.outerWidth(),r=t.outerHeight(),a=/^rect\((-?\d*\.?\d*px|-?\d+%|auto),?\s*(-?\d*\.?\d*px|-?\d+%|auto),?\s*(-?\d*\.?\d*px|-?\d+%|auto),?\s*(-?\d*\.?\d*px|-?\d+%|auto)\)$/.exec(e)||["",0,n,r,0];return{top:parseFloat(a[1])||0,right:"auto"===a[2]?n:parseFloat(a[2]),bottom:"auto"===a[3]?r:parseFloat(a[3]),left:parseFloat(a[4])||0}}e.expr&&e.expr.filters&&e.expr.filters.animated&&(e.expr.filters.animated=(t=e.expr.filters.animated,function(r){return!!e(r).data(n)||t(r)})),!1!==e.uiBackCompat&&e.extend(e.effects,{save:function(e,t){for(var n=0,r=t.length;n<r;n++)null!==t[n]&&e.data("ui-effects-"+t[n],e[0].style[t[n]])},restore:function(e,t){for(var n,r=0,a=t.length;r<a;r++)null!==t[r]&&(n=e.data("ui-effects-"+t[r]),e.css(t[r],n))},setMode:function(e,t){return"toggle"===t&&(t=e.is(":hidden")?"show":"hide"),t},createWrapper:function(t){if(t.parent().is(".ui-effects-wrapper"))return t.parent();var n={width:t.outerWidth(!0),height:t.outerHeight(!0),float:t.css("float")},r=e("<div></div>").addClass("ui-effects-wrapper").css({fontSize:"100%",background:"transparent",border:"none",margin:0,padding:0}),a={width:t.width(),height:t.height()},i=document.activeElement;try{i.id}catch(e){i=document.body}return t.wrap(r),(t[0]===i||e.contains(t[0],i))&&e(i).trigger("focus"),r=t.parent(),"static"===t.css("position")?(r.css({position:"relative"}),t.css({position:"relative"})):(e.extend(n,{position:t.css("position"),zIndex:t.css("z-index")}),e.each(["top","left","bottom","right"],function(e,r){n[r]=t.css(r),isNaN(parseInt(n[r],10))&&(n[r]="auto")}),t.css({position:"relative",top:0,left:0,right:"auto",bottom:"auto"})),t.css(a),r.css(n).show()},removeWrapper:function(t){var n=document.activeElement;return t.parent().is(".ui-effects-wrapper")&&(t.parent().replaceWith(t),(t[0]===n||e.contains(t[0],n))&&e(n).trigger("focus")),t}}),e.extend(e.effects,{version:"1.12.1",define:function(t,n,r){return r||(r=n,n="effect"),e.effects.effect[t]=r,e.effects.effect[t].mode=n,r},scaledDimensions:function(e,t,n){if(0===t)return{height:0,width:0,outerHeight:0,outerWidth:0};var r="horizontal"!==n?(t||100)/100:1,a="vertical"!==n?(t||100)/100:1;return{height:e.height()*a,width:e.width()*r,outerHeight:e.outerHeight()*a,outerWidth:e.outerWidth()*r}},clipToBox:function(e){return{width:e.clip.right-e.clip.left,height:e.clip.bottom-e.clip.top,left:e.clip.left,top:e.clip.top}},unshift:function(e,t,n){var r=e.queue();t>1&&r.splice.apply(r,[1,0].concat(r.splice(t,n))),e.dequeue()},saveStyle:function(e){e.data("ui-effects-style",e[0].style.cssText)},restoreStyle:function(e){e[0].style.cssText=e.data("ui-effects-style")||"",e.removeData("ui-effects-style")},mode:function(e,t){var n=e.is(":hidden");return"toggle"===t&&(t=n?"show":"hide"),(n?"hide"===t:"show"===t)&&(t="none"),t},getBaseline:function(e,t){var n,r;switch(e[0]){case"top":n=0;break;case"middle":n=.5;break;case"bottom":n=1;break;default:n=e[0]/t.height}switch(e[1]){case"left":r=0;break;case"center":r=.5;break;case"right":r=1;break;default:r=e[1]/t.width}return{x:r,y:n}},createPlaceholder:function(t){var n,r=t.css("position"),a=t.position();return t.css({marginTop:t.css("marginTop"),marginBottom:t.css("marginBottom"),marginLeft:t.css("marginLeft"),marginRight:t.css("marginRight")}).outerWidth(t.outerWidth()).outerHeight(t.outerHeight()),/^(static|relative)/.test(r)&&(r="absolute",n=e("<"+t[0].nodeName+">").insertAfter(t).css({display:/^(inline|ruby)/.test(t.css("display"))?"inline-block":"block",visibility:"hidden",marginTop:t.css("marginTop"),marginBottom:t.css("marginBottom"),marginLeft:t.css("marginLeft"),marginRight:t.css("marginRight"),float:t.css("float")}).outerWidth(t.outerWidth()).outerHeight(t.outerHeight()).addClass("ui-effects-placeholder"),t.data("ui-effects-placeholder",n)),t.css({position:r,left:a.left,top:a.top}),n},removePlaceholder:function(e){var t="ui-effects-placeholder",n=e.data(t);n&&(n.remove(),e.removeData(t))},cleanUp:function(t){e.effects.restoreStyle(t),e.effects.removePlaceholder(t)},setTransition:function(t,n,r,a){return a=a||{},e.each(n,function(e,n){var i=t.cssUnit(n);i[0]>0&&(a[n]=i[0]*r+i[1])}),a}}),e.fn.extend({effect:function(){var t=r.apply(this,arguments),a=e.effects.effect[t.effect],i=a.mode,o=t.queue,s=o||"fx",l=t.complete,c=t.mode,u=[],f=function(t){var r=e(this),a=e.effects.mode(r,c)||i;r.data(n,!0),u.push(a),i&&("show"===a||a===i&&"hide"===a)&&r.show(),i&&"none"===a||e.effects.saveStyle(r),e.isFunction(t)&&t()};if(e.fx.off||!a)return c?this[c](t.duration,l):this.each(function(){l&&l.call(this)});function d(r){var o=e(this);function s(){e.isFunction(l)&&l.call(o[0]),e.isFunction(r)&&r()}t.mode=u.shift(),!1===e.uiBackCompat||i?"none"===t.mode?(o[c](),s()):a.call(o[0],t,function(){o.removeData(n),e.effects.cleanUp(o),"hide"===t.mode&&o.hide(),s()}):(o.is(":hidden")?"hide"===c:"show"===c)?(o[c](),s()):a.call(o[0],t,s)}return!1===o?this.each(f).each(d):this.queue(s,f).queue(s,d)},show:function(e){return function(t){if(a(t))return e.apply(this,arguments);var n=r.apply(this,arguments);return n.mode="show",this.effect.call(this,n)}}(e.fn.show),hide:function(e){return function(t){if(a(t))return e.apply(this,arguments);var n=r.apply(this,arguments);return n.mode="hide",this.effect.call(this,n)}}(e.fn.hide),toggle:function(e){return function(t){if(a(t)||"boolean"==typeof t)return e.apply(this,arguments);var n=r.apply(this,arguments);return n.mode="toggle",this.effect.call(this,n)}}(e.fn.toggle),cssUnit:function(t){var n=this.css(t),r=[];return e.each(["em","px","%","pt"],function(e,t){n.indexOf(t)>0&&(r=[parseFloat(n),t])}),r},cssClip:function(e){return e?this.css("clip","rect("+e.top+"px "+e.right+"px "+e.bottom+"px "+e.left+"px)"):i(this.css("clip"),this)},transfer:function(t,n){var r=e(this),a=e(t.to),i="fixed"===a.css("position"),o=e("body"),s=i?o.scrollTop():0,l=i?o.scrollLeft():0,c=a.offset(),u={top:c.top-s,left:c.left-l,height:a.innerHeight(),width:a.innerWidth()},f=r.offset(),d=e("<div class='ui-effects-transfer'></div>").appendTo("body").addClass(t.className).css({top:f.top-s,left:f.left-l,height:r.innerHeight(),width:r.innerWidth(),position:i?"fixed":"absolute"}).animate(u,t.duration,t.easing,function(){d.remove(),e.isFunction(n)&&n()})}}),e.fx.step.clip=function(t){t.clipInit||(t.start=e(t.elem).cssClip(),"string"==typeof t.end&&(t.end=i(t.end,t.elem)),t.clipInit=!0),e(t.elem).cssClip({top:t.pos*(t.end.top-t.start.top)+t.start.top,right:t.pos*(t.end.right-t.start.right)+t.start.right,bottom:t.pos*(t.end.bottom-t.start.bottom)+t.start.bottom,left:t.pos*(t.end.left-t.start.left)+t.start.left})}}(),t={},e.each(["Quad","Cubic","Quart","Quint","Expo"],function(e,n){t[n]=function(t){return Math.pow(t,e+2)}}),e.extend(t,{Sine:function(e){return 1-Math.cos(e*Math.PI/2)},Circ:function(e){return 1-Math.sqrt(1-e*e)},Elastic:function(e){return 0===e||1===e?e:-Math.pow(2,8*(e-1))*Math.sin((80*(e-1)-7.5)*Math.PI/15)},Back:function(e){return e*e*(3*e-2)},Bounce:function(e){for(var t,n=4;e<((t=Math.pow(2,--n))-1)/11;);return 1/Math.pow(4,3-n)-7.5625*Math.pow((3*t-2)/22-e,2)}}),e.each(t,function(t,n){e.easing["easeIn"+t]=n,e.easing["easeOut"+t]=function(e){return 1-n(1-e)},e.easing["easeInOut"+t]=function(e){return e<.5?n(2*e)/2:1-n(-2*e+2)/2}}),e.effects})?r.apply(t,a):r)||(e.exports=i)},217:function(e,t,n){var r,a,i;
/*!
 * jQuery UI Effects Highlight 1.12.1
 * http://jqueryui.com
 *
 * Copyright jQuery Foundation and other contributors
 * Released under the MIT license.
 * http://jquery.org/license
 */a=[n(3),n(5),n(216)],void 0===(i="function"==typeof(r=function(e){return e.effects.define("highlight","show",function(t,n){var r=e(this),a={backgroundColor:r.css("backgroundColor")};"hide"===t.mode&&(a.opacity=0),e.effects.saveStyle(r),r.css({backgroundImage:"none",backgroundColor:t.color||"#ffff99"}).animate(a,{queue:!1,duration:t.duration,easing:t.easing,complete:n})})})?r.apply(t,a):r)||(e.exports=i)},221:function(e,t,n){(function(e){n(19),n(12),n(18),n(17),n(152),n(16),n(217),n(15);const{SearchNode:t}=n(215);let r=n(156),{Textcomplete:a,Textarea:i}=n(155),o=new r([],{}),s=["","has_formalization"],l=["","Todo","Review","Done"],c=[""],u=[""],f=[!0,!0,!0,!0,!0,!0],d=[],p=JSON.parse(search_query),h={},m=[],g=sessionStorage.getItem("req_search_string"),_=sessionStorage.getItem("filter_status_string"),v=sessionStorage.getItem("filter_tag_string"),b=sessionStorage.getItem("filter_type_string"),y=void 0,w=void 0;function q(){g=e("#search_bar").val().trim(),sessionStorage.setItem("req_search_string",g),y=t.fromQuery(query=g)}function x(){function n(e,n,r){return n.length>0&&(e.length>0&&(e=e.concat([":AND:"])),e=e.concat(function(e){return["("].concat(e,[")"])}(t.awesomeQuerySplitt0r(n,r)))),e}d=[],_=e("#status-filter-input").val(),v=e("#tag-filter-input").val(),b=e("#type-filter-input").val(),sessionStorage.setItem("filter_status_string",_),sessionStorage.setItem("filter_tag_string",v),sessionStorage.setItem("filter_type_string",b),d=n(d=n(d=n(d,b,4),v,5),_,6),w=t.searchArrayToTree(d)}function C(e){let t=[];return e.rows({selected:!0}).every(function(){let e=this.data();t.push(e.id)}),t}function z(){e(".requirement_var_group").each(function(){e(this).hide(),e(this).removeClass("type-error")}),e(".formalization_card").each(function(t){if(formalization_id=e(this).attr("title"),selected_scope=e("#requirement_scope"+formalization_id).val(),selected_pattern=e("#requirement_pattern"+formalization_id).val(),header=e("#formalization_heading"+formalization_id),var_p=e("#requirement_var_group_p"+formalization_id),var_q=e("#requirement_var_group_q"+formalization_id),var_r=e("#requirement_var_group_r"+formalization_id),var_s=e("#requirement_var_group_s"+formalization_id),var_t=e("#requirement_var_group_t"+formalization_id),var_u=e("#requirement_var_group_u"+formalization_id),formalization_id in m)for(let e=0;e<m[formalization_id].length;e++)window["var_"+m[formalization_id][e]].addClass("type-error"),header.addClass("type-error-head");else header.removeClass("type-error-head");switch(selected_scope){case"BEFORE":case"AFTER":var_p.show();break;case"BETWEEN":case"AFTER_UNTIL":var_p.show(),var_q.show()}switch(selected_pattern){case"Absence":case"Universality":case"Existence":case"BoundedExistence":var_r.show();break;case"Invariant":case"Precedence":case"Response":case"MinDuration":case"MaxDuration":case"BoundedRecurrence":var_r.show(),var_s.show();break;case"PrecedenceChain1-2":case"PrecedenceChain2-1":case"ResponseChain1-2":case"ResponseChain2-1":case"BoundedResponse":case"BoundedInvariance":case"TimeConstrainedInvariant":var_r.show(),var_s.show(),var_t.show();break;case"ConstrainedChain":case"TimeConstrainedMinDuration":case"ConstrainedTimedExistence":var_r.show(),var_s.show(),var_t.show(),var_u.show();break;case"NotFormalizable":var_p.hide(),var_q.hide()}})}function k(){e(".formalization_card").each(function(t){formalization_id=e(this).attr("title"),formalization="",selected_scope=e("#requirement_scope"+formalization_id).find("option:selected").text().replace(/\s\s+/g," "),selected_pattern=e("#requirement_pattern"+formalization_id).find("option:selected").text().replace(/\s\s+/g," "),"None"!==selected_scope&&"None"!==selected_pattern&&(formalization=selected_scope+", "+selected_pattern+"."),var_p=e("#formalization_var_p"+formalization_id).val(),var_q=e("#formalization_var_q"+formalization_id).val(),var_r=e("#formalization_var_r"+formalization_id).val(),var_s=e("#formalization_var_s"+formalization_id).val(),var_t=e("#formalization_var_t"+formalization_id).val(),var_u=e("#formalization_var_u"+formalization_id).val(),var_p.length>0&&(formalization=formalization.replace(/{P}/g,var_p)),var_q.length>0&&(formalization=formalization.replace(/{Q}/g,var_q)),var_r.length>0&&(formalization=formalization.replace(/{R}/g,var_r)),var_s.length>0&&(formalization=formalization.replace(/{S}/g,var_s)),var_t.length>0&&(formalization=formalization.replace(/{T}/g,var_t)),var_u.length>0&&(formalization=formalization.replace(/{U}/g,var_u)),e("#current_formalization_textarea"+formalization_id).val(formalization)}),e("#requirement_formalization_updated").val("true")}function O(t){requirement_modal_content=e(".modal-content"),requirement_modal_content.LoadingOverlay("show"),req_id=e("#requirement_id").val(),e.post("api/req/predict_pattern",{id:req_id,reset:t},function(t){requirement_modal_content.LoadingOverlay("hide",!0),!1===t.success?alert(t.errormsg):(e("#requirement_scope").html(t.scopes),e("#requirement_pattern").html(t.patterns))})}function S(){e(".formalization_selector").change(function(){z(),k()}),e(".reqirement-variable, .req_var_type").change(function(){k()}),e(".delete_formalization").confirmation({rootSelector:".delete_formalization"}).click(function(){var t;t=e(this).attr("name"),requirement_modal_content=e(".modal-content"),requirement_modal_content.LoadingOverlay("show"),req_id=e("#requirement_id").val(),e.post("api/req/del_formalization",{requirement_id:req_id,formalization_id:t},function(t){requirement_modal_content.LoadingOverlay("hide",!0),!1===t.success?alert(t.errormsg):e("#formalization_accordion").html(t.html)}).done(function(){z(),k(),S(),T(),E()})})}function T(){e(".reqirement-variable").each(function(t){let n=new i(this),r=new a(n,{dropdown:{maxCount:10}});r.register([{match:/(^|\s|[!=&\|>]+)(\w+)$/,search:function(e,t){include_elems=function(e){return o.search(e)}(e),result=[];for(let e=0;e<Math.min(10,include_elems.length);e++)result.push(u[include_elems[e]]);t(result)},replace:function(e){return"$1"+e+" "}}]),e(this).on("blur click",function(e){r.dropdown.deactivate(),e.preventDefault()})})}function L(t){if(-1===t)return void alert("Requirement not found.");let n=requirements_table.row(t).data();requirement_modal_content=e(".modal-content"),e("#requirement_modal").modal("show"),requirement_modal_content.LoadingOverlay("show"),e("#formalization_accordion").html(""),e("#requirement_tag_field").data("bs.tokenfield").$input.autocomplete({source:s}),requirement=e.get("api/req/get",{id:n.id,row_idx:t},function(n){e("#requirement_id").val(n.id),e("#requirement_formalization_updated").val("false"),e("#modal_associated_row_index").val(t),u=n.available_vars,m=n.type_inference_errors,o=new r(u,{shouldSort:!0,threshold:.6,location:0,distance:100,maxPatternLength:12,minMatchCharLength:1,keys:void 0}),e("#requirement_modal_title").html(n.id+": "+n.type),e("#description_textarea").text(n.desc),e("#add_guess_description").text(n.desc),e("#formalization_accordion").html(n.formalizations_html),e("#requirement_scope").val(n.scope),e("#requirement_pattern").val(n.pattern),e("#requirement_tag_field").tokenfield("setTokens",n.tags),e("#requirement_status").val(n.status),csv_row_content=e("#csv_content_accordion"),csv_row_content.html(""),csv_row_content.collapse("hide");let a=n.csv_data;for(const e in a)if(a.hasOwnProperty(e)){const t=a[e];csv_row_content.append("<p><strong>"+e+":</strong>"+t+"</p>")}!1===n.success&&alert("Could Not load the Requirement: "+n.errormsg)}).done(function(){z(),T(),S(),e("#requirement_tag_field").on("tokenfield:createtoken",function(t){let n=e(this).tokenfield("getTokens");e.each(n,function(e,n){n.value===t.attrs.value&&t.preventDefault()})}),requirement_modal_content.LoadingOverlay("hide",!0)})}function N(){let t=e("#requirements_table").DataTable(),n=[];e.each(t.columns().visible(),function(t,r){!1===r?(e("#col_toggle_button_"+t).removeClass("btn-info").addClass("btn-secondary"),n.push(!1)):(e("#col_toggle_button_"+t).removeClass("btn-secondary").addClass("btn-info"),n.push(!0))}),f=n}function I(t){t.columns().every(function(e){e>0&&t.column(e).header().append(" ("+e+")")}),e("#save_requirement_modal").click(function(){!function(t){requirement_modal_content=e(".modal-content"),requirement_modal_content.LoadingOverlay("show"),req_id=e("#requirement_id").val(),req_tags=e("#requirement_tag_field").val(),req_status=e("#requirement_status").val(),updated_formalization=e("#requirement_formalization_updated").val(),associated_row_id=parseInt(e("#modal_associated_row_index").val());let n={};e(".formalization_card").each(function(t){let r={};r.id=e(this).attr("title"),e(this).find("select").each(function(){e(this).hasClass("scope_selector")&&(r.scope=e(this).val()),e(this).hasClass("pattern_selector")&&(r.pattern=e(this).val())}),r.expression_mapping={},e(this).find("textarea.reqirement-variable").each(function(){""!==e(this).attr("title")&&(r.expression_mapping[e(this).attr("title")]=e(this).val())}),n[r.id]=r}),e.post("api/req/update",{id:req_id,row_idx:associated_row_id,update_formalization:updated_formalization,tags:req_tags,status:req_status,formalizations:JSON.stringify(n)},function(n){requirement_modal_content.LoadingOverlay("hide",!0),!1===n.success?alert(n.errormsg):(t.row(associated_row_id).data(n),e("#requirement_modal").modal("hide"))}).done(function(){E()})}(t)}),e("#search_bar").keypress(function(e){13===e.which&&(q(),t.draw())}),e("#type-filter-input").autocomplete({minLength:0,source:c,delay:100}),e("#status-filter-input").autocomplete({minLength:0,source:l,delay:100}),e("#tag-filter-input").autocomplete({minLength:0,source:s,delay:100}),e("#tag-filter-input, #status-filter-input, #type-filter-input").on("focus",function(){e(this).keydown()}).on("keypress",function(e){13===e.which&&(x(),t.draw())}),e("#table-filter-toggle").click(function(){e("#tag-filter-input").autocomplete({source:s}),e("#type-filter-input").autocomplete({source:c})}),e(".clear-all-filters").click(function(){e("#status-filter-input").val("").effect("highlight",{color:"green"},500),e("#tag-filter-input").val("").effect("highlight",{color:"green"},500),e("#type-filter-input").val("").effect("highlight",{color:"green"},500),e("#search_bar").val("").effect("highlight",{color:"green"},500),x(),q(),t.draw()}),e("#gen-req-from-selection").click(function(){req_ids=[],t.rows({search:"applied"}).every(function(){let e=this.data();req_ids.push(e.id)}),e("#selected_requirement_ids").val(JSON.stringify(req_ids)),e("#generate_req_form").submit()}),e("#gen-csv-from-selection").click(function(){req_ids=[],t.rows({search:"applied"}).every(function(){let e=this.data();req_ids.push(e.id)}),e("#selected_csv_requirement_ids").val(JSON.stringify(req_ids)),e("#generate_csv_form").submit()}),e("#sort_by_guess").click(function(){e(this).hasClass("btn-secondary")?(O(),e(this).removeClass("btn-secondary").addClass("btn-success").text("On")):(e(this).removeClass("btn-success").addClass("btn-secondary").text("Off"),O(reset=!0))}),e(".colum-toggle-button").on("click",function(n){n.preventDefault();let r=t.column(e(this).attr("data-column"));state=r.visible(!r.visible()),N()}),e(".reset-colum-toggle").on("click",function(e){e.preventDefault(),t.columns(".default-col").visible(!0),t.columns(".extra-col").visible(!1),N()}),N(),e(".select-all-button").on("click",function(n){e(this).hasClass("btn-secondary")?t.rows({page:"current"}).select():t.rows({page:"current"}).deselect(),e(".select-all-button").toggleClass("btn-secondary btn-primary")}),t.on("user-select",function(){let t=e(".select-all-button");t.removeClass("btn-primary"),t.addClass("btn-secondary ")}),e("#multi-add-tag-input, #multi-remove-tag-input").autocomplete({minLength:0,source:s,delay:100}).on("focus",function(){e(this).keydown()}).val(""),e("#multi-set-status-input").autocomplete({minLength:0,source:l,delay:100}).on("focus",function(){e(this).keydown()}).val(""),e(".apply-multi-edit").click(function(){!function(t){let n=e("body");n.LoadingOverlay("show");let r=e("#multi-add-tag-input").val().trim(),a=e("#multi-remove-tag-input").val().trim(),i=e("#multi-set-status-input").val().trim(),o=C(t);e.post("api/req/multi_update",{add_tag:r,remove_tag:a,set_status:i,selected_ids:JSON.stringify(o)},function(e){n.LoadingOverlay("hide",!0),!1===e.success?alert(e.errormsg):location.reload()})}(t)}),e(".add_top_guess_button").confirmation({rootSelector:".add_top_guess_button"}).click(function(){!function(t){let n=e("body");n.LoadingOverlay("show");let r=C(t);e.post("api/req/multi_add_top_guess",{selected_ids:JSON.stringify(r)},function(e){n.LoadingOverlay("hide",!0),!1===e.success?alert(e.errormsg):location.reload()})}(t)})}function R(t){requirements_table=e("#requirements_table").DataTable({language:{emptyTable:"Loading data."},paging:!0,stateSave:!0,select:{style:"os",selector:"td:first-child"},pageLength:50,lengthMenu:[[10,50,100,500,-1],[10,50,100,500,"All"]],dom:'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',ajax:"api/req/gets",deferRender:!0,columnDefs:t,createdRow:function(t,n,r){"Heading"===n.type&&e(t).addClass("bg-primary"),"Information"===n.type&&e(t).addClass("table-info"),"Requirement"===n.type&&e(t).addClass("table-warning"),"not set"===n.type&&e(t).addClass("table-light")},initComplete:function(){e("#search_bar").val(g),e("#type-filter-input").val(b),e("#tag-filter-input").val(v),e("#status-filter-input").val(_),function(t){e("#requirements_table").find("tbody").on("click","a",function(n){n.preventDefault(),L(t.row(e(n.target).parent()).index())})}(requirements_table),I(requirements_table),function(e,t){e.search("").columns().search(""),t.q.length>0&&e.columns(Number(t.col)).search("^"+t.q+"$",!0,!1),e.draw()}(requirements_table,p),q(),x(),e.fn.dataTable.ext.search.push(function(e,t,n){return console.log("Evaluate search"),function(e){return y.evaluate(e,f)&&w.evaluate(e,f)}(t)}),this.api().draw()}})}function D(){let t=e("#requirement_guess_modal"),n=e("#available_guesses_cards"),r=e(".modal-content"),a=e("#requirement_id").val();function i(e){let t='<div id="available_guesses_cards" >                <div class="card">                    <div class="pl-1 pr-1">                        <p>'+e.string+'                        </p>                    </div>                    <button type="button" class="btn btn-success btn-sm add_guess"                            title="Add formalization"                            data-scope="'+e.scope+'"                            data-pattern="'+e.pattern+"\"                            data-mapping='"+JSON.stringify(e.mapping)+"'>                        <strong>+ Add this formalization +</strong>                    </button>                </div>            </div>";n.append(t)}t.modal("show"),r.LoadingOverlay("show"),n.html(""),e.post("api/req/get_available_guesses",{requirement_id:a},function(e){if(!1===e.success)alert(e.errormsg);else for(let t=0;t<e.available_guesses.length;t++)i(e.available_guesses[t])}).done(function(){e(".add_guess").click(function(){!function(t,n,r){let a=e(".modal-content");a.LoadingOverlay("show");let i=e("#requirement_id").val();e.post("api/req/add_formalization_from_guess",{requirement_id:i,scope:t,pattern:n,mapping:JSON.stringify(r)},function(t){a.LoadingOverlay("hide",!0),!1===t.success?alert(t.errormsg):e("#formalization_accordion").append(t.html)}).done(function(){z(),k(),S(),T(),E()})}(e(this).data("scope"),e(this).data("pattern"),e(this).data("mapping"))}),r.LoadingOverlay("hide",!0)})}function M(){let t=[{orderable:!1,className:"select-checkbox",targets:[0],data:null,defaultContent:""},{targets:[1],data:"pos"},{targets:[2],data:"id",render:function(e,t,n,r){return result='<a href="#">'+e+"</a>",result}},{targets:[3],data:"desc"},{targets:[4],data:"type",render:function(e,t,n,r){return c.indexOf(e)<=-1&&c.push(e),e}},{targets:[5],data:"tags",render:function(t,n,r,a){return result="",e(t).each(function(e,t){var n;t.length>0&&(result+='<span class="badge" style="background-color: '+(n=t,h.hasOwnProperty(n)?h[n]:"#5bc0de")+'">'+t+"</span></br>",s.indexOf(t)<=-1&&s.push(t))}),r.formal.length>0&&(result+='<span class="badge badge-success">has_formalization</span></br>'),result}},{targets:[6],data:"status",render:function(e,t,n,r){return result='<span class="badge badge-info">'+e+"</span></br>",result}},{targets:[7],data:"formal",render:function(t,n,r,a){return result="",r.formal.length>0&&e(t).each(function(e,t){t.length>0&&(result+="<p>"+t+"</p>")}),result}}];genericColums=e.get("api/table/colum_defs","",function(e){const n=e.col_defs.length;for(let r=0;r<n;r++)t.push({targets:[parseInt(e.col_defs[r].target)],data:e.col_defs[r].csv_name,visible:!1,searchable:!0})}).done(function(){R(t)})}function B(){e("#requirement_tag_field").tokenfield({autocomplete:{source:s,delay:100},showAutocompleteOnFocus:!0}),e("#requirement_modal").on("hidden.bs.modal",function(t){e("#requirement_tag_field").val(""),e("#requirement_tag_field-tokenfield").val("")}),e("#add_formalization").click(function(){requirement_modal_content=e(".modal-content"),requirement_modal_content.LoadingOverlay("show"),req_id=e("#requirement_id").val(),e.post("api/req/new_formalization",{id:req_id},function(t){requirement_modal_content.LoadingOverlay("hide",!0),!1===t.success?alert(t.errormsg):e("#formalization_accordion").append(t.html)}).done(function(){z(),k(),S(),T(),E()})}),e("#add_gussed_formalization").click(function(){D()}),z()}function E(){e.get("api/logs/get","",function(t){e("#log_textarea").html(t)}).done(function(){e(".req_direct_link").click(function(){L(function(t){let n=-1;return e("#requirements_table").DataTable().column(2).data().filter(function(e,r){return e===t&&(n=r,!0)}),n}(e(this).data("rid")))}),e("#log_textarea").scrollTop(1e3)})}e(document).ready(function(){e.get("api/meta/get","",function(e){h=e.tag_colors}),M(),B(),E()})}).call(this,n(3))}});