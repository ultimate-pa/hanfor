require('gasparesganga-jquery-loading-overlay');
require('bootstrap');
require('bootstrap-confirmation2');
require('datatables.net-bs4');
require('jquery-ui/ui/widgets/autocomplete');
require('./bootstrap-tokenfield.js');

let tag_search_string = sessionStorage.getItem('tag_search_string');

/**
 * Store the currently active (in the modal) tag.
 * @param tagss_datatable
 */
function store_tag(tagss_datatable) {
    tag_modal_content = $('.modal-content');
    tag_modal_content.LoadingOverlay('show');

    // Get data.
    tag_name = $('#tag_name').val();
    tag_name_old = $('#tag_name_old').val();
    occurences = $('#occurences').val();
    tag_color = $('#tag_color').val();
    associated_row_id = parseInt($('#modal_associated_row_index').val());

    // Store the tag.
    $.post( "api/tag/update",
        {
            name: tag_name,
            name_old: tag_name_old,
            occurences: occurences,
            color: tag_color
        },
        // Update tag table on success or show an error message.
        function( data ) {
            tag_modal_content.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                if (data.rebuild_table) {
                    location.reload();
                } else {
                    tags_datatable.row(associated_row_id).data(data.data).draw();
                    $('#tag_modal').modal('hide');
                }
            }
    });
}


function delete_tag(name) {
    tag_modal_content = $('.modal-content');
    tag_modal_content.LoadingOverlay('show');

    tag_name = $('#tag_name').val();
    occurences = $('#occurences').val();
    $.post( "api/tag/del_tag",
        {
            name: tag_name,
            occurences: occurences
        },
        // Update tag table on success or show an error message.
        function( data ) {
            tag_modal_content.LoadingOverlay('hide', true);
            if (data['success'] === false) {
                alert(data['errormsg']);
            } else {
                if (data.rebuild_table) {
                    location.reload();
                } else {
                    tags_datatable.row(associated_row_id).data(data.data).draw();
                    $('#tag_modal').modal('hide');
                }
            }
    });
}

$(document).ready(function() {
    // Prepare and load the tags table.
    tags_table = $('#tags_table');
    tags_datatable = tags_table.DataTable({
        "paging": true,
        "stateSave": true,
        "pageLength": 50,
        "responsive": true,
        "lengthMenu": [[10, 50, 100, 500, -1], [10, 50, 100, 500, "All"]],
        "dom": 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        "ajax": "api/tag/gets",
        "deferRender": true,
        "columns": [
            {
                "data": "name",
                "render": function ( data, type, row, meta ) {
                    result = '<a class="modal-opener" href="#">' + data + '</span></br>';
                    return result;
                }
            },
            {
                "data": "used_by",
                "render": function ( data, type, row, meta ) {
                    result = '';
                    $(data).each(function (id, name) {
                        if (name.length > 0) {
                            search_query = '?command=search&col=2&q=' + name;
                            result += '<span class="badge badge-info">' +
                                '<a href="' + base_url + search_query + '" target="_blank">' + name + '</a>' +
                                '</span>';
                        }
                    });
                    return result;
                }

            },
            {
                "data": "used_by",
                "visible": false,
                "searchable": false,
                "render": function ( data, type, row, meta ) {
                    result = '';
                    $(data).each(function (id, name) {
                        if (name.length > 0) {
                            if (result.length > 1) {
                                result += ', '
                            }
                            result += name;
                        }
                    });
                    return result;
                }
            }
        ],
        initComplete : function() {
            $('#search_bar').val(tag_search_string);
        }
    });
    tags_datatable.column(2).visible(false);

    // Bind big custom searchbar to search the table.
    $('#search_bar').keyup(function(){
      tags_datatable.search($(this).val()).draw();
      sessionStorage.setItem('tag_search_string', $(this).val());
    });

    // Add listener for tag link to modal.
    tags_table.find('tbody').on('click', 'a.modal-opener', function (event) {
        // prevent body to be scrolled to the top.
        event.preventDefault();

        // Get row data
        let data = tags_datatable.row($(event.target).parent()).data();
        let row_id = tags_datatable.row($(event.target).parent()).index();

        // Prepare tag modal
        tag_modal_content = $('.modal-content');
        $('#tag_modal').modal('show');

        // Meta information
        $('#tag_name_old').val(data.name);
        $('#occurences').val(data.used_by);

        // Visible information
        $('#tag_modal_title').html('Tag: ' + data.name);
        $('#tag_name').val(data.name);

        tag_modal_content.LoadingOverlay('hide');
    });

    // Store changes on tag on save.
    $('#save_tag_modal').click(function () {
        store_tag(tags_datatable);
    });

    $('.delete_tag').confirmation({
      rootSelector: '.delete_tag'
    }).click(function () {
        delete_tag( $(this).attr('name') );
    });
} );