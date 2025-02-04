require('gasparesganga-jquery-loading-overlay')
require('bootstrap')
require('datatables.net-bs5')
require('jquery-ui/ui/widgets/autocomplete')
require('jquery-ui/ui/effects/effect-highlight')
require('awesomplete')
require('awesomplete/awesomplete.css')
require('datatables.net-colreorder-bs5')


$(document).ready(function () {

    // region Data handling from API

    let ai_data;

    const updateFunctions = {
        ai_formalization: updateAIFormalization,
        ai_methods: updateAIMethods,
        ai_models: updateAIModels,
        ai_statistic: updateAIStatistic,
        ai_status: updateAIStatus,
        cluster_status: updateClusterStatus,
        clusters: updateClusters,
        flags: updateFlags,
        req_ids: updateRequestIDs,
        sim_methods: updateSimilarityMethods
    };

    // Helper function for the socket connection
    function updateAIData(newData) {
        for (const key in newData) {
            if (newData.hasOwnProperty(key)) {
                ai_data[key] = newData[key];

                // updating the corresponding section on the Web
                if (updateFunctions[key]) {
                    updateFunctions[key](newData[key]);
                }
            }
        }
    }

    // region Initial side load

    initial_side_data()
    waitForDataForInitialSideLoad()

    function initial_side_data(){
        $.ajax({
            type: 'Get',
            url: '/api/ai/get/data/initial',
            contentType: 'application/json'
        }).done(function (response){
            ai_data = response;
            console.debug(ai_data);
        })
    }

    function waitForDataForInitialSideLoad() {
        const checkInterval = setInterval(function() {
            if (ai_data) {
                clearInterval(checkInterval);
                updateAllUI();
            }
        }, 30);
    }

    function updateAllUI() {
        for (const key in updateFunctions) {
            if (updateFunctions.hasOwnProperty(key)) {
                updateFunctions[key]();
            }
        }
    }

    // endregion

    // endregion

    // region TEMP UNTIL SOCKET

    function temp_function_until_socket(){
        ai_data = null
        initial_side_data()
        temp_waitForDataForInitialSideLoad()
    }

    function temp_waitForDataForInitialSideLoad() {
        const checkInterval = setInterval(function() {
            if (ai_data) {
                clearInterval(checkInterval);
                temp_updateSome()
            }
        }, 30);
    }

    function temp_updateSome() {
        for (const key in updateFunctions) {
            if (updateFunctions.hasOwnProperty(key)) {
                updateFunctions[key]();
            }
        }
    }

    setInterval(temp_function_until_socket, 250);

    // endregion

    // region Updating Functions for the individual sections

    function updateAIFormalization() {
        // Destroy any existing DataTable before initializing a new one
        if ($.fn.dataTable.isDataTable('#ai-progress-table')) {
            $('#ai-progress-table').DataTable().clear().destroy();
        }
        const tableBody = $('#ai-progress-table tbody');
        tableBody.empty(); // Clear the table before adding new data

        // Iterate through the data and build table rows
        ai_data.ai_formalization.forEach(item => {
            // Safety check for each column and fallback logic
            const id = item.id || 'N/A';
            const promptDesc = item.prompt ? item.prompt : 'N/A';
            const status = item.status || 'N/A';
            const aiResponse = item.ai_response ? JSON.stringify(item.ai_response, null, 2) : 'N/A'; // Pretty formatted JSON
            const try_count = item.try_count || 'X';
            // Calculate the countdown for deletion, rounded to the next second
            const currentTime = Math.floor(Date.now() / 1000); // Current time in seconds
            const deletionCountdown = item.time ? Math.max(0, Math.ceil(ai_data.ai_formalization_deletion_time - (currentTime - item.time))) : 'N/A';

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

    function updateAIMethods() {
        const selectElement = $('#prompt-parsing-selection');
        selectElement.empty();

        ai_data.ai_methods.forEach(method => {
            const option = $('<option></option>')
                .attr('value', method.name)
                .text(`${method.name}: ${method.description}`)
                .prop('selected', method.selected);
            selectElement.append(option);
        });
    }

    function updateAIModels() {
        const selectElement = $('#ai-model-selection');
        selectElement.empty();

        ai_data.ai_models.forEach(model => {
            const option = $('<option></option>')
                .attr('value', model.name)
                .text(`${model.name}: ${model.description}`)
                .prop('selected', model.selected);
            selectElement.append(option);
        });
    }

    function updateAIStatistic() {
        let data = ai_data.ai_statistic
        const statistics_container = $('#ai-statistics-container');

        statistics_container.empty();

        data.ai_statistic?.forEach(stat => {
            const model = stat.model || 'N/A';
            const promptGen = stat.prompt_gen || 'N/A';
            const avgTryCount = stat.avg_try_count || 0;

            // Create a unique ID for each table
            const tableId = `ai-statistics-table-${model.replace(/\W/g, '-')}-${promptGen.replace(/\W/g, '-')}`;
            const sectionId = `section-${tableId}`;

            // Add a section for each model/prompt_gen with a heading and average try count
            const section = `
                <div class="ai-statistics-section" style="margin-bottom: 15px;">
                    <h6 
                        id="toggle-${tableId}" 
                        style="cursor: pointer; padding: 10px; background-color: #f1f1f1; border: 1px solid #ccc; border-radius: 5px; margin-bottom: 5px; font-weight: bold;">
                        ${model} - ${promptGen}
                        <span id="${tableId}-icon" style="float: right; color: #007bff;">[+]</span>
                    </h6>
                    <div id="${tableId}-content" style="display: none; padding: 10px; border: 1px solid #ccc; border-top: none; border-radius: 0 0 5px 5px;">
                        <p>Average Try Count: ${avgTryCount}</p>
                        <table class="display ai-statistics-table">
                            <thead>
                                <tr>
                                    <th>Status</th>
                                    <th>Total</th>
                                    <th>Percentage</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${stat.status_table.map(status => `
                                    <tr>
                                        <td>${status.status}</td>
                                        <td>${status.total}</td>
                                        <td>${status.percentage}%</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
            statistics_container.append(section);

            // Check if the section should be expanded or collapsed
            const isOpen = localStorage.getItem(sectionId) === 'open'; // Retrieve state from localStorage
            const content = document.getElementById(`${tableId}-content`);
            const icon = document.getElementById(`${tableId}-icon`);

            if (isOpen) {
                content.style.display = 'block';
                icon.textContent = '[-]';
            } else {
                content.style.display = 'none';
                icon.textContent = '[+]';
            }

            // Add the event listener to toggle the section
            const toggleButton = document.getElementById(`toggle-${tableId}`);
            toggleButton.addEventListener('click', () => toggleSection(sectionId, tableId));

            // Initialize DataTable for each table (apply only to <table> tags)
            $(`#${tableId}-content .ai-statistics-table`).DataTable({
                paging: false,
                searching: false,
                info: false,
                responsive: true,
                order: [[1, 'desc']], // Sort by Total descending
            });
        });

        // Function to toggle the section visibility and save the state
        function toggleSection(sectionId, tableId) {
            const content = document.getElementById(`${tableId}-content`);
            const icon = document.getElementById(`${tableId}-icon`);

            // Check the current display state and toggle accordingly
            if (content.style.display === 'none') {
                // Open the section
                content.style.display = 'block';
                icon.textContent = '[-]';
                localStorage.setItem(sectionId, 'open'); // Save state as open
            } else {
                // Close the section
                content.style.display = 'none';
                icon.textContent = '[+]';
                localStorage.setItem(sectionId, 'closed'); // Save state as closed
            }
        }

    }

    function updateAIStatus() {
        $('#ai-query').text(ai_data.ai_status.query || 'No query');
        $('#ai-queue-count').text(ai_data.ai_status.queued || 0);
        $('#ai-response').text(ai_data.ai_status.response || 'No response');
        $('#ai-running-count').text(ai_data.ai_status.running || 0);
    }

    function updateClusterStatus() {
        const processed = ai_data.cluster_status.processed || 0;
        const total = ai_data.cluster_status.total || 0;
        const status = ai_data.cluster_status.status || 'N/A';
        const percentage = (processed / (total|| 1)) * 100;
        $('#cluster-status').text(status);
        $('#cluster-availability').text(`${processed} / ${total || 0}`);
        $('#progress-bar').css('width', `${percentage}%`).attr('aria-valuenow', processed).text(`${processed}/${total}`);
    }

    function updateClusters() {
        const table_body = $('#cluster-table tbody');
        const table = $('#cluster-table');
        let data = ai_data.clusters

        // Destroy existing DataTable if it's initialized
        if ($.fn.dataTable.isDataTable(table)) {
            table.DataTable().clear().destroy();
        }

        // Clear the table body
        table_body.empty();

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
            table_body.append(row);
        });

        // Initialize DataTable after populating the table
        table.DataTable({
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
    }

    function updateFlags() {
        $('#toggle-system-switch').prop('checked', ai_data.flags.system).trigger('change');
        $('#toggle-ai-switch').prop('checked', ai_data.flags.ai).trigger('change');
    }

    function updateRequestIDs() {
        const dropdown = $('#idDropdown');
        dropdown.empty();

        ai_data.req_ids.forEach(id => {
            const option = $('<option></option>').attr('value', id).text(id);
            dropdown.append(option);
        });
    }

    function updateSimilarityMethods() {
        const selectElement = $('#clustering-process-select');
        selectElement.empty();

        const [threshold, methods] = ai_data.sim_methods;
        methods.forEach(method => {
            const option = $('<option></option>')
                .attr('value', method.name)
                .text(`${method.name}: ${method.description}`)
                .prop('selected', method.selected);
            selectElement.append(option);
        });

        // Slider-Update (Threshold anpassen)
        const selectedMethod = methods.find(m => m.selected);
        if (selectedMethod) {
            updateSliderRange(selectedMethod.interval[0], selectedMethod.interval[1], selectedMethod.default);
        }

        function updateSliderRange(minVal, maxVal, defaultVal) {
            const slider = $('#similarity-slider');
            slider.attr({ min: minVal, max: maxVal, step: (maxVal - minVal) / 200 });
            slider.val(defaultVal);
            $('#slider-value').text(defaultVal);
        }

    }

    // endregion

    // region UI Interaction Handlers

    // region Termination Handlers

    function terminateProcess(endpoint, successMessage) {
        $.ajax({
            type: 'POST',
            url: endpoint,
            contentType: 'application/json'
        }).done(function (data) {
            alert(successMessage || data.message);  // Show success message
        }).fail(function (jqXHR) {
            const errorMsg = jqXHR.responseText || 'An unknown error occurred.';
            alert(`Error: ${errorMsg}`);  // Show error message
        });
    }

    $('#terminate-all-button').click(function () {
        terminateProcess('/api/ai/terminate/all', 'All processes have been successfully terminated.');
    });

    $('#terminate-clustering-button').click(function () {
        terminateProcess('/api/ai/terminate/sim', 'Clustering process has been successfully terminated.');
    });

    $('#terminate-ai-button').click(function () {
        terminateProcess('/api/ai/terminate/ai', 'AI process has been successfully terminated.');
    });

    // endregion

    // region Toggle Switch Handlers

    function handleToggleSwitch(endpoint, key, newValue) {
        // Check if the new value is different from the current value in ai_data
        if (ai_data.flags[key] !== newValue) {
            $.ajax({
                type: 'POST',
                url: endpoint,
                contentType: 'application/json',
                data: JSON.stringify({ [`${key}_enabled`]: newValue })
            }).done(function () {
                // Update the ai_data to reflect the new state
                ai_data.flags[key] = newValue;
                console.log(`Successfully updated ${key} to ${newValue}`);
            }).fail(function (jqXHR) {
                const errorMsg = jqXHR.responseText || 'An error occurred while updating the setting.';
                alert(`Error: ${errorMsg}`);
            });
        } else {
            console.log(`No change detected for ${key}. No request sent.`);
        }
    }

    // Event handler for the System toggle switch
    $('#toggle-system-switch').on('change', function () {
        const isChecked = $(this).is(':checked');  // Returns a boolean
        handleToggleSwitch('/api/ai/set/flag/system', 'system', isChecked);
    });

    // Event handler for the AI toggle switch
    $('#toggle-ai-switch').on('change', function () {
        const isChecked = $(this).is(':checked');
        handleToggleSwitch('/api/ai/set/flag/ai', 'ai', isChecked);
    });

    // endregion

    // region Choosing Methods / Models

    function handleDropdownChange(endpoint, selectedValue) {
        $.ajax({
            type: 'POST',
            url: endpoint,
            contentType: 'application/json',
            data: JSON.stringify({ name: selectedValue }),
        }).done(function (response) {
            console.log(response.message);
        }).fail(function (error) {
            console.error("Error setting method/model:", error);
            alert('Failed to update selection. Please try again.');
        })
    }

    // Mapping dropdown IDs to their respective API endpoints
    const dropdownMappings = {
        '#clustering-process-select': '/api/ai/set/sim/method',
        '#prompt-parsing-selection': '/api/ai/set/ai/method',
        '#ai-model-selection': '/api/ai/set/ai/model'
    };

    // Attach change event handlers dynamically based on the mappings
    Object.keys(dropdownMappings).forEach(function (dropdownSelector) {
        $(dropdownSelector).on('change', function () {
            const selectedValue = $(this).val();
            const endpoint = dropdownMappings[dropdownSelector];
            handleDropdownChange(endpoint, selectedValue);
        });
    });

    // endregion

    // region Buttons (+ Slider) - POST Requests Only

    function handlePostRequest(endpoint, data = null, successCallback = null, errorCallback = null) {
        $.ajax({
            type: 'POST',
            url: endpoint,
            contentType: 'application/json',
            data: data ? JSON.stringify(data) : null
        })
        .done(function (response) {
            console.log(response.message);
            if (typeof successCallback === 'function') {
                successCallback(response);
            }
        })
        .fail(function (jqXHR) {
            const errorMessage = jqXHR.responseJSON?.error || jqXHR.responseText || 'An unknown error occurred.';
            console.error("Error:", errorMessage);
            if (typeof errorCallback === 'function') {
                errorCallback(errorMessage);
            }
        });
    }

    // Start Clustering Button
    $('#start-clustering').click(function () {
        handlePostRequest('/api/ai/set/sim/start');
    });

    // Process AI Button
    $('#process-ai').click(function () {
        handlePostRequest('/api/ai/ai/process');
    });

    // Submit Prompt Button
    $('#submit-prompt-button').click(function () {
        const userPrompt = $('#user-prompt').val();
        if (!userPrompt) {
            alert('Please enter a prompt!');
            return;
        }

        handlePostRequest('/api/ai/ai/query', { query: userPrompt },
            () => $('#ai-response').text('Processing your query...'),
            (error) => $('#ai-response').text(`Error: ${error}`)
        );
    });

    // Submit IDs Button
    $('#submit-ids-button').click(function () {
        const idsInput = $('#id-input').val().trim();
        if (!idsInput) {
            alert('Please enter at least one ID!');
            return;
        }

        handlePostRequest('/api/ai/set/ids', { ids: idsInput },
            null,
            (error) => alert(error)
        );
    });

    // Similarity Slider Change
    $('#similarity-slider').on('change', function () {
        const thresholdValue = $(this).val();
        $('#slider-value').text(thresholdValue);

        handlePostRequest('/api/ai/set/sim/threshold', { threshold: thresholdValue },
            (response) => console.log(response.message),
            (error) => console.error("Error setting threshold:", error)
        );
    });

    // endregion

    // region Similarity Matrix and Log Dropdown IDs

    function handleGetRequest(endpoint, successCallback, errorCallback) {
        $.ajax({
            type: 'GET',
            url: endpoint,
            contentType: 'application/json'
        }).done(successCallback)
          .fail(errorCallback);
    }

    // region Similarity Matrix

    // Fetch and Display Similarity Matrix
    $('#get-matrix-button').click(function () {
        handleGetRequest('/api/ai/get/sim/matrix', renderSimilarityMatrix, clearMatrixTable);
    });

    function renderSimilarityMatrix(matrixData) {
        const table = document.getElementById("similarity-matrix");
        const thead = table.querySelector("thead");
        const tbody = table.querySelector("tbody");

        thead.innerHTML = '';
        tbody.innerHTML = '';

        const { matrix, indexing } = matrixData;

        // Create table header
        const headerRow = document.createElement("tr");
        headerRow.appendChild(document.createElement("th")); // Empty top-left cell
        Object.keys(indexing).forEach(key => {
            const th = document.createElement("th");
            th.textContent = key;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);

        // Create table rows with data
        Object.keys(indexing).forEach((rowKey, rowIndex) => {
            const row = document.createElement("tr");
            const th = document.createElement("th");
            th.textContent = rowKey;
            row.appendChild(th);

            matrix[rowIndex].forEach(value => {
                const td = document.createElement("td");
                td.textContent = value.toFixed(2);
                td.style.backgroundColor = calculateHeatmapColor(value);
                row.appendChild(td);
            });

            tbody.appendChild(row);
        });
    }

    // Clears the similarity matrix table in case of an error.
    function clearMatrixTable() {
        const table = document.getElementById("similarity-matrix");
        table.querySelector("thead").innerHTML = '';
        table.querySelector("tbody").innerHTML = '';
        alert('Failed to load similarity matrix.');
    }

    function calculateHeatmapColor(value) {
        const baseValue = ai_data.sim_methods[0];
        const distance = Math.abs(value - baseValue);
        const alpha = 0.3 + (distance * 0.4); // Scale to an alpha value between 0.3 and 0.7

        return value >= baseValue
            ? `rgba(0, 0, 180, ${Math.min(alpha, 0.7)})`  // Blue for higher values
            : `rgba(0, 180, 0, ${Math.min(alpha, 0.7)})`; // Green for lower values
    }

    // endregion

    // region Log Dropdown IDs

    // Dynamic Dropdown Update Based on Search
    function updateDropdown(filter = '') {
        const dropdown = document.getElementById('idDropdown');
        dropdown.innerHTML = '';

        const filteredIDs = ai_data.req_ids.filter(id => id.toLowerCase().includes(filter.toLowerCase()));

        filteredIDs.forEach(id => {
            const option = document.createElement('option');
            option.value = id;
            option.textContent = id;
            dropdown.appendChild(option);
        });

        if (filteredIDs.length === 0) {
            const noResult = document.createElement('option');
            noResult.textContent = 'No matching IDs';
            noResult.disabled = true;
            dropdown.appendChild(noResult);
        }
    }

    // Search Input Event for Filtering IDs
    $('#idSearch').on('input', function () {
        updateDropdown($(this).val());
    });

    // Fetch and Display Log Data for Selected ID
    $('#idDropdown').on('change', function () {
        const selectedID = $(this).val();
        handleGetRequest(`/api/ai/set/log/id?id=${selectedID}`,
            (response) => renderLogData(selectedID, response.data),
            () => alert('Failed to fetch log data for the selected ID.')
        );
    });

    function renderLogData(selectedID, logData) {
        let logHtml = `<h3>Log for ID: ${selectedID}</h3>`;

        const sortedEntries = Object.entries(logData).sort((a, b) => {
            const numA = parseInt(a[0].split('_').pop());
            const numB = parseInt(b[0].split('_').pop());
            return numA - numB;
        });

        sortedEntries.forEach(([time, data]) => {
            logHtml += `
                <div class="log-entry">
                    <p><strong>Time:</strong> ${time}</p>
            `;
            Object.entries(data).forEach(([key, value]) => {
                logHtml += `<p><strong>${key}:</strong> ${value}</p>`;
            });
            logHtml += `</div><hr>`;
        });

        $('#log-container').html(logHtml);
    }

    // endregion

    // endregion

    // endregion

});