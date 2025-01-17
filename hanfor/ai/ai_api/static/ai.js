require('gasparesganga-jquery-loading-overlay')
require('bootstrap')
require('datatables.net-bs5')
require('jquery-ui/ui/widgets/autocomplete')
require('jquery-ui/ui/effects/effect-highlight')
require('awesomplete')
require('awesomplete/awesomplete.css')
require('datatables.net-colreorder-bs5')



$(document).ready(function (){
    // TODO with socket
    function get_update(){
        $.ajax({
            type: 'GET',
            url: '/api/ai/get/current_data',
            contentType: 'application/json'
        }).done(function (data) {
            update(data)
        });
    }


    // Main update function for all changing data
    function update(data) {
        // Update Cluster Status
        if (data.cluster_status) {
            $('#cluster-status').text(data.cluster_status.status || 'N/A');
            const processed = data.cluster_status.processed || 0;
            const total = data.cluster_status.total || 0;
            $('#cluster-availability').text(`${processed} / ${total}`);
        } else {
            $('#cluster-status').text('N/A');
            $('#cluster-availability').text(0);
        }

        // Update AI Status
        if (data.ai_status) {
            $('#ai-running-count').text(data.ai_status.running || 0);
            $('#ai-queue-count').text(data.ai_status.queued || 0);
        } else {
            $('#ai-running-count').text(0);
            $('#ai-queue-count').text(0);
        }

        // Update Flags (switches)
        if (data.flags) {
            $('#toggle-system-switch').prop('checked', data.flags.system).trigger('change');
            $('#toggle-ai-switch').prop('checked', data.flags.ai).trigger('change');
        }

        // Update Clustering Process Selection with Sim Methods
        if (data.sim_methods) {
            const selectElement = $('#clustering-process-select');
            selectElement.empty(); // Clear existing options

            // Loop through each similarity method and add it to the dropdown
            data.sim_methods.forEach(function (method) {
                const option = $('<option></option>')
                    .attr('value', method.name)
                    .text(`${method.name}: ${method.description}`)
                    .prop('selected', method.selected); // Mark the selected method
                selectElement.append(option); // Add the option to the dropdown
            });
        }

        // Update the Progressbar on Similarity Interface
        const processed = data.cluster_status.processed;
        const total = data.cluster_status.total;
        const status = data.cluster_status.status;
        // Update the progress bar and status text
        $('#progress-status').text(`Status: ${status}`);
        $('#progress-bar').css('width', `${(processed / total) * 100}%`);
        $('#progress-bar').attr('aria-valuenow', processed);
        $('#progress-bar').text(`${processed}/${total}`);

        if (data.ai_status.response !== null) {
            $('#ai-response').text(data.ai_status.response);
        }
        if (data.ai_status.query !== null) {
            $('#ai-query').text(data.ai_status.query);
        }

        // Updating the cluster table
        populateTable(data.clusters)
        fetchAndDisplayProgress(data.ai_formalization)
    }

    $('#terminate-all-button').click(function () {
        $.ajax({
            type: 'POST',
            url: '/api/ai/terminate/all',
            contentType: 'application/json'
        }).done(function (data) {
            alert(data.message);  // Show a popup alert with the response message
        }).fail(function (jqXHR) {
            alert(`Error: ${jqXHR.responseText}`);  // Show error alert
        });
    });

    $('#toggle-system-switch').on('change', function () {
        const isChecked = $(this).is(':checked');
        $.ajax({
            type: 'POST',
            url: '/api/ai/set/flag/system',
            contentType: 'application/json',
            data: JSON.stringify({ system_enabled: isChecked })
        });
    });

    $('#toggle-ai-switch').on('change', function () {
        const isChecked = $(this).is(':checked');
        $.ajax({
            type: 'POST',
            url: '/api/ai/set/flag/ai',
            contentType: 'application/json',
            data: JSON.stringify({ ai_enabled: isChecked })
        });
    });


    // EVENT Dropdown for choosing clustering methode
    $('#clustering-process-select').on('change', function() {
        const selectedMethod = $(this).val();
        $.ajax({
            type: 'POST',
            url: '/api/ai/set/method/sim',
            contentType: 'application/json',
            data: JSON.stringify({ name: selectedMethod }),
            success: function(response) {
                console.log(response.message);
                get_update();
            },
            error: function(error) {
                console.error("Error setting method:", error);
            }
        });
    });

    $('#start-clustering').click(function () {
        $.ajax({
            type: 'POST',
            url: '/api/ai/set/sim/start',
            contentType: 'application/json'
        })
    });

    $('#terminate-clustering-button').click(function () {
        $.ajax({
            type: 'POST',
            url: '/api/ai/terminate/sim',
            contentType: 'application/json'
        })
    });

    $('#terminate-ai-button').click(function () {
        $.ajax({
            type: 'POST',
            url: '/api/ai/terminate/ai',
            contentType: 'application/json'
        })
    });

    $('#process-ai').click(function () {
        $.ajax({
            type: 'POST',
            url: '/api/ai/ai/process',
            contentType: 'application/json'
        })
    });

    $('#submit-prompt-button').click(function () {
        var userPrompt = $('#user-prompt').val();

        if (!userPrompt) {
            alert('Please enter a prompt!');
            return;
        }
        $.ajax({
            type: 'POST',
            url: '/api/ai/ai/query',
            contentType: 'application/json',
            data: JSON.stringify({ query: userPrompt }),
            success: function(response) {
                $('#ai-response').text('Processing your query...');
            },
            error: function(xhr, status, error) {
                $('#ai-response').text('Error: ' + xhr.responseJSON.error);
            }
        });
    });


    // Visualization of the similarity matrix
    $('#get-matrix-button').click(function () {
        $.ajax({
            type: 'GET',
            url: '/api/ai/get/sim/matrix',
            contentType: 'application/json'
        }).done(function (data) {
            const table = document.getElementById("similarity-matrix");
            const thead = table.querySelector("thead");
            const tbody = table.querySelector("tbody");

            thead.innerHTML = '';
            tbody.innerHTML = '';

            const matrix = data.matrix;
            const indexing = data.indexing;

            function calculateHeatmapColor(value) {
                const intensity = Math.round(value * 255);
                return `rgb(${255 - intensity}, ${255 - intensity}, 255)`;
            }

            const headerRow = document.createElement("tr");
            headerRow.appendChild(document.createElement("th")); // Leeres Eckfeld
            Object.keys(indexing).forEach(key => {
                const th = document.createElement("th");
                th.textContent = key;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);

            Object.keys(indexing).forEach((rowKey, rowIndex) => {
                const row = document.createElement("tr");

                // Zeilenbeschriftung
                const th = document.createElement("th");
                th.textContent = rowKey;
                row.appendChild(th);

                // Zellen erstellen
                matrix[rowIndex].forEach(value => {
                    const td = document.createElement("td");
                    td.textContent = value.toFixed(2);
                    td.style.backgroundColor = calculateHeatmapColor(value);
                    row.appendChild(td);
                });

                tbody.appendChild(row);
            });
        }).fail(function () {
            const table = document.getElementById("similarity-matrix");
            const thead = table.querySelector("thead");
            const tbody = table.querySelector("tbody");
            thead.innerHTML = '';
            tbody.innerHTML = '';
        });
    });


    function populateTable(data) {
        const TABLE_BODY = $('#cluster-table tbody');
        const TABLE = $('#cluster-table');

        // Destroy existing DataTable if it's initialized
        if ($.fn.dataTable.isDataTable(TABLE)) {
            TABLE.DataTable().clear().destroy();
        }

        // Clear the table body
        TABLE_BODY.empty();

        // Ensure data is in correct format (array of arrays)
        if (!Array.isArray(data) || data.length === 0) {
            console.error('Invalid or empty data.');
            return;
        }

        // Sort clusters by the smallest ID in each cluster
        data.sort((a, b) => getSmallestId(a).localeCompare(getSmallestId(b)));

        // Iterate over each cluster and populate the table
        data.forEach(ids => {
            if (!Array.isArray(ids)) {
                console.error('Invalid cluster structure:', ids);
                return;
            }

            // Sort IDs lexicographically within each cluster
            ids.sort((a, b) => a.localeCompare(b));

            const clusterName = `Cluster ${ids[0]}`;
            const idsHtml = generateIdsHtml(ids);
            const searchQuery = ids.map(id => `%5C%22${id}%5C%22`).join('%3AOR%3A');
            const showAllLink = ids.length > 1 ? generateShowAllLink(searchQuery) : '';
            const idCountCell = `<td>${ids.length}</td>`;

            const row = `<tr>
                            <td>${clusterName}</td>
                            <td>${idsHtml} ${showAllLink}</td>
                            ${idCountCell}
                        </tr>`;
            TABLE_BODY.append(row);
        });

        // Initialize DataTable after populating the table
        TABLE.DataTable({
            paging: true,
            stateSave: true,
            pageLength: 10,
            responsive: true,
            lengthMenu: [[10, 50, 100, 500, -1], [10, 50, 100, 500, 'All']],
            dom: 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
            columnDefs: [{
                targets: 2,
                orderDataType: 'dom-text',
            }],
            order: [[2, 'desc']],
        });
    }

    function getSmallestId(cluster) {
        if (!Array.isArray(cluster) || cluster.length === 0) return '';
        return cluster.map(id => id.toString()).sort()[0];
    }

    function generateIdsHtml(ids) {
        return ids.map(id =>
            `<span class="badge bg-info">
                <a href="${base_url}?command=search&col=2&q=%5C%22${id}%5C%22" target="_blank" class="link-light">${id}</a>
            </span>`
        ).join(' ');
    }

    function generateShowAllLink(query) {
        return `<span class="badge bg-info">
                    <a href="${base_url}?command=search&col=2&q=${query}" target="_blank" class="link-light">Show all</a>
                </span>`;
    }


    function fetchAndDisplayProgress(data) {
        // Destroy any existing DataTable before initializing a new one
        if ($.fn.dataTable.isDataTable('#ai-progress-table')) {
            $('#ai-progress-table').DataTable().clear().destroy();
        }
        const tableBody = $('#ai-progress-table tbody');
        tableBody.empty(); // Clear the table before adding new data

        // Iterate through the data and build table rows
        data.forEach(item => {
            // Safety check for each column and fallback logic
            const id = item.id || 'N/A';
            const promptDesc = item.prompt ? item.prompt : 'N/A';
            const status = item.status || 'N/A';
            const aiResponse = item.ai_response ? JSON.stringify(item.ai_response, null, 2) : 'N/A'; // Pretty formatted JSON
            const try_count = item.try_count || 'X';
            // Calculate the countdown for deletion, rounded to the next second
            const currentTime = Math.floor(Date.now() / 1000); // Current time in seconds
            const deletionCountdown = item.time ? Math.max(0, Math.ceil(9 - (currentTime - item.time))) : 'N/A';

            // Create the table row with an additional column for the countdown
            const row = `
                <tr id="row-${id}">
                    <td>${id}</td>
                    <td>${promptDesc}</td>
                    <td>${status}</td>
                    <td>${aiResponse}</td>
                    <td>${try_count}</td>td>
                    <td id="countdown-${id}">${deletionCountdown !== 'N/A' ? `${deletionCountdown} sec` : deletionCountdown}</td>
                </tr>
            `;
            tableBody.append(row);
        });

        // Initialize the DataTable after populating the table
        $('#ai-progress-table').DataTable({
            paging: true,
            stateSave: true,
            pageLength: 10,
            responsive: true,
            lengthMenu: [[10, 50, 100, 500, -1], [10, 50, 100, 500, 'All']],
            dom: 'rt<"container"<"row"<"col-md-6"li><"col-md-6"p>>>',
            order: [[0, 'asc']],  // Optionally sort by ID (or another column) by default
        });
    }
    get_update()
    setInterval(get_update, 1000);
});
