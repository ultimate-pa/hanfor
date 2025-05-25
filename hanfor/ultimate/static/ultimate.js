require('gasparesganga-jquery-loading-overlay')
require('bootstrap')
require('datatables.net-bs5')
require('jquery-ui/ui/effects/effect-highlight')
require('../../static/js/bootstrap-tokenfield.js')
require('../../static/js/bootstrap-confirm-button')
require('datatables.net-colreorder-bs5')
require('../../telemetry/static/telemetry')

const {SearchNode} = require("../../static/js/datatables-advanced-search");
const ultimateSearchString = sessionStorage.getItem('ultimateSearchString')
const {Modal} = require('bootstrap')

let search_tree
let reload_timer

$(document).ready(function () {
    const searchInput = $('#search_bar')
    const ultimateJobsTable = $('#ultimate-jobs-tbl')
    const ultimateJobsDataTable = ultimateJobsTable.DataTable({
        paging: true,
        stateSave: true,
        pageLength: 50,
        responsive: true,
        lengthMenu: [[10, 50, 100, 500, -1], [10, 50, 100, 500, 'All']],
        dom: 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        ajax: {
            url: 'api/v1/ultimate/jobs'
        },
        deferRender: true,
        columns: dataTableColumns,
        initComplete: function () {
            searchInput.val(ultimateSearchString);
            update_search(searchInput.val().trim());

            // Enable Hanfor specific table filtering.
            $.fn.dataTable.ext.search.push(function (settings, data) {
                // data contains the row. data[0] is the content of the first column in the actual row.
                // Return true to include the row into the data. false to exclude.
                return evaluate_search(data);
            })
            this.api().draw();
            updateTableData()
        }
    });

    // Bind big custom searchbar to search the table.
    searchInput.keypress(function (e) {
        if (e.which === 13) { // Search on enter.
            update_search(searchInput.val().trim());
            ultimateJobsDataTable.draw();
        }
    });

    $('.clear-all-filters').click(function () {
        searchInput.val('').effect('highlight', {color: 'green'}, 500);
        update_search(searchInput.val().trim());
        ultimateJobsDataTable.draw();
    });

    const ultimateResultTable = $('#ultimate-job-modal-result-tbl')
    const ultimateResultDataTable = ultimateResultTable.DataTable({
        paging: true,
        stateSave: true,
        pageLength: 50,
        responsive: true,
        lengthMenu: [[10, 50, 100, 500, -1], [10, 50, 100, 500, 'All']],
        dom: 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        deferRender: true,
        columns: resultDataTableColumns,
        initComplete: function () {
            this.api().draw()
        }
    });

    // Add listener for job_link link to modal.
    ultimateJobsTable.find('tbody').on('click', 'a.modal-opener', function (event) {
        // prevent body to be scrolled to the top.
        event.preventDefault();

        // Get row data
        let data = ultimateJobsDataTable.row($(event.target).parent()).data();

        Modal.getOrCreateInstance($('#ultimate-job-modal')).show();
        $('#ultimate-job-modal-title').html('Job ID: ' + data['requestId']);

        $('#ultimate-job-modal-request-time').text(data['request_time']);
        $('#ultimate-job-modal-last-update').text(data['last_update']);
        $('#ultimate-job-modal-request-status').text(data['status']);
        ultimateResultDataTable.clear();
        ultimateResultDataTable.rows.add(data['result']);
        ultimateResultDataTable.draw();

        $('#ultimate-tag-modal-download-btn').click(function () {
            download_req(data['requestId']);
        });

        $('#ultimate-tag-modal-cancel-btn').click(function () {
            cancel_job(data['requestId']);
        });

    })
});

const dataTableColumns = [
    {
        data: 'requestId',
        render: function (data) {
            return `<a class="modal-opener" href="#">${data}</a>`
        }
    }, {
        data: 'request_time',
        order: 'asc',
        render: function (data) {
            return `<div class="white-space-pre">${data}</div>`
        }
    }, {
        data: 'last_update',
        render: function (data) {
            return `<div class="white-space-pre">${data}</div>`
        }
    }, {
        data: 'status',
        render: function (data) {
            return `<div class="white-space-pre">${data}</div>`
        }
    }, {
        data: 'selected_requirements',
        render: function (data) {
            let result = ''
            for (let name in data) {
                let count = data[name]
                if (display_req_without_formalisation !== "True" && count === 0) continue;
                const searchQuery = `?command=search&col=2&q=%5C%22${name}%5C%22`
                const color = count === 0 ? 'bg-light' : 'bg-info'
                result += `<span class="badge ${color}"><a href="${base_url}${searchQuery}" target="_blank" class="link-light text-muted">${name} (${count})</a></span> `
            }
            return result;
        }
    }, {
        data: 'result_requirements',
        render: function (data) {
            let result = ''
            for (let name in data) {
                let count = data[name]
                const searchQuery = `?command=search&col=2&q=%5C%22${name}%5C%22`
                const color = count === 0 ? 'bg-light' : 'bg-info'
                result += `<span class="badge ${color}"><a href="${base_url}${searchQuery}" target="_blank" class="link-light text-muted">${name} (${count})</a></span> `
            }
            return result;
        }
    }
]

const resultDataTableColumns = [
    {
        data: 'logLvl'
    }, {
        data: 'type'
    }, {
        data: 'shortDesc',
        render: function (data) {
            return `${data.replaceAll("\n", "<br/>")}`
        }
    }, {
        data: 'longDesc',
        render: function (data) {
            return `${data.replaceAll("\n", "<br/>")}`
        }
    }
]

function update_search(string) {
    sessionStorage.setItem('ultimateSearchString', string)
    search_tree = SearchNode.fromQuery(string)
}

function evaluate_search(data) {
    return search_tree.evaluate(data, [true, true, true])
}

function download_req(req_id) {
    $.ajax({
        type: 'GET',
        url: 'api/v1/ultimate/jobs/' + req_id + '?download=true',
    }).done(function (data) {
        download(data['job_id'] + '.json', JSON.stringify(data, null, 4))
        updateTableData()
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(errorThrown + '\n\n' + jqXHR['responseText'])
    })
}

function cancel_job(job_id) {
    console.log("cancel")
    $.ajax({
        type: 'POST',
        url: 'api/v1/ultimate/jobs/' + job_id +'/abort',
    }).done(function (data) {
        updateTableData()
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(errorThrown + '\n\n' + jqXHR['responseText'])
    })
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

function updateTableData() {
    stoppReloadTimer()
    $.ajax({
        type: 'POST',
        url: 'api/v1/ultimate/update-all'
    }).done(function (data) {
        if (data['status'] === 'done') {
            const ultimateJobsTable = $('#ultimate-jobs-tbl')
            ultimateJobsTable.DataTable().ajax.reload()
        }
        startReloadTimer()
    }).fail(function (jqXHR, textStatus, errorThrown) {
        alert(errorThrown + '\n\n' + jqXHR['responseText']);
    })
}

function startReloadTimer(){
    reload_timer = setTimeout(updateTableData, 60000)
}

function stoppReloadTimer() {
    clearInterval(reload_timer)
}