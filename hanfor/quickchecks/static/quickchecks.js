//const {Button} = require('bootstrap')
require('gasparesganga-jquery-loading-overlay')
require('datatables.net-bs5')
require('bootstrap')
const bootstrap = require('bootstrap')

const AWESOME_MESSAGE_BUTTON = $('#awesome-message-button')
const bsButton = bootstrap.Button.getOrCreateInstance('#awesome-message-button')

$(document).ready(function () {
    const completenessTable = $('#completeness-table')
    const completenessDataTable = completenessTable.DataTable({
        paging: true,
        stateSave: true,
        pageLength: 50,
        deferRender: false,
        lengthMenu: [[10, 50, 100, 500, -1], [10, 50, 100, 500, 'All']],
        dom: 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        columns: completenessDataTableColumns,
        initComplete: function () {
            this.api().draw();
        }
       });

    AWESOME_MESSAGE_BUTTON.click(function () {
        /**
         * Performs an asynchronous HTTP request: https://api.jquery.com/jquery.ajax
         * HTTP response status codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
         */
        $.ajax({
            type: 'POST', url: '/api/quickchecks/completeness', contentType: 'application/json',
        }).done(function (data, textStatus, jqXHR) {
            completenessDataTable.clear();
            data["data"].forEach(d => {
                completenessDataTable.row.add(d);
            });
            //completenessDataTable.rows.add(data)
            completenessDataTable.draw();
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.log('jqXHR:', jqXHR, 'textStatus:', textStatus, 'errorThrown:', errorThrown)
            alert(errorThrown + '\n\n' + jqXHR['responseText'])
        })
    })
})

const completenessDataTableColumns = [
    {
        title: 'var'
    }, {
        title: 'type'
    }, {
        title: 'description',
        render: function (data) {
            return `${data.replaceAll("\n", "<br/>")}`
        }
    }
]