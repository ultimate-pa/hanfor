//const {Button} = require('bootstrap')
require('gasparesganga-jquery-loading-overlay')
require('datatables.net-bs5')
require('bootstrap')
require('../../telemetry/static/telemetry')
const bootstrap = require('bootstrap')

const CHECK_COMPLETENESS_BUTTON = $('#check-completeness-button')
const bsButton = bootstrap.Button.getOrCreateInstance('#check-completeness-button')

$(document).ready(function () {
    const completenessTable = $('#completeness-table')
    const completenessDataTable = completenessTable.DataTable({
        paging: true,
        stateSave: true,
        pageLength: 50,
        responsive: true,
        lengthMenu: [[10, 50, 100, 500, -1], [10, 50, 100, 500, 'All']],
        dom: 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        ajax: {url: '../api/quickchecks/results', dataSrc: ''},
        deferRender: true,
        columns: completenessDataTableColumns,
        initComplete: function () {
            this.api().draw();
        }
       });

    CHECK_COMPLETENESS_BUTTON.click(function () {
        /**
         * Performs an asynchronous HTTP request: https://api.jquery.com/jquery.ajax
         * HTTP response status codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
         */
        $.ajax({
            type: 'POST', url: '/api/quickchecks', contentType: 'application/json',
        }).done(function (data, textStatus, jqXHR) {
            completenessDataTable.ajax.reload(null, false);
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.log('jqXHR:', jqXHR, 'textStatus:', textStatus, 'errorThrown:', errorThrown)
            alert(errorThrown + '\n\n' + jqXHR['responseText'])
        })
    })
})

const completenessDataTableColumns = [
    {
        title: 'ID'
    }, {
        title: 'Check'
    }, {
        title: 'Result'
    }, {
        title: 'Description',
        render: function (data) {
            return `${data.replaceAll("\n", "<br/>")}`
        }
    }
]