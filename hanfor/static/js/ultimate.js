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
let _ULTIMATE_TOOLCHAIN_XML = null

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

    let task = new utils.UltimateAPITaskPingUltimate().run();
    task.done(function (response) {
        if (response.success) {
            set_badge_status(badge_status.established);
        } else {
            set_badge_status(badge_status.error);
        }
    });
}

function fetch_ultimate_toolchain_xml() {
    return $.get('static/configs/ultimate/toolchain.xml', function (response) {
        _ULTIMATE_TOOLCHAIN_XML = (new XMLSerializer()).serializeToString(response);
    }).fail(function () {
        alert("Could not fetch ultimate toolchain xml. Config error.");
    });
}

function populate_modal_with_data(data) {
    // Meta information.
    $('#modal_run_job_id').val(data.id);
    $('#modal_run_ultimate_job_id').val(data.ultimate_run_id);

    // Visible information.
    $('#modal_title').html('Ultimate run: ' + data.id);
    $('#req_file_accordion').html(data.req_file_content);
    let results = $('#results_accordion');
    if (data.status === 'done') {
        results.html(JSON.stringify(data.results.results));
    } else {
        results.html('No results so far...');
    }
}

function initiate_ultimate_run() {
    loading_overlay('show');
    let requirements_table = $('#ultimate_runs_table').DataTable();
    const row_id = $('#modal_associated_row_index').val();
    const run_id = $('#modal_run_job_id').val();
    const user_settings = [];

    let task = new utils.UltimateAPITaskStartRun(
      run_id,
      JSON.stringify({user_settings}),
      _ULTIMATE_TOOLCHAIN_XML
    ).run();
    task.done(function (response) {
        if (response['success'] === false) {
            alert(response['errormsg']);
        } else {
            populate_modal_with_data(response.data);
            requirements_table.row(row_id).data(response.data);
        }
    });
    task.always(function () {
        loading_overlay('hide');
    });
}

function start_ultimate_run() {
    if (_ULTIMATE_TOOLCHAIN_XML === null) {
        let xhr = fetch_ultimate_toolchain_xml();
        xhr.done(function () {
            initiate_ultimate_run();
        });
    } else {
        initiate_ultimate_run();
    }
}

function loading_overlay(overlay_state) {
    let modal_content = $('.modal-content');
    modal_content.LoadingOverlay(overlay_state);
}

function fetch_ultimate_results(row_id) {
    loading_overlay('show');
    console.log(row_id);
    let requirements_table = $('#ultimate_runs_table').DataTable();
    const hanfor_job_id = $('#modal_run_job_id').val();
    let task = new utils.UltimateAPITaskReloadRun(hanfor_job_id).run();

    task.done(function (response) {
        if (response['success'] === false) {
            alert(response['errormsg']);
        } else {
            populate_modal_with_data(response.data);
            requirements_table.row(row_id).data(response.data);
        }
    });
    task.always(function (){
        loading_overlay('hide');
    });
}

function reload_run() {
    const row_id = $('modal_associated_row_index').val();
    fetch_ultimate_results(row_id);
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
                    let result = '<a class="modal-opener" href="#">' + data + '</span></br>';
                    return result;
                }
            },
            {
                "data": "queued_human",
                "render": function ( data, type, row, meta ) {
                    let result = '<div class="white-space-pre">' + data + '</div>';
                    return result;
                }

            },
            {
                "data": "status",
                "render": function ( data, type, row, meta ) {
                    let result = '';
                    switch (data) {
                        case 'done': {
                            result = '<span class="badge badge-success">Done</span>';
                            break;
                        }
                        case 'waiting': {
                            result = '<span class="badge badge-info">Waiting</span>';
                            break
                        }
                        case 'scheduled': {
                            result = '<div class="spinner-border text-success" role="status">' +
                                '<span class="sr-only">Running</span></div>';
                            break
                        }
                        default: {
                            result = '<span class="badge badge-danger">Error</span>';
                        }
                    }
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
        $('#ultimate_run_modal').modal('show');
        $('#modal_associated_row_index').val(row_id);

        populate_modal_with_data(data);
        fetch_ultimate_results(row_id);
    });

    $('#start_ultimate_run').confirmation({
      rootSelector: '#start_ultimate_run'
    }).click(function () {
        start_ultimate_run();
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

    $('#reload_run').on('click', function (event) {
        reload_run();
    })
});