require('gasparesganga-jquery-loading-overlay')
require('bootstrap')
require('jquery-ui/ui/effects/effect-highlight')
require('../../static/js/bootstrap-tokenfield.js')
require('../../static/js/bootstrap-confirm-button')
require('datatables.net-colreorder-bs5')


$(document).ready(function () {
    load_all_jobs()

    const ultimateTbl = $('#ultimate-job-result-tbl')
    const ultimateDataTable = ultimateTbl.DataTable({
        paging: true,
        stateSave: true,
        pageLength: 50,
        responsive: true,
        lengthMenu: [[10, 50, 100, 500, -1], [10, 50, 100, 500, 'All']],
        dom: 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        //ajax: {url: '../api/ultimate/job/' + $('#ultimate-job-select').val(), dataSrc: ''},
        deferRender: true,
        columns: [
                    {data: 'logLvl'},
                    {data: 'type'},
                    {data: 'shortDesc'},
                    {data: 'longDesc'}
                 ],
        initComplete: function () {
            this.api().draw()
        }
    });

    new $.fn.dataTable.ColReorder(ultimateDataTable, {})

    $('#ultimate-job-refresh-btn').click(function () {
        load_all_jobs()
    });

    $('#ultimate-job-load-btn').click(function () {
        let table = $('#ultimate-job-result-tbl').DataTable()
        $.ajax({
            type: "GET",
            url: '../api/ultimate/job/' + $('#ultimate-job-select').val()
        }).done(function (data) {
            $('#ultimate-job-request-id').text(data['requestId']);
            $('#ultimate-job-request-time').text(data['request_time']);
            $('#ultimate-job-last-update').text(data['last_update']);
            $('#ultimate-job-request-status').text(data['status']);
            table.clear();
            table.rows.add(data['result']);
            table.draw();
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert(errorThrown + '\n\n' + jqXHR['responseText']);
        });
    });

    $('#ultimate-job-download-btn').click(function () {
        $.ajax({
            type: 'GET',
            url: '../api/ultimate/job/' + $('#ultimate-job-select').val() + '?download=true',
        }).done(function (data) {
            download(data['job_id'] + '.json', JSON.stringify(data, null, 4));
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert(errorThrown + '\n\n' + jqXHR['responseText']);
        })
    });
})

function load_all_jobs() {
    $.ajax({
        type: 'GET',
        url: '../api/ultimate/jobs'
    }).done(function (data) {
        let select = $('#ultimate-job-select');
        select.empty();
        let jobs = data['data'];
        for (let i = 0; i < jobs.length; i++) {
            let displayed_name = jobs[i]['requestId'];
            displayed_name += ' ' + jobs[i]['request_time'];
            displayed_name += ' (' + jobs[i]['status'] + ')';
            select.append($('<option></option>').val(jobs[i]['requestId']).text(displayed_name));
        }
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(errorThrown + '\n\n' + jqXHR['responseText']);
    });
}

function download(filename, text) {
    let element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}