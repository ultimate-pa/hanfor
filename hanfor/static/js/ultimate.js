require('gasparesganga-jquery-loading-overlay');
require('bootstrap');
require('bootstrap-confirmation2');
require('datatables.net-bs4');
require('jquery-ui/ui/widgets/autocomplete');
require('jquery-ui/ui/effects/effect-highlight');
require('./bootstrap-tokenfield.js');
require('awesomplete');
require('awesomplete/awesomplete.css');
require('./colResizable-1.6.min.js');

$(document).ready(function() {
    let runs_table = $('#ultimate_runs_table');
    let runs_datatable = runs_table.DataTable({
        "paging": true,
        "stateSave": true,
        "pageLength": 50,
        "responsive": true,
        "lengthMenu": [[10, 50, 100, 500, -1], [10, 50, 100, 500, "All"]],
        "dom": 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        "ajax": "api/ultimate/runs",
        "deferRender": true,
        "columns": [
            {
                "data": "id",
                "render": function ( data, type, row, meta ) {
                  console.log(data);
                    result = '<a class="modal-opener" href="#">' + data + '</span></br>';
                    return result;
                }
            },
            {
                "data": "queued_human",
                "render": function ( data, type, row, meta ) {
                    result = '<div class="white-space-pre">' + data + '</div>';
                    return result;
                }

            },
            {
                "data": "description",
                "render": function ( data, type, row, meta ) {
                    result = '<div class="white-space-pre">' + data + '</div>';
                    return result;
                }

            }
        ],
        initComplete : function() {
        }
    });
});
