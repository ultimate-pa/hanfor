$(document).ready(function () {
    // Helper function to display output in the <pre> element
    function updateOutput(content) {
        $('#output-content').text(content);
    }

    // Event listener for the Terminate AI button
    $('#terminate-ai-button').click(function () {
        $.ajax({
            type: 'POST',
            url: '/api/ai/terminate_ai',
            contentType: 'application/json'
        }).done(function (data) {
            alert(data.message);  // Show a popup alert with the response message
            updateOutput(JSON.stringify(data, null, 2));  // Display response in the <pre> element
        }).fail(function (jqXHR) {
            alert(`Error: ${jqXHR.responseText}`);  // Show error alert
            updateOutput(jqXHR.responseText);
        });
    });

    // Event listener for the Terminate Clustering button
    $('#terminate-clustering-button').click(function () {
        $.ajax({
            type: 'POST',
            url: '/api/ai/terminate_clustering',
            contentType: 'application/json'
        }).done(function (data) {
            alert(data.message);  // Show a popup alert with the response message
            updateOutput(JSON.stringify(data, null, 2));
        }).fail(function (jqXHR) {
            alert(`Error: ${jqXHR.responseText}`);  // Show error alert
            updateOutput(jqXHR.responseText);
        });
    });

    // Event listener for the Get Cluster Data button
    $('#get-cluster-button').click(function () {
        $.ajax({
            type: 'GET',
            url: '/api/ai/cluster',
            contentType: 'application/json'
        }).done(function (data) {
            console.log(data); // Debugging: check the API response in the console
            populateTable(data); // Populate the table with received data
        }).fail(function (jqXHR) {
            alert(`Error: ${jqXHR.responseText}`);  // Show error alert
            updateOutput(jqXHR.responseText);
        });
    });

    // Event listener for the Get AI Progress button
    $('#get-ai-progress-button').click(function () {
        $.ajax({
            type: 'GET',
            url: '/api/ai/ai_progress',
            contentType: 'application/json'
        }).done(function (data) {
            updateOutput(JSON.stringify(data, null, 2));
        }).fail(function (jqXHR) {
            alert(`Error: ${jqXHR.responseText}`);
            updateOutput(jqXHR.responseText);
        });
    });

    // Event listener for the Start Clustering button
    $('#start-clustering').click(function () {
        $.ajax({
            type: 'POST',
            url: '/api/ai/start_clustering',
            contentType: 'application/json'
        }).done(function (data) {
            updateOutput(JSON.stringify(data, null, 2));
        }).fail(function (jqXHR) {
            updateOutput(jqXHR.responseText);
        });
    });

    // Function to check the progress of the clustering process
    function checkProgress() {
        $.ajax({
            type: 'GET',
            url: '/api/ai/cluster_progress',
            contentType: 'application/json'
        }).done(function (data) {
            const processed = data.processed;
            const total = data.total;
            const status = data.status;

            // Update the progress bar and status text
            $('#progress-status').text(`Status: ${status}`);
            $('#progress-bar').css('width', `${(processed / total) * 100}%`);
            $('#progress-bar').attr('aria-valuenow', processed);
            $('#progress-bar').text(`${processed}/${total}`);

            console.log(`Progress: ${processed}/${total} (Status: ${status})`);
        }).fail(function (jqXHR) {
            alert(`Error: ${jqXHR.responseText}`);
            $('#progress-bar').css('width', '0%');
            $('#progress-bar').text('0/0');
            $('#progress-status').text('Status: Error');
        });
    }

    // Function to populate the table with cluster data
    function populateTable(data) {
        console.log("Received data:", data); // Debugging: check the received data

        if (!Array.isArray(data)) {
            console.error("The API response is not in the expected format.");
            return;
        }

        const TABLE_BODY = $('#cluster-table tbody');
        TABLE_BODY.empty(); // Clear existing table content

        // Sort clusters by the smallest ID in each cluster
        data.sort((a, b) => {
            const minIdA = a.map(id => (id ? id.toString() : '')).sort()[0];
            const minIdB = b.map(id => (id ? id.toString() : '')).sort()[0];
            return minIdA.localeCompare(minIdB);
        });

        // Iterate over each cluster and populate the table
        data.forEach((ids) => {
            if (!Array.isArray(ids)) {
                console.error("A cluster has an invalid structure:", ids);
                return; // Skip clusters without valid IDs
            }

            // Sort IDs within the cluster lexicographically
            ids.sort((a, b) => a.localeCompare(b));
            const clusterName = `Cluster ${ids[0]}`;

            const tr = $('<tr></tr>');
            const clusterNameCell = `<td>${clusterName}</td>`;

            // Generate the IDs as links
            const idsHtml = ids.map(id =>
                `<span class="badge bg-info">
                    <a href="${base_url}?command=search&col=2&q=%5C%22${id}%5C%22" target="_blank" class="link-light">${id}</a>
                </span>`
            ).join(' ');

            // Generate combined search query for all IDs
            const searchQuery = ids.map(id => `%5C%22${id}%5C%22`).join('%3AOR%3A');

            // Add "Show all" link if there are multiple IDs
            const showAllLink = ids.length > 1
                ? `<span class="badge bg-info">
                    <a href="${base_url}?command=search&col=2&q=${searchQuery}" target="_blank" class="link-light">Show all</a>
                </span>`
                : '';

            tr.append(clusterNameCell);
            tr.append(`<td>${idsHtml} ${showAllLink}</td>`); // Add IDs and "Show all" link
            TABLE_BODY.append(tr);
        });
    }

    function fetchAndDisplayProgress() {
        $.get('/api/ai/ai_progress').done(function (data) {
            const tableBody = $('#ai-progress-table tbody');
            tableBody.empty(); // Leere die Tabelle vor dem Hinzufügen neuer Daten

            data.forEach(item => {
                // Sicherheitsüberprüfung für jede Spalte und Fallback-Logik
                const id = item.id || 'N/A';
                const promptDesc = item.prompt ? item.prompt : 'N/A';
                const status = item.status || 'N/A';
                const aiResponse = item.ai_response ? JSON.stringify(item.ai_response, null, 2) : 'N/A'; // Formatiertes JSON

                // Berechnung des Countdowns für die Löschung, auf die nächste Sekunde gerundet
                const currentTime = Math.floor(Date.now() / 1000); // Aktuelle Zeit in Sekunden
                const deletionCountdown = item.time ? Math.max(0, Math.ceil(9 - (currentTime - item.time))) : 'N/A';

                // Erstellen der Tabellenzeile mit einer zusätzlichen Spalte für den Countdown
                const row = `
                    <tr id="row-${id}">
                        <td>${id}</td>
                        <td>${promptDesc}</td>
                        <td>${status}</td>
                        <td>${aiResponse}</td>
                        <td id="countdown-${id}">${deletionCountdown !== 'N/A' ? `${deletionCountdown} sec` : deletionCountdown}</td>
                    </tr>
                `;
                tableBody.append(row);
            });

        });
    }

    setInterval(checkProgress, 50);
    setInterval(fetchAndDisplayProgress, 50);
});
