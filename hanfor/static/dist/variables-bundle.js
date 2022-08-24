(()=>{var e,a={6052:(e,a,t)=>{var n=t(9755);t(1388);const{Modal:r}=t(4712);t(3333),t(6099),t(2993),t(3889),t(944),t(7312),t(2106),t(9570),t(7175);let o=t(5759),l=["CONST","ENUM_INT","ENUM_REAL"],i=[":AND:",":OR:",":NOT:",":COL_INDEX_01:",":COL_INDEX_02:",":COL_INDEX_03:",":COL_INDEX_04:"],s=sessionStorage.getItem("var_search_string"),c=[];const{SearchNode:u}=t(3024);let _,m=[!0,!0,!0,!0,!0],v=JSON.parse(search_query);function d(){s=n("#search_bar").val().trim(),sessionStorage.setItem("var_search_string",s),_=u.fromQuery(s)}function p(e,a=!1){let t=n("body");t.LoadingOverlay("show");let r=n("#multi-change-type-input").val().trim(),o=[];e.rows({selected:!0}).every((function(){let e=this.data();o.push(e.name)})),n.post("api/var/multi_update",{change_type:r,selected_vars:JSON.stringify(o),del:a},(function(e){t.LoadingOverlay("hide",!0),!1===e.success?alert(e.errormsg):location.reload()}))}function h(){n(".requirement_var_group").each((function(){n(this).hide()})),n(".formalization_card").each((function(){const e=n(this).attr("title"),a=n("#requirement_scope"+e).val(),t=n("#requirement_pattern"+e).val();let r=n("#requirement_var_group_p"+e),o=n("#requirement_var_group_q"+e),l=n("#requirement_var_group_r"+e),i=n("#requirement_var_group_s"+e),s=n("#requirement_var_group_t"+e),c=n("#requirement_var_group_u"+e),u=n("#requirement_var_group_v"+e);switch(a){case"BEFORE":case"AFTER":r.show();break;case"BETWEEN":case"AFTER_UNTIL":r.show(),o.show()}Object.keys(_PATTERNS[t].env).forEach((function(e){switch(e){case"R":l.show();break;case"S":i.show();break;case"T":s.show();break;case"U":c.show();break;case"V":u.show()}}))}))}function f(){n(".formalization_card").each((function(){const e=n(this).attr("title");let a="";const t=n("#requirement_scope"+e).find("option:selected").text().replace(/\s\s+/g," "),r=n("#requirement_pattern"+e).find("option:selected").text().replace(/\s\s+/g," ");"None"!==t&&"None"!==r&&(a=t+", "+r+".");let o=n("#formalization_var_p"+e).val(),l=n("#formalization_var_q"+e).val(),i=n("#formalization_var_r"+e).val(),s=n("#formalization_var_s"+e).val(),u=n("#formalization_var_t"+e).val(),_=n("#formalization_var_u"+e).val(),m=n("#formalization_var_v"+e).val();o.length>0&&(a=a.replace(/{P}/g,o)),l.length>0&&(a=a.replace(/{Q}/g,l)),i.length>0&&(a=a.replace(/{R}/g,i)),s.length>0&&(a=a.replace(/{S}/g,s)),u.length>0&&(a=a.replace(/{T}/g,u)),_.length>0&&(a=a.replace(/{U}/g,_)),m.length>0&&(a=a.replace(/{V}/g,m)),n("#current_formalization_textarea"+e).val(a);let v=n("#formalization_heading"+e);if(e in c)for(let a=0;a<c[e].length;a++)n("#formalization_var_"+c[e][a]+e).addClass("type-error"),v.addClass("type-error-head");else v.removeClass("type-error-head")})),n("#variable_constraint_updated").val("true")}function g(){n(".formalization_selector").change((function(){h(),f()})),n(".reqirement-variable, .req_var_type").change((function(){f()})),n(".delete_formalization").bootstrapConfirmButton({onConfirm:function(){!function(e){let a=n(".modal-content");a.LoadingOverlay("show");const t=n("#variable_name").val();n.post("api/var/del_constraint",{name:t,constraint_id:e},(function(e){a.LoadingOverlay("hide",!0),!1===e.success?alert(e.errormsg):n("#formalization_accordion").html(e.html)})).done((function(){h(),f(),g()}))}(n(this).attr("name"))}})}function b(e){!0===e?n("#variable_value_form_group").hide():n("#variable_value_form_group").show()}function y(e=!1){!0===e?n("#variable_belongs_to_form_group").hide():n("#variable_belongs_to_form_group").show()}function w(e=!1){!0===e?n(".enum-controls").hide():n(".enum-controls").show()}function O(e){let a=n("#variables_table").DataTable().row(e).data(),t=n(".modal-content");b(!0),w(!0),y(!0),r.getOrCreateInstance(document.getElementById("variable_modal")).show(),n("#modal_associated_row_index").val(e),n("#variable_name_old").val(a.name),n("#variable_type_old").val(a.type),n("#occurences").val(a.used_by),n("#variable_modal_title").html("Variable: "+a.name),n("#variable_name").val(a.name);let o=n("#variable_type"),i=n("#variable_value"),s=n("#variable_value_old"),u=n("#belongs_to_enum"),_=n("#belongs_to_enum_old"),m=n("#enumerators");var v;o.val(a.type),i.val(""),s.val(""),u.val(""),_.val(""),m.html(""),"CONST"!==a.type&&"ENUMERATOR_INT"!==a.type&&"ENUMERATOR_REAL"!==a.type||(b(),i.val(a.const_val),s.val(a.const_val)),"ENUMERATOR_INT"!==a.type&&"ENUMERATOR_REAL"!==a.type||(y(),u.val(a.belongs_to_enum),_.val(a.belongs_to_enum)),"ENUM_REAL"!==a.type&&"ENUM_INT"!==a.type||(w(),v=a.name,n.post("api/var/get_enumerators",{name:v},(function(e){!1===e.success?alert(e.errormsg):n.each(e.enumerators,(function(e,a){N(a[0].substr(v.length+1),a[1])}))})).done((function(){h(),f(),g()}))),o.autocomplete({minLength:0,source:l}).on("focus",(function(){n(this).keydown()})),function(e){n.post("api/var/get_constraints_html",{name:e},(function(e){!1===e.success?alert(e.errormsg):(c=e.type_inference_errors,n("#formalization_accordion").html(e.html))})).done((function(){h(),f(),g()}))}(a.name),t.LoadingOverlay("hide")}function N(e,a){const t=`\n        <div class="input-group enumerator-input">\n            <span class="input-group-prepend input-group-text">Name</span>\n            <input class="form-control enum_name_input" type="text" value="${e}">\n            <span class="input-group-prepend input-group-text">Value</span>\n            <input class="form-control enum_value_input" type="number" step="any" value="${a}">\n            <buttton type="button" class="btn btn-danger input-group-append del_enum" data-name="${e}">Delete</buttton>\n        </div>`;n("#enumerators").append(t)}function E(){const e=n("#new_variable_type").val();let a=n("#new_variable_const_input");"CONST"===e?a.show():a.hide()}n(document).ready((function(){let e=n("#variables_table").DataTable({paging:!0,stateSave:!0,select:{style:"os",selector:"td:first-child"},pageLength:50,responsive:!0,lengthMenu:[[10,50,100,500,-1],[10,50,100,500,"All"]],dom:'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',ajax:"api/var/gets",deferRender:!0,columns:[{orderable:!1,className:"select-checkbox",targets:[0],data:null,defaultContent:""},{data:"name",targets:[1],render:function(e){return'<a class="modal-opener" href="#">'+e+"</span></br>"}},{data:"type",targets:[2],render:function(e,a,t){return null!==e&&l.indexOf(e)<=-1&&l.push(e),null!==e&&"CONST"===e&&(e=e+" ("+t.const_val+")"),e}},{data:"used_by",targets:[3],render:function(e,a,t){let r="",o="";return n.inArray("Type_inference_error",t.tags)>-1&&(r+='<span class="badge bg-danger"><a href="#" class="variable_link" data-name="'+t.name+'" >Type-error in Constraint</a></span> '),n(e).each((function(e,a){if(a.length>0){let e=function(e){let a=null,t=/^(Constraint_)(.*)(_[0-9]+$)/gm.exec(e);return null!==t&&(a=t[2]),a}(a);null!==e?r+='<span class="badge bg-success"><a href="#" class="variable_link" data-name="'+e+'" >'+a+"</a></span> ":(r+='<span class="badge bg-info"><a href="./?command=search&col=2&q=%5C%22'+a+'%5C%22" target="_blank">'+a+"</a></span> ",o.length>0?o+="%3AOR%3A%5C%22"+a+"%5C%22":o+="?command=search&col=2&q=%5C%22"+a+"%5C%22")}})),r.length<1?r+='<span class="badge bg-warning"><a href="#">Not used</a></span></br>':e.length>1&&(r+='<span class="badge bg-info" style="background-color: #4275d8"><a href="./'+o+'" target="_blank">Show all</a></span> '),r}},{data:"script_results",targets:[4],render:function(e){return e}},{data:"used_by",targets:[5],visible:!1,searchable:!1,render:function(e){let a="";return n(e).each((function(e,t){t.length>0&&(a.length>1&&(a+=", "),a+=t)})),a}}],infoCallback:function(e,a,t,r,o){let l=this.api().page.info();n("#clear-all-filters-text").html("Showing "+o+"/"+l.recordsTotal+". Clear all.");let i="Showing "+a+" to "+t+" of "+o+" entries";return i+=" (filtered from "+l.recordsTotal+" total entries).",i},initComplete:function(){n("#search_bar").val(s),n(".variable_link").click((function(e){e.preventDefault(),O(function(e){let a=n("#variables_table").DataTable(),t=-1;return a.row((function(a,n){n.name===e&&(t=a)})),t}(n(this).data("name")))})),o.process_url_query(v),d(),n.fn.dataTable.ext.search.push((function(e,a){return function(e){return _.evaluate(e,m)}(a)})),this.api().draw()}});e.column(4).visible(!0),e.column(5).visible(!1),new n.fn.dataTable.ColReorder(e,{});let a=n("#search_bar");new Awesomplete(a[0],{filter:function(e,a){let t=!1;return(a.split(":").length-1)%2==1&&(t=Awesomplete.FILTER_CONTAINS(e,a.match(/[^:]*$/)[0])),t},item:function(e,a){return Awesomplete.ITEM(e,a.match(/(:)([\S]*$)/)[2])},replace:function(e){const a=this.input.value.match(/(.*)(:(?!.*:).*$)/)[1];this.input.value=a+e},list:i,minChars:1,autoFirst:!0}),a.keypress((function(a){13===a.which&&(d(),e.draw())})),n("#variables_table  tbody").on("click","a.modal-opener",(function(a){a.preventDefault(),O(e.row(n(a.target).parent()).index())})),n("#save_variable_modal").click((function(){!function(e){let a=n(".modal-content");a.LoadingOverlay("show");const t=n("#variable_name").val(),r=n("#variable_name_old").val(),o=n("#variable_type").val(),i=n("#variable_type_old").val(),s=parseInt(n("#modal_associated_row_index").val()),c=n("#occurences").val(),u=n("#variable_value").val(),_=n("#variable_value_old").val(),m=n("#variable_constraint_updated").val(),v=n("#belongs_to_enum").val(),d=n("#belongs_to_enum_old").val();let p={};n(".formalization_card").each((function(){let e={};e.id=n(this).attr("title"),n(this).find("select").each((function(){n(this).hasClass("scope_selector")&&(e.scope=n(this).val()),n(this).hasClass("pattern_selector")&&(e.pattern=n(this).val())})),e.expression_mapping={},n(this).find("textarea.reqirement-variable").each((function(){""!==n(this).attr("title")&&(e.expression_mapping[n(this).attr("title")]=n(this).val())})),p[e.id]=e})),null!==o&&l.indexOf(o)<=-1&&l.push(o);let h=[];"ENUM_INT"!==o&&"ENUM_REAL"!==o||n(".enumerator-input").each((function(){let e=n(this).find(".enum_name_input").val(),a=n(this).find(".enum_value_input").val();h.push([e,a])})),n.post("api/var/update",{name:t,name_old:r,type:o,const_val:u,const_val_old:_,type_old:i,occurrences:c,constraints:JSON.stringify(p),updated_constraints:m,enumerators:JSON.stringify(h),belongs_to_enum:v,belongs_to_enum_old:d},(function(t){a.LoadingOverlay("hide",!0),!1===t.success?alert(t.errormsg):t.rebuild_table?location.reload():(e.row(s).data(t.data).draw(),n("#variable_modal").modal("hide"))}))}(e)})),n("#variable_type").on("keyup change autocompleteclose",(function(){"CONST"===n(this).val()?b():b(!0),"ENUMERATOR_INT"===n(this).val()||"ENUMERATOR_REAL"===n(this).val()?(y(),b()):y(!0),"ENUM_INT"===n(this).val()||"ENUM_REAL"===n(this).val()?w():w(!0)})),n(".import_link").on("click",(function(){!function(e,a){let t=n("#variable_import_modal");n("#variable_import_sess_name").val(e),n("#variable_import_sess_revision").val(a),n("#variable_import_modal_title").html("Import from Session: "+e+" at: "+a),r.getOrCreateInstance(t).show(),t.LoadingOverlay("show"),n.post("api/var/var_import_info",{sess_name:e,sess_revision:a},(function(e){t.LoadingOverlay("hide",!0),!1===e.success?alert(e.errormsg):(n("#import_tot_number").html("Total:\t"+e.tot_vars+" Variables."),n("#import_new_number").html("New:\t"+e.new_vars+" Variables."))}))}(n(this).attr("data-name"),n(this).attr("data-revision"))})),n("#start_variable_import_session").click((function(){!function(){let e=n("#variable_import_modal"),a=n("#variable_import_sess_name").val(),t=n("#variable_import_sess_revision").val();e.LoadingOverlay("show"),n.post("api/var/start_import_session",{sess_name:a,sess_revision:t},(function(a){e.LoadingOverlay("hide",!0),!1===a.success?alert(a.errormsg):window.location.href=base_url+"variable_import/"+a.session_id}))}()})),n(".select-all-button").on("click",(function(){n(this).hasClass("btn-secondary")?e.rows({page:"current"}).select():e.rows({page:"current"}).deselect(),n(".select-all-button").toggleClass("btn-secondary btn-primary")})),e.on("user-select",(function(){let e=n(".select-all-button");e.removeClass("btn-primary"),e.addClass("btn-secondary ")})),n("#multi-change-type-input").autocomplete({minLength:0,source:l,delay:100}).on("focus",(function(){n(this).keydown()})).val(""),n(".apply-multi-edit").click((function(){p(e)})),n("body").on("click",".delete_button",(function(){const a=n(this);void 0===a.data("html")?(a.outerWidth(a.outerWidth()).data("html",a.html()).html("Do it!"),setTimeout((function(){a.html(a.data("html")).removeData("html").outerWidth("")}),2e3)):(a.html(a.data("html")).removeData("html").outerWidth(""),p(e,!0))})),n("#add_constraint").click((function(){!function(){let e=n(".modal-content");e.LoadingOverlay("show");const a=n("#variable_name").val();n.post("api/var/new_constraint",{name:a},(function(a){e.LoadingOverlay("hide",!0),!1===a.success?alert(a.errormsg):n("#formalization_accordion").html(a.html)})).done((function(){h(),f(),g()}))}()})),n("#save_new_variable_modal").click((function(){!function(){const e=n("#new_variable_name").val(),a=n("#new_variable_type").val(),t=n("#new_variable_const_value").val();n.post("api/var/add_new_variable",{name:e,type:a,value:t},(function(e){!1===e.success?alert(e.errormsg):location.reload()}))}()})),n("#add_enumerator").click((function(){N("")})),n("#enumerators").on("click",".del_enum",(function(){const e=n(this).attr("data-name"),a=n("#variable_name_old").val();let t=n(this).parent(".enumerator-input");0===e.length?t.remove():function(e,a,t){let r=n("#variable_modal");r.LoadingOverlay("show"),n.post("api/var/del_var",{name:e+"_"+a},(function(e){r.LoadingOverlay("hide",!0),!1===e.success?alert(e.errormsg):t.remove()}))}(a,e,t)})).on("paste",".enum_name_input",(function(e){let a=e.originalEvent.clipboardData.getData("text");if(function(e){const a=e.match(/[^\r\n]+/g);if(a.length<=0)return!1;for(const e of a){const a=e.match(/[^\t]+/g);if(2!==a.length)return!1;if(isNaN(a[1]))return!1}return!0}(a)){console.log("has smart input form");const t=function(e){const a=e.match(/[^\r\n]+/g);let t=[];for(const e of a){const a=e.match(/[^\t]+/g);t.push([a[0],a[1]])}return t}(a);console.log(t);for(const e of t)N(e[0],e[1]);e.preventDefault()}})),n("#generate_req").click((function(){n("#generate_req_form").submit()})),n(".clear-all-filters").click((function(){n("#search_bar").val("").effect("highlight",{color:"green"},500),d(),e.draw()})),n("#variable_new_vaiable_modal")[0].addEventListener("show.bs.modal",(function(){E()})),n("#new_variable_type").on("change",(function(){E()}))}))}},t={};function n(e){var r=t[e];if(void 0!==r)return r.exports;var o=t[e]={id:e,exports:{}};return a[e].call(o.exports,o,o.exports,n),o.exports}n.m=a,e=[],n.O=(a,t,r,o)=>{if(!t){var l=1/0;for(u=0;u<e.length;u++){for(var[t,r,o]=e[u],i=!0,s=0;s<t.length;s++)(!1&o||l>=o)&&Object.keys(n.O).every((e=>n.O[e](t[s])))?t.splice(s--,1):(i=!1,o<l&&(l=o));if(i){e.splice(u--,1);var c=r();void 0!==c&&(a=c)}}return a}o=o||0;for(var u=e.length;u>0&&e[u-1][2]>o;u--)e[u]=e[u-1];e[u]=[t,r,o]},n.n=e=>{var a=e&&e.__esModule?()=>e.default:()=>e;return n.d(a,{a}),a},n.d=(e,a)=>{for(var t in a)n.o(a,t)&&!n.o(e,t)&&Object.defineProperty(e,t,{enumerable:!0,get:a[t]})},n.o=(e,a)=>Object.prototype.hasOwnProperty.call(e,a),n.r=e=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},n.j=565,(()=>{var e={565:0};n.O.j=a=>0===e[a];var a=(a,t)=>{var r,o,[l,i,s]=t,c=0;if(l.some((a=>0!==e[a]))){for(r in i)n.o(i,r)&&(n.m[r]=i[r]);if(s)var u=s(n)}for(a&&a(t);c<l.length;c++)o=l[c],n.o(e,o)&&e[o]&&e[o][0](),e[o]=0;return n.O(u)},t=self.webpackChunkhanfor=self.webpackChunkhanfor||[];t.forEach(a.bind(null,0)),t.push=a.bind(null,t.push.bind(t))})(),n.nc=void 0;var r=n.O(void 0,[351],(()=>n(6052)));r=n.O(r)})();