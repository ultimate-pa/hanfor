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
                "data": "status",
                "render": function ( data, type, row, meta ) {
                    result = '<div class="white-space-pre">' + data + '</div>';
                    return result;
                }

            }
        ],
        initComplete : function() {
        }
    });

    // Add listener for tag link to modal.
    runs_table.find('tbody').on('click', 'a.modal-opener', function (event) {
        // prevent body to be scrolled to the top.
        event.preventDefault();

        // Get row data
        let data = runs_datatable.row($(event.target).parent()).data();
        let row_id = runs_datatable.row($(event.target).parent()).index();

        // Prepare modal
        let modal_content = $('.modal-content');
        $('#ultimate_run_modal').modal('show');
        // modal_content.LoadingOverlay('show');
        $('#modal_associated_row_index').val(row_id);

        // Meta information
        $('#tag_name_old').val(data.name);
        $('#occurences').val(data.used_by);

        // Visible information
        $('#tag_modal_title').html('Ultimate run: ' + data.id);

        modal_content.LoadingOverlay('hide');
    });

    $('#stop_ultimate_run').confirmation({
      rootSelector: '#stop_ultimate_run'
    }).click(function () {
        alert('stopping ultimate run not implemented yet.')
    });

    $('#delete_ultimate_run').confirmation({
      rootSelector: '#delete_ultimate_run'
    }).click(function () {
        alert('deleting ultimate run not implemented yet.')
    });
});
