(()=>{var e,t={1521:(e,t,a)=>{var n=a(4692);a(7081);const{Collapse:r,Modal:o}=a(9875);a(5194),a(6628),a(97),a(7776),a(4371),a(5219),a(9145),a(1453),a(8131);let i=a(879);const s=a(9692),{SearchNode:l}=a(1108),{init_simulator_tab:c}=a(985);let u=[];t.B=u;const{Textcomplete:d}=a(6e3),{TextareaEditor:f}=a(9787);let p,m,_=a(8357),g=new _([],{}),h=["","has_formalization"],v=["","Todo","Review","Done"],b=[":AND:",":OR:",":NOT:",":COL_INDEX_01:",":COL_INDEX_02:",":COL_INDEX_03:",":COL_INDEX_04:",":COL_INDEX_05:",":COL_INDEX_06:",":COL_INDEX_07:"],y=[""],q=[""],w=[],x=[!0,!0,!0,!0,!0,!0],O=[],k=JSON.parse(search_query),C={},T=[],S=sessionStorage.getItem("req_search_string"),L=sessionStorage.getItem("filter_status_string"),z=sessionStorage.getItem("filter_tag_string"),N=sessionStorage.getItem("filter_type_string");function E(){S=n("#search_bar").val().trim(),sessionStorage.setItem("req_search_string",S),p=l.fromQuery(S)}function I(){function e(e,t,a){return t.length>0&&(e.length>0&&(e=e.concat([":AND:"])),e=e.concat(function(e){return["("].concat(e,[")"])}(l.awesomeQuerySplitt0r(t,a)))),e}O=[],L=n("#status-filter-input").val(),z=n("#tag-filter-input").val(),N=n("#type-filter-input").val(),sessionStorage.setItem("filter_status_string",L),sessionStorage.setItem("filter_tag_string",z),sessionStorage.setItem("filter_type_string",N),O=e(O,N,4),O=e(O,z,5),O=e(O,L,6),m=l.searchArrayToTree(O)}function D(){let e=n("#requirements_table").DataTable(),t=[];n.each(e.columns().visible(),(function(e,a){!1===a?(n("#col_toggle_button_"+e).removeClass("btn-info").addClass("btn-secondary"),t.push(!1)):(n("#col_toggle_button_"+e).removeClass("btn-secondary").addClass("btn-info"),t.push(!0))})),x=t}function j(e){let t=[];return e.rows({selected:!0}).every((function(){let e=this.data();t.push(e.id)})),t}function R(){n.get("api/logs/get","",(function(e){n("#log_textarea").html(e)})).done((function(){n(".req_direct_link").click((function(){A(function(e){let t=n("#requirements_table").DataTable(),a=-1;return t.data().filter((function(t,n){return String(t.id)===String(e)&&(a=n,!0)})),a}(n(this).data("rid")))})),n("#log_textarea").scrollTop(1e5)}))}function A(e){if(-1===e)return void alert("Requirement not found.");H();let t=n("#requirements_table").DataTable().row(e).data(),a=n(".modal-content");o.getOrCreateInstance("#requirement_modal").show(),a.LoadingOverlay("show"),n("#formalization_accordion").html(""),n("#requirement_tag_field").data("bs.tokenfield").$input.autocomplete({source:h}),n.get("api/req/get",{id:t.id,row_idx:e},(function(t){if(!1===t.success)return void alert("Could Not load the Requirement: "+t.errormsg);n("#requirement_id").val(t.id),n("#modal_associated_row_index").val(e),q=t.available_vars,q=q.concat(t.additional_static_available_vars),T=t.type_inference_errors,g=new _(q,{shouldSort:!0,threshold:.6,location:0,distance:100,maxPatternLength:12,minMatchCharLength:1,keys:[]}),n("#requirement_modal_title").html(t.id+": "+t.type),n("#description_textarea").text(t.desc).change(),n("#add_guess_description").text(t.desc).change(),n("#formalization_accordion").html(t.formalizations_html),n("#requirement_scope").val(t.scope),n("#requirement_pattern").val(t.pattern),n("#tags_comments_table").find("tr:gt(0)").remove(),n("#requirement_tag_field").tokenfield("setTokens",t.tags),n("#tags_comments_table tr:gt(0)").each((function(){let e=n(this).find("td:eq(0)").text();n(this).find("textarea:eq(0)").val(t.tags_comments[e])})),n("#requirement_status").val(t.status);let a=n("#csv_content_accordion");a.html("");let r=t.csv_data;for(const e in r)if(r.hasOwnProperty(e)){const t=r[e];a.append("<p><strong>"+e+":</strong>"+t+"</p>")}let o=n("#show_revision_diff");n.isEmptyObject(t.revision_diff)?o.hide():o.show();let i=n("#revision_diff_accordion");i.html("");let s=t.revision_diff;for(const e in s)if(s.hasOwnProperty(e)){const t=s[e];i.append("<p><strong>"+e+":</strong><pre>"+t+"</pre></p>")}let l=n("#used_variables_accordion");l.html(""),t.vars.forEach((function(e){let t="?command=search&col=1&q=%5C%22"+e+"%5C%22";l.append('<span class="badge bg-info"><a href="./variables'+t+'" target="_blank">'+e+"</a></span>&numsp;")}))})).done((function(){B(),P(),J(),n("#requirement_modal").data({unsaved_changes:!1,updated_formalization:!1}),a.LoadingOverlay("hide",!0)}))}function P(){n(".reqirement-variable").each((function(){$(this)}))}function $(e){const t=new d(new f(e),[{match:/(|\s|[!=&\|>]+)(\w+)$/,index:2,search:function(e,t,a){let n=function(e){return g.search(e)}(e),r=[];for(let e=0;e<Math.min(10,n.length);e++)r.push(q[n[e].refIndex]);t(r)},replace:function(e){return"$1"+e+" "}}],{dropdown:{className:"dropdown-menu textcomplete-dropdown",maxCount:10,style:{display:"none",position:"absolute",zIndex:"9999"},item:{className:"dropdown-item",activeClassName:"dropdown-item active"}}});n(document).on("click",(function(e){t!==e.target&&t.hide()}))}function J(){n(".formalization_card").each((function(){const e=n(this).attr("title");let t="",a=n("#current_formalization_textarea"+e);const r=n("#requirement_scope"+e).find("option:selected").text().replace(/\s\s+/g," "),o=n("#requirement_pattern"+e).find("option:selected").text().replace(/\s\s+/g," ");"None"!==r&&"None"!==o&&(t=r+", "+o+".");let i=n("#formalization_var_p"+e).val(),l=n("#formalization_var_q"+e).val(),c=n("#formalization_var_r"+e).val(),u=n("#formalization_var_s"+e).val(),d=n("#formalization_var_t"+e).val(),f=n("#formalization_var_u"+e).val(),p=n("#formalization_var_v"+e).val();i.length>0&&(t=t.replace(/{P}/g,M(i))),l.length>0&&(t=t.replace(/{Q}/g,M(l))),c.length>0&&(t=t.replace(/{R}/g,M(c))),u.length>0&&(t=t.replace(/{S}/g,M(u))),d.length>0&&(t=t.replace(/{T}/g,M(d))),f.length>0&&(t=t.replace(/{U}/g,M(f))),p.length>0&&(t=t.replace(/{V}/g,M(p))),a.html(t),s.update(a)})),n("#requirement_modal").data({unsaved_changes:!0,updated_formalization:!0})}function M(e){let t="";return e.split(/([\s&<>!()=:\[\]{}\-|+*,])/g).forEach((function(e){q.includes(e)?t+='<a href="./variables?command=search&col=1&q=%5C%22'+e+'%5C%22" target="_blank"  title="Go to declaration of '+e+'" class="alert-link">'+e+"</a>":t+=i.escapeHtml(e)})),t}function B(){n(".requirement_var_group").each((function(){n(this).hide(),n(this).removeClass("type-error")})),n(".formalization_card").each((function(){const e=n(this).attr("title"),t=n("#requirement_scope"+e).val(),a=n("#requirement_pattern"+e).val();let r=n("#formalization_heading"+e),o=n("#requirement_var_group_p"+e),i=n("#requirement_var_group_q"+e),s=n("#requirement_var_group_r"+e),l=n("#requirement_var_group_s"+e),c=n("#requirement_var_group_t"+e),u=n("#requirement_var_group_u"+e),d=n("#requirement_var_group_v"+e);if(e in T)for(let t=0;t<T[e].length;t++)n("#formalization_var_"+T[e][t]+e).addClass("type-error"),r.addClass("type-error-head");else r.removeClass("type-error-head");switch(t){case"BEFORE":case"AFTER":o.show();break;case"BETWEEN":case"AFTER_UNTIL":o.show(),i.show()}Object.keys(_PATTERNS[a].env).forEach((function(e){switch(e){case"R":s.show();break;case"S":l.show();break;case"T":c.show();break;case"U":u.show();break;case"V":d.show()}}))}))}function H(){n.ajax({type:"GET",url:"api/tags/"}).done((function(e){h=[];for(let t of e)h.push(t.name),C[t.name]=t.color})).fail((function(e,t,a){alert(a+"\n\n"+e.responseText)}))}function X(e=!1){let t=n("#report_query_textarea"),a=n("#report_results_textarea"),r=n("#report_modal_title"),i=n("#report_name"),s="",l="",c="",u=-1;n("#report_modal"),!1!==e&&(u=e.attr("data-id"),s=w[u].queries,l=w[u].results,c=w[u].name),t.val(s).change(),a.val(l).change(),i.val(c).change(),r.html(c),n("#save_report").attr("data-id",u),o.getOrCreateInstance(document.querySelector("#report_modal")).show()}function F(){n.get("api/report/get",{},(function(e){if(!1===e.success)alert(e.errormsg);else{let t="";w=e.data,n.each(e.data,(function(e,a){t+=`<div class="card border-primary">\n                              <div class="card-body">\n                                <h5 class="card-title">${a.name}</h5>\n                                <h6 class="card-subtitle mb-2 text-muted">Query</h6>\n                                <p class="card-text report-results">${a.queries}</p>\n                                <h6 class="card-subtitle mb-2 text-muted">Matches for queries</h6>\n                                <p class="card-text report-results">${a.results}</p>\n                                <a href="#" class="card-link open-report" data-id="${e}">\n                                    Edit (reevaluate) Report.\n                                </a>\n                                <a href="#" class="card-link delete-report" data-id="${e}">Delete Report.</a>\n                              </div>\n                            </div>`})),n("#available_reports").html(t)}}))}n(document).ready((function(){H(),function(){let e=n("#search_bar");new Awesomplete(e[0],{filter:function(e,t){let a=!1;return(t.split(":").length-1)%2==1&&(a=Awesomplete.FILTER_CONTAINS(e,t.match(/[^:]*$/)[0])),a},item:function(e,t){return Awesomplete.ITEM(e,t.match(/(:)([\S]*$)/)[2])},replace:function(e){const t=this.input.value.match(/(.*)(:(?!.*:).*$)/)[1];this.input.value=t+e},list:b,minChars:1,autoFirst:!0})}(),function(){let e=[{orderable:!1,className:"select-checkbox",targets:[0],data:null,defaultContent:""},{targets:[1],data:"pos"},{targets:[2],data:"id",render:function(e){return'<a href="#">'+i.escapeHtml(e)+"</a>"}},{targets:[3],data:"desc",render:function(e){return'<div class="white-space-pre">'+i.escapeHtml(e)+"</div>"}},{targets:[4],data:"type",render:function(e){return y.indexOf(e)<=-1&&y.push(e),i.escapeHtml(e)}},{targets:[5],data:"tags",render:function(e,t,a){let r="";return n(e).each((function(e,t){var a;t.length>0&&(r+='<span class="badge" style="background-color: '+(a=t,(C.hasOwnProperty(a)?C[a]:"var(--bs-info)")+'">')+i.escapeHtml(t)+"</span></br> ")})),r}},{targets:[6],data:"status",render:function(e){return'<span class="badge bg-info">'+e+"</span></br>"}},{targets:[7],data:"formal",render:function(e,t,a){let r="";return a.formal.length>0&&n(e).each((function(e,t){t.length>0&&(r+='<div class="white-space-pre">'+i.escapeHtml(t)+"</div>")})),r}}];n.get("api/table/colum_defs","",(function(t){const a=t.col_defs.length;for(let n=0;n<a;n++)e.push({targets:[parseInt(t.col_defs[n].target)],data:t.col_defs[n].csv_name,visible:!1,searchable:!0})})).done((function(){!function(e){let t=n("#requirements_table").DataTable({language:{emptyTable:"Loading data."},paging:!0,stateSave:!0,select:{style:"os",selector:"td:first-child"},order:[[1,"asc"]],pageLength:50,lengthMenu:[[10,50,100,500,-1],[10,50,100,500,"All"]],dom:'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',ajax:"api/req/gets",deferRender:!0,columnDefs:e,createdRow:function(e,t){"Heading"===t.type&&n(e).addClass("bg-primary"),"Information"===t.type&&n(e).addClass("table-info"),"Requirement"===t.type&&n(e).addClass("table-warning"),"not set"===t.type&&n(e).addClass("table-light")},infoCallback:function(e,t,a,r,o){let i=this.api().page.info();n("#clear-all-filters-text").html("Showing "+o+"/"+i.recordsTotal+". Clear all.");let s="Showing "+t+" to "+a+" of "+o+" entries";return s+=" (filtered from "+i.recordsTotal+" total entries).",s},initComplete:function(){n("#search_bar").val(S),n("#type-filter-input").val(N),n("#tag-filter-input").val(z),n("#status-filter-input").val(L);let e=this.api();!function(e){n("#requirements_table").find("tbody").on("click","a",(function(t){t.preventDefault(),A(e.row(n(this).closest("tr")).index())}))}(e),function(e){e.columns().every((function(t){t>0&&e.column(t).header().append(" ("+t+")")})),n("#save_requirement_modal").click((function(){!function(e){let t=n(".modal-content");t.LoadingOverlay("show");const a=n("#requirement_id").val(),r=n("#requirement_status").val(),i=n("#requirement_modal").data("updated_formalization"),s=parseInt(n("#modal_associated_row_index").val());let l={};n(".formalization_card").each((function(){let e={};e.id=n(this).attr("title"),n(this).find("select").each((function(){n(this).hasClass("scope_selector")&&(e.scope=n(this).val()),n(this).hasClass("pattern_selector")&&(e.pattern=n(this).val())})),e.expression_mapping={},n(this).find("textarea.reqirement-variable").each((function(){""!==n(this).attr("title")&&(e.expression_mapping[n(this).attr("title")]=n(this).val())})),l[e.id]=e}));let c=new Map;n("#tags_comments_table tr:gt(0)").each((function(){let e=n(this).find("td:eq(0)").text(),t=n(this).find("textarea:eq(0)").val();c.set(e,t)})),n.post("api/req/update",{id:a,row_idx:s,update_formalization:i,tags:JSON.stringify(Object.fromEntries(c)),status:r,formalizations:JSON.stringify(l)},(function(a){if(t.LoadingOverlay("hide",!0),!1===a.success)alert(a.errormsg);else{e.row(s).data(a),n("#requirement_modal").data("unsaved_changes",!1);const t=document.querySelector("#requirement_modal");o.getOrCreateInstance(t).hide()}})).done((function(){R()}))}(e)})),n("#search_bar").keypress((function(t){13===t.which&&(E(),e.draw())})),n("#type-filter-input").autocomplete({minLength:0,source:y,delay:100}),n("#status-filter-input").autocomplete({minLength:0,source:v,delay:100}),n("#tag-filter-input").autocomplete({minLength:0,source:h,delay:100}),n("#tag-filter-input, #status-filter-input, #type-filter-input").on("focus",(function(){n(this).keydown()})).on("keypress",(function(t){13===t.which&&(I(),e.draw())})),n("#table-filter-toggle").click((function(){n("#tag-filter-input").autocomplete({source:h}),n("#type-filter-input").autocomplete({source:y})})),n(".clear-all-filters").click((function(){n("#status-filter-input").val("").effect("highlight",{color:"green"},500),n("#tag-filter-input").val("").effect("highlight",{color:"green"},500),n("#type-filter-input").val("").effect("highlight",{color:"green"},500),n("#search_bar").val("").effect("highlight",{color:"green"},500),I(),E(),e.draw()})),n("#gen-req-from-selection").click((function(){let t=[];e.rows({search:"applied"}).every((function(){let e=this.data();t.push(e.id)})),n("#selected_requirement_ids").val(JSON.stringify(t)),n("#generate_req_form").submit()})),n("#gen-csv-from-selection").click((function(){let t=[];e.rows({search:"applied"}).every((function(){let e=this.data();t.push(e.id)})),n("#selected_csv_requirement_ids").val(JSON.stringify(t)),n("#generate_csv_form").submit()})),n("#gen-xls-from-selection").click((function(){let t=[];e.rows({search:"applied"}).every((function(){let e=this.data();t.push(e.id)})),n("#selected_xls_requirement_ids").val(JSON.stringify(t)),n("#generate_xls_form").submit()})),n(".column-toggle-button").on("click",(function(t){t.preventDefault();let a=e.column(n(this).attr("data-column"));a.visible(!a.visible()),D()})),n(".reset-column-toggle").on("click",(function(t){t.preventDefault(),e.columns(".default-col").visible(!0),e.columns(".extra-col").visible(!1),D()})),D(),n(".select-all-button").on("click",(function(){n(this).hasClass("btn-secondary")?e.rows({page:"current"}).select():e.rows({page:"current"}).deselect(),n(".select-all-button").toggleClass("btn-secondary btn-primary")})),e.on("user-select",(function(){let e=n(".select-all-button");e.removeClass("btn-primary"),e.addClass("btn-secondary ")})),n("#multi-add-tag-input, #multi-remove-tag-input").autocomplete({minLength:0,source:h,delay:100}).on("focus",(function(){n(this).keydown()})).val(""),n("#multi-set-status-input").autocomplete({minLength:0,source:v,delay:100}).on("focus",(function(){n(this).keydown()})).val(""),n(".apply-multi-edit").click((function(){!function(e){let t=n("body");t.LoadingOverlay("show");let a=n("#multi-add-tag-input").val().trim(),r=n("#multi-remove-tag-input").val().trim(),o=n("#multi-set-status-input").val().trim(),i=j(e);n.post("api/req/multi_update",{add_tag:a,remove_tag:r,set_status:o,selected_ids:JSON.stringify(i)},(function(e){t.LoadingOverlay("hide",!0),!1===e.success?alert(e.errormsg):location.reload()}))}(e)})),n(".add_top_guess_button").bootstrapConfirmButton({onConfirm:function(){!function(e){let t=n("body");t.LoadingOverlay("show");let a=j(e),r=n("#top_guess_append_mode").val();n.post("api/req/multi_add_top_guess",{selected_ids:JSON.stringify(a),insert_mode:r},(function(e){t.LoadingOverlay("hide",!0),!1===e.success?alert(e.errormsg):location.reload()}))}(e)}})}(e);for(const t of u)t(e);i.process_url_query(k),E(),I(),n.fn.dataTable.ext.search.push((function(e,t){return function(e){return p.evaluate(e,x)&&m.evaluate(e,x)}(t)})),this.api().draw()}});new n.fn.dataTable.ColReorder(t,{})}(e)}))}(),function(){let e=n("#requirement_modal");n("#requirement_tag_field").tokenfield({autocomplete:{source:h,delay:100},showAutocompleteOnFocus:!0}).change((function(){e.data("unsaved_changes",!0)})),n("#requirement_status").change((function(){n("#requirement_modal").data("unsaved_changes",!0)})),e[0].addEventListener("hide.bs.modal",(function(e){!function(e){!0===n("#requirement_modal").data("unsaved_changes")&&!0!==confirm("You have unsaved changes, do you really want to close?")&&e.preventDefault()}(e)})),n(document).keyup((function(e){if(n(".modal:visible").length&&27===e.keyCode){let e=n("input[type=text], textarea, select").filter(":focus");0===e.length?n("#requirement_guess_modal:visible").length?o.getOrCreateInstance("#requirement_guess_modal").hide():o.getOrCreateInstance("#requirement_modal").hide():e.each((function(){n(this).blur()}))}})),e.on("hidden.bs.modal",(function(){n("#requirement_tag_field").val(""),n("#requirement_tag_field-tokenfield").val("")})),n("#add_formalization").click((function(){!function(){let e=n(".modal-content");e.LoadingOverlay("show");const t=n("#requirement_id").val();n.post("api/req/new_formalization",{id:t},(function(t){if(e.LoadingOverlay("hide",!0),!1===t.success)alert(t.errormsg);else{let e=n(t.html);e.find(".reqirement-variable").each((function(){$(this)})),e.appendTo("#formalization_accordion")}})).done((function(){B(),J(),R()}))}()})),n("#add_gussed_formalization").click((function(){!function(){let e=n("#requirement_guess_modal"),t=n("#available_guesses_cards"),a=n(".modal-content"),r=n("#requirement_id").val();function i(e){let a='<div class="card">                    <div class="pl-1 pr-1">                        <p>'+e.string+'                        </p>                    </div>                    <button type="button" class="btn btn-success btn-sm add_guess"                            title="Add formalization"                            data-scope="'+e.scope+'"                            data-pattern="'+e.pattern+"\"                            data-mapping='"+JSON.stringify(e.mapping)+"'>                        <strong>+ Add this formalization +</strong>                    </button>                </div>";t.append(a)}new o(e,{keyboard:!1}),o.getOrCreateInstance(e).show(),a.LoadingOverlay("show"),t.html(""),n.post("api/req/get_available_guesses",{requirement_id:r},(function(e){if(!1===e.success)alert(e.errormsg);else for(let t=0;t<e.available_guesses.length;t++)i(e.available_guesses[t])})).done((function(){n(".add_guess").click((function(){!function(e,t,a){let r=n(".modal-content");r.LoadingOverlay("show");let o=n("#requirement_id").val();n.post("api/req/add_formalization_from_guess",{requirement_id:o,scope:e,pattern:t,mapping:JSON.stringify(a)},(function(e){r.LoadingOverlay("hide",!0),!1===e.success?alert(e.errormsg):n("#formalization_accordion").append(e.html)})).done((function(){B(),J(),P(),R()}))}(n(this).data("scope"),n(this).data("pattern"),n(this).data("mapping"))})),a.LoadingOverlay("hide",!0)}))}()})),n(".modal").on("hidden.bs.modal",(function(){n(".modal:visible").length?n("body").addClass("modal-open"):n("textarea").each((function(){s.destroy(n(this))}))})),n("#formalization_accordion").on("shown.bs.collapse",".card",(function(){n(this).find("textarea").each((function(){s(n(this)),s.update(n(this))}))})),B()}(),R(),function(){n("#add-new-report").click((function(){X()})),n("#eval_report").click((function(){!function(){let e=n("body");e.LoadingOverlay("show");const t=n("#report_query_textarea").val().split("\n");let a=n("#requirements_table").DataTable(),r="";const o=/^(:NAME:)(`(\w+)`)(.*)/;try{n.each(t,(function(e,t){let n=o.exec(t);null!=n&&(t=n[4],e=n[3]),p=l.fromQuery(t),a.draw();let i=a.page.info();r+=`"${e}":\t${i.recordsDisplay}\n`})),n("#report_results_textarea").val(r).change(),E(),a.draw()}catch(e){alert(e)}e.LoadingOverlay("hide",!0)}()})),n("#save_report").click((function(){!function(){let e=n("body");e.LoadingOverlay("show"),n.post("api/report/set",{report_querys:n("#report_query_textarea").val(),report_results:n("#report_results_textarea").val(),report_name:n("#report_name").val(),report_id:n("#save_report").attr("data-id")},(function(t){e.LoadingOverlay("hide",!0),!1===t.success&&alert(t.errormsg),F()}))}()}));let e=n("#available_reports");e.on("click",".open-report",(function(){X(n(this))})),e.on("click",".delete-report",(function(){var e;e=n(this).attr("data-id"),n.ajax({type:"DELETE",url:"api/report/delete",data:{report_id:e},success:function(e){!1===e.success&&alert(e.errormsg),F()}})})),n("#report_name").change((function(){n("#report_modal_title").html(n(this).val())})),F()}(),c();let e=n("body");n("body").bootstrapConfirmButton({selector:".delete_formalization",onConfirm:function(){!function(e,t){let a=n(".modal-content");a.LoadingOverlay("show");const r=n("#requirement_id").val();n.post("api/req/del_formalization",{requirement_id:r,formalization_id:e},(function(e){a.LoadingOverlay("hide",!0),!1===e.success?alert(e.errormsg):t.remove()})).done((function(){B(),J(),R()}))}(n(this).attr("name"),n(this).closest(".accordion-item"))}}),e.on("click",".delete_formalization1",(function(){bootstrapConfirmation({yesCallBack:function(){console.log("yes")},noCallBack:function(){console.log("no")},config:{closeIcon:!0,message:"This is an example.",title:"Example",no:{class:"btn btn-danger",text:"No"},yes:{class:"btn btn-success",text:"Yes"}}})})),e.on("change",".formalization_selector, .reqirement-variable, .req_var_type",(function(){J()})),e.on("change",".formalization_selector",(function(){B()})),document.getElementById("requirement_modal").addEventListener("shown.bs.modal",(function(){n(this).find("textarea").each((function(){s(n(this)),s.update(n(this))}))})),e.on("change focus","textarea",(function(){s(n(this)),s.update(n(this))})),n("#requirement_tag_field").on("tokenfield:createtoken",(function(e){let t=n(this).tokenfield("getTokens");for(const a of t)if(e.attrs.value===a.value)return!1})).on("tokenfield:createdtoken",(function(e){var t;t="<tr><td>"+e.attrs.value+"</td><td><textarea rows='1' class='form-control w-100' type='text'></textarea></td>",n("#tags_comments_table tbody").append(t)})).on("tokenfield:removedtoken",(function(e){n("#tags_comments_table tr:gt(0)").each((function(){let t=n(this);n(this).find("td:eq(0)").text()===e.attrs.value&&t.remove()}))}))}))},7943:(e,t,a)=>{var n=a(4692);let r=a(1521).B;function o(e){n("#ultimate-tab-create-filtered-btn").click((function(){let t=[];e.rows({search:"applied"}).every((function(){let e=this.data();t.push(e.id)})),i(n("#ultimate-tab-create-filtered-btn"),t)})),n("#ultimate-tab-create-selected-btn").click((function(){let t=[];e.rows({selected:!0}).every((function(){let e=this.data();t.push(e.id)})),i(n("#ultimate-tab-create-selected-btn"),t)}))}function i(e,t){let a=e.text();e.text("Processing Request");let r={selected_requirement_ids:JSON.stringify(t)};"all"===t&&(r={}),n.ajax({type:"POST",url:"api/tools/req_file",data:r}).done((function(r){let o=n("#ultimate-tab-configuration-select").val();n.ajax({type:"POST",url:"api/ultimate/job",data:JSON.stringify({configuration:o,req_file:r,req_ids:t})}).done((function(t){console.log(t.requestId),e.text(a)})).fail((function(e,t,a){alert(a+"\n\n"+e.responseText)}))})).fail((function(e,t,a){alert(a+"\n\n"+e.responseText)}))}n(document).ready((function(){r.push(o),n.ajax({type:"GET",url:"api/ultimate/version"}).done((function(e){if(""!==e.version){let t=n("#ultimate-tab-ultimate-status-img"),a=t.attr("src");t.attr("src",a.replace("/disconnected.svg","/connected.svg")),t.attr("title","Ultimate Api connected: "+e.version),n("#ultimate-tab-create-unfiltered-btn").prop("disabled",!1),n("#ultimate-tab-create-filtered-btn").prop("disabled",!1),n("#ultimate-tab-create-selected-btn").prop("disabled",!1)}else console.log("no ultimate connection found!")})).fail((function(e,t,a){alert(a+"\n\n"+e.responseText)})),n.ajax({type:"GET",url:"api/ultimate/configurations"}).done((function(e){let t=n("#ultimate-tab-configuration-select");t.empty();let a=Object.keys(e);for(let r=0;r<a.length;r++){let o=a[r];o+=" (Toolchain: "+e[a[r]].toolchain,o+=", User Settings: "+e[a[r]].user_settings+")",t.append(n("<option></option>").val(a[r]).text(o))}})).fail((function(e,t,a){alert(a+"\n\n"+e.responseText)})),n("#ultimate-tab-create-unfiltered-btn").click((function(){i(n("#ultimate-tab-create-unfiltered-btn"),"all")}))}))}},a={};function n(e){var r=a[e];if(void 0!==r)return r.exports;var o=a[e]={id:e,exports:{}};return t[e].call(o.exports,o,o.exports,n),o.exports}n.m=t,e=[],n.O=(t,a,r,o)=>{if(!a){var i=1/0;for(u=0;u<e.length;u++){for(var[a,r,o]=e[u],s=!0,l=0;l<a.length;l++)(!1&o||i>=o)&&Object.keys(n.O).every((e=>n.O[e](a[l])))?a.splice(l--,1):(s=!1,o<i&&(i=o));if(s){e.splice(u--,1);var c=r();void 0!==c&&(t=c)}}return t}o=o||0;for(var u=e.length;u>0&&e[u-1][2]>o;u--)e[u]=e[u-1];e[u]=[a,r,o]},n.n=e=>{var t=e&&e.__esModule?()=>e.default:()=>e;return n.d(t,{a:t}),t},n.d=(e,t)=>{for(var a in t)n.o(t,a)&&!n.o(e,a)&&Object.defineProperty(e,a,{enumerable:!0,get:t[a]})},n.o=(e,t)=>Object.prototype.hasOwnProperty.call(e,t),n.r=e=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},n.j=838,(()=>{var e={299:0,838:0};n.O.j=t=>0===e[t];var t=(t,a)=>{var r,o,[i,s,l]=a,c=0;if(i.some((t=>0!==e[t]))){for(r in s)n.o(s,r)&&(n.m[r]=s[r]);if(l)var u=l(n)}for(t&&t(a);c<i.length;c++)o=i[c],n.o(e,o)&&e[o]&&e[o][0](),e[o]=0;return n.O(u)},a=self.webpackChunkhanfor=self.webpackChunkhanfor||[];a.forEach(t.bind(null,0)),a.push=t.bind(null,a.push.bind(a))})(),n.nc=void 0;var r=n.O(void 0,[223],(()=>n(7943)));r=n.O(r)})();