//const {Button} = require('bootstrap')
require('gasparesganga-jquery-loading-overlay')
require('datatables.net-bs5')
require('bootstrap')
require('../../telemetry/static/telemetry')

$(document).ready(function () {
    const completenessTable = $('#completeness-table')
    const completenessDataTable = completenessTable.DataTable({
        paging: true,
        stateSave: true,
        pageLength: 50,
        responsive: true,
        lengthMenu: [[10, 50, 100, 500, -1], [10, 50, 100, 500, 'All']],
        dom: 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        ajax: {url: 'api/quickchecks/results', dataSrc: ''},
        deferRender: true,
        columns: completenessDataTableColumns,
        initComplete: function () {
            this.api().draw();
        }
       });

     $('#check-completeness-button').click(function () {
        $.ajax({
            type: 'POST',
            url: 'api/quickchecks/',
            contentType: 'application/json',
            success: function (data, textStatus, jqXHR) {
                completenessDataTable.ajax.reload(null, false)},
            fail: function (jqXHR, textStatus, errorThrown) {
                console.log('jqXHR:', jqXHR, 'textStatus:', textStatus, 'errorThrown:', errorThrown)
                alert(errorThrown + '\n\n' + jqXHR['responseText'])}
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