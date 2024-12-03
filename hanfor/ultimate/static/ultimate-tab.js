
// let init_table_connection_functions = require('/js/requirements.js')['init_table_connection_functions']

$(document).ready(function () {
    init_ultimate_tab()
});

function init_ultimate_tab() {
    init_table_connection_functions.push(init_ultimate_requirements_table_connection)
    check_ultimate_version();
    update_configurations();

    $('#ultimate-tab-create-unfiltered-btn').click(function () {
        let btn = $('#ultimate-tab-create-unfiltered-btn')
        create_ultimate_analysis(btn, "all");
    });
}

function init_ultimate_requirements_table_connection (requirements_table) {
    $('#ultimate-tab-create-filtered-btn').click(function () {
        let req_ids = [];
        requirements_table.rows({search: 'applied'}).every(function () {
            let d = this.data();
            req_ids.push(d['id']);
        });

        let btn = $('#ultimate-tab-create-filtered-btn')
        create_ultimate_analysis(btn, req_ids);
    });

    $('#ultimate-tab-create-selected-btn').click(function () {
        let req_ids = [];
        requirements_table.rows({selected: true}).every(function () {
            let d = this.data();
            req_ids.push(d['id']);
        });

        let btn = $('#ultimate-tab-create-selected-btn')
        create_ultimate_analysis(btn, req_ids);
    });
}

function check_ultimate_version() {
    $.ajax({
        type: 'GET',
        url: 'api/ultimate/version'
    }).done(function (data) {
        if (data['version'] !== '') {
            let img = $('#ultimate-tab-ultimate-status-img')
            let img_src = img.attr("src");
            img.attr("src", img_src.replace('/disconnected.svg', '/connected.svg'));
            img.attr('title', 'Ultimate Api connected: ' + data['version'])
            $('#ultimate-tab-create-unfiltered-btn').prop("disabled",false);
            $('#ultimate-tab-create-filtered-btn').prop("disabled",false);
            $('#ultimate-tab-create-selected-btn').prop("disabled",false);
        } else {
            console.log('no ultimate connection found!');
        }
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(errorThrown + '\n\n' + jqXHR['responseText']);
    });
}

function update_configurations() {
    $.ajax({
        type: 'GET',
        url: 'api/ultimate/configurations'
    }).done(function (data) {
        let select = $('#ultimate-tab-configuration-select');
        select.empty();
        let configurations = Object.keys(data);
        for (let i = 0; i < configurations.length; i++) {
            let displayed_name = configurations[i];
            displayed_name += ' (Toolchain: ' + data[configurations[i]]['toolchain'];
            displayed_name += ', User Settings: ' + data[configurations[i]]['user_settings'] + ')';
            select.append($('<option></option>').val(configurations[i]).text(displayed_name));
        }
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(errorThrown + '\n\n' + jqXHR['responseText']);
    });
}

function create_ultimate_analysis(btn, req_ids) {
    let old_text = btn.text()
    btn.text("Processing Request")
    let request_data = {'selected_requirement_ids': JSON.stringify(req_ids)}
    if (req_ids === "all") {
        request_data = {}
    }
    $.ajax({
        type: 'POST',
        url: 'api/tools/req_file',
        data: request_data
    }).done(function (data) {
        let select = $('#ultimate-tab-configuration-select');
        let configuration = select.val();
        $.ajax({
            type: 'POST',
            url: 'api/ultimate/job',
            data: JSON.stringify({"configuration": configuration,
                   "req_file": data,
                   "req_ids": req_ids})
        }).done(function (data) {
            console.log(data['requestId'])
            // TODO inform user about new analysis
            btn.text(old_text);
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert(errorThrown + '\n\n' + jqXHR['responseText']);
        })
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(errorThrown + '\n\n' + jqXHR['responseText']);
    });
}
