require('bootstrap')
require('datatables.net-bs5')
require('datatables.net-colreorder-bs5')

const {SearchNode} = require("../../static/js/datatables-advanced-search");

const exampleSearchString = sessionStorage.getItem('exampleSearchString')

let search_tree

const dataTableColumns = [
    {
        data: 'id',
        render: function (data) {
            return `<div class="white-space-pre">${data}</div>`
        }
    }, {
        data: 'name',
        render: function (data) {
            return `<div class="white-space-pre">${data}</div>`
        }
    }, {
        data: 'age',
        render: function (data) {
            return `<div class="white-space-pre">${data}</div>`
        }
    }, {
        data: 'city',
        render: function (data) {
            return `<div class="white-space-pre">${data}</div>`
        }
    }
]

$(document).ready(function () {
    const searchInput = $('#search_bar')
    const table = $('#example-blueprint-tbl')
    const dataTable = table.DataTable({
        paging: true,
        stateSave: true,
        pageLength: 50,
        responsive: true,
        lengthMenu: [[10, 50, 100, 500, -1], [10, 50, 100, 500, 'All']],
        dom: 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
        ajax: {
            url: '../api/v1/example-blueprint/',
            dataSrc: function (json) {
                // Convert dictionary to array
                return Object.keys(json["data"]).map(id => ({
                    id: id, // Extract the ID as a field
                    ...json["data"][id] // Spread the actual data fields
                }));
            }
        },
        deferRender: true,
        columns: dataTableColumns,
        initComplete: function () {
            searchInput.val(exampleSearchString);
            update_search(searchInput.val().trim());

            // Enable Hanfor specific table filtering.
            $.fn.dataTable.ext.search.push(function (settings, data) {
                // data contains the row. data[0] is the content of the first column in the actual row.
                // Return true to include the row into the data. false to exclude.
                return evaluate_search(data);
            })
            this.api().draw();
        }
    });

    // Bind big custom searchbar to search the table.
    searchInput.keypress(function (e) {
        if (e.which === 13) { // Search on enter.
            update_search(searchInput.val().trim());
            dataTable.draw();
        }
    });

    $('.clear-all-filters').click(function () {
        searchInput.val('').effect('highlight', {color: 'green'}, 500);
        update_search(searchInput.val().trim());
        dataTable.draw();
    });

    $("#userForm").submit(function (event) {
        event.preventDefault(); // Prevent page reload

        let userData = {
            name: $("#name").val().trim(),
            age: parseInt($("#age").val()),
            city: $("#city").val().trim()
        };

        $.ajax({
            url: "../api/v1/example-blueprint/",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(userData),
            success: function (response) {
                console.log(response)
                $("#message").html('<div class="alert alert-success">User added successfully!</div>');
                $("#userForm")[0].reset(); // Reset form
                dataTable.ajax.reload(null, false); // 'false' prevents page reset
            },
            error: function (xhr) {
                $("#message").html('<div class="alert alert-danger">Error: ' + xhr.responseText + '</div>');
            }
        });
    });

    $("#deleteForm").submit(function (event) {
        event.preventDefault(); // Prevent page reload

        let userId = $("#userId").val().trim();

        $.ajax({
            url: `../api/v1/example-blueprint/${userId}`, // Use the entered ID in the URL
            type: "DELETE",
            success: function (response) {
                $("#deleteMessage").html('<div class="alert alert-success">User deleted successfully!</div>');
                $("#deleteForm")[0].reset(); // Reset form

                // Reload the DataTable to reflect the changes
                dataTable.ajax.reload(null, false); // 'false' prevents page reset
            },
            error: function (xhr) {
                $("#deleteMessage").html('<div class="alert alert-danger">Error: ' + xhr.responseText + '</div>');
            }
        });
    });
})

function update_search(string) {
    sessionStorage.setItem('ultimateSearchString', string)
    search_tree = SearchNode.fromQuery(string)
}

function evaluate_search(data) {
    return search_tree.evaluate(data, [true, true, true])
}