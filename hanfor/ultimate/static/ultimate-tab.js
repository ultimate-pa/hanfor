
function init_ultimate_tab() {
    check_ultimate_version();
    update_configurations();
}

function check_ultimate_version() {
    $.ajax({
        type: 'GET',
        url: '../api/ultimate/version'
    }).done(function (data) {
        if (data['version'] !== '') {
            let img = $('#ultimate-tab-ultimate-status-img')
            let img_src = img.attr("src");
            img.attr("src", img_src.replace('/disconnected.svg', '/connected.svg'));
            img.attr('title', 'Ultimate Api connected: ' + data['version'])
            $('#ultimate-tab-create-unfiltered-btn').prop("disabled",false);
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
        url: '../api/ultimate/configurations'
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

    $('#ultimate-tab-create-unfiltered-btn').click(function () {
        $('#ultimate-tab-create-unfiltered-btn').text("Processing Request")
        $.ajax({
            type: 'GET',
            url: '../api/tools/req_file',
        }).done(function (data) {
            let select = $('#ultimate-tab-configuration-select');
            let configuration = select.val();
            $.ajax({
                type: 'POST',
                url: '../api/ultimate/job?configuration=' + configuration,
                data: data
            }).done(function (data) {
                console.log(data['requestId'])
                // TODO inform user about new analysis
                $('#ultimate-tab-create-unfiltered-btn').text("Create Analysis");
            }).fail(function (jqXHR, textStatus, errorThrown) {
                alert(errorThrown + '\n\n' + jqXHR['responseText']);
            })
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert(errorThrown + '\n\n' + jqXHR['responseText']);
        })
    })
}

module.exports.init_ultimate_tab = init_ultimate_tab