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

let utils = require('./hanfor-utils');

function ping_ultimate_api() {
    let badge = $('#ultimate_api_connection_badge');

    const badge_status = {
        fetching: 0,
        established: 1,
        error: 2
    };

    function set_badge_status(status) {
        // Remove all styling
        badge.attr('class', function(i, c){
            return c.replace(/(^|\s)badge-\S+/g, '');
        });
        switch (status) {
            case badge_status.fetching:
                badge.addClass('badge-info');
                badge.html('Fetching ...');
                break;
            case badge_status.established:
                badge.addClass('badge-success');
                badge.html('Established');
                break;
            case badge_status.error:
                badge.addClass('badge-danger');
                badge.html('Error');
                break;
        }
    }

    set_badge_status(badge_status.fetching);

    $.ajax({
        url: utils.api.ultimate.api_version.url,
        type: 'GET',
        data: JSON.stringify(utils.api.ultimate.api_version.task_payload.get_version),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        success: function(response) {
            if (response.success) {
                set_badge_status(badge_status.established);
            } else {
                set_badge_status(badge_status.error);
            }
        },
        error: function (jq_XHR, text_status, error_thrown) {
            alert('Could not ping ultimate API: ' + text_status + '\n' + error_thrown);
            set_badge_status(badge_status.error);
        }
    });
}

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
        $('#req_file_accordion').html(data.req_file_content);

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

    $('#api-info-tab').on('click', function (event){
        ping_ultimate_api();
    });
});
