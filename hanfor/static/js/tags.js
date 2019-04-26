require('gasparesganga-jquery-loading-overlay');
require('bootstrap');
require('bootstrap-confirmation2');
require('datatables.net-bs4');
require('jquery-ui/ui/widgets/autocomplete');
require('./bootstrap-tokenfield.js');
const autosize = require('autosize');

let tag_search_string = sessionStorage.getItem('tag_search_string');

/**
 * Store the currently active (in the modal) tag.
 * @param tags_datatable
 */
function store_tag(tags_datatable) {
    let tag_modal_content = $('.modal-content');
    tag_modal_content.LoadingOverlay('show');

    // Get data.
    let tag_name = $('#tag_name').val();
    let tag_name_old = $('#tag_name_old').val();
    let occurences = $('#occurences').val();
    let tag_color = $('#tag_color').val();
    let associated_row_id = parseInt($('#modal_associated_row_index').val());
    let tag_description = $('#tag-description').val();

    // Store the tag.
    $.post( "api/tag/update",
        {
            name: tag_name,
            name_old: tag_name_old,
            occurences: occurences,
            color: tag_color,
            description: tag_description
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
    let tag_modal_content = $('.modal-content');
    tag_modal_content.LoadingOverlay('show');

    let tag_name = $('#tag_name').val();
    let occurences = $('#occurences').val();
    $.ajax({
      type: "DELETE",
      url: "api/tag/del_tag",
      data: {name: tag_name, occurences: occurences},
      success: function (data) {
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
      }
    });
}

$(document).ready(function() {
    // Prepare and load the tags table.
    let tags_table = $('#tags_table');
    let tags_datatable = tags_table.DataTable({
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
                "data": "description",
                "render": function ( data, type, row, meta ) {
                    result = data;
                    return result;
                }

            },
            {
                "data": "used_by",
                "render": function ( data, type, row, meta ) {
                    result = '';
                    $(data).each(function (id, name) {
                        if (name.length > 0) {
                            search_query = '?command=search&col=2&q=%5C%22' + name + '%5C%22';
                            result += '<span class="badge" style="background-color: ' + row.color +'">' +
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
    tags_datatable.column(3).visible(false);

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
        let tag_modal_content = $('.modal-content');
        $('#tag_modal').modal('show');
        $('#modal_associated_row_index').val(row_id);

        // Meta information
        $('#tag_name_old').val(data.name);
        $('#occurences').val(data.used_by);

        // Visible information
        $('#tag_modal_title').html('Tag: ' + data.name);
        $('#tag_name').val(data.name);
        $('#tag_color').val(data.color);
        $('#tag-description').val(data.description);

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

    autosize($('#tag-description'));
} );