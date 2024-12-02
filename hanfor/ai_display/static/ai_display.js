require('bootstrap');
const bootstrap = require('bootstrap');

$(document).ready(function () {
    const PROGRESS_BAR = $('#clustering-progress-bar');
    const CLUSTERING_BUTTON = $('#start-clustering-button');

    // Function to update the progress bar
    function updateProgressBar(current, total) {
        const percentage = Math.round((current / total) * 100);
        PROGRESS_BAR.css('width', percentage + '%');
        PROGRESS_BAR.attr('aria-valuenow', percentage);
        PROGRESS_BAR.text(`${current}/${total} (${current} of ${total} completed)`);
    }

    // Function to check the progress of the clustering process
    function checkProgress() {
        $.get('/api/ai_display?type=progress').done(function (progress) {
            // Update the progress bar with current status
            updateProgressBar(progress.processed, progress.total);

            // Update the status display with the current status
            document.getElementById('statusDisplay').innerText = `Status: ${progress.status.charAt(0).toUpperCase() + progress.status.slice(1)}`;

            // Check if the clustering process is complete
            if (progress.status === "completed") {
                if (localStorage.getItem("clusteringCompleted") !== "true") {
                    // Mark clustering as completed in local storage
                    localStorage.setItem("clusteringCompleted", "true");
                    loadTableData(); // Load table data when clustering is complete
                    CLUSTERING_BUTTON.prop('disabled', false); // Enable the button
                    setTimeout(() => {
                        alert('Clustering completed!');
                    }, 500); // Delay to allow the UI to update before showing the alert
                } else {
                    // If already completed, just enable the button
                    CLUSTERING_BUTTON.prop('disabled', false);
                }
            } else if (["clustering", "pending", "extracting"].includes(progress.status)) {
                resetClusteringStatus();
                CLUSTERING_BUTTON.prop('disabled', true); // Disable the button during processing
                setTimeout(checkProgress, 50); // Check progress again after a short delay
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.error('Error fetching progress:', textStatus, errorThrown);
        });
    }

    // Function to reset the clustering status in local storage
    function resetClusteringStatus() {
        localStorage.removeItem("clusteringCompleted");
    }

    // Event handler for the clustering button click
    CLUSTERING_BUTTON.click(function () {
        $.ajax({
            type: 'POST',
            url: '/api/ai_display',
            contentType: 'application/json',
            data: JSON.stringify({ action: 'start_clustering' })
        }).done(function (response) {
            resetClusteringStatus();
            console.log('Clustering started:', response);
            CLUSTERING_BUTTON.prop('disabled', true); // Disable the button after starting clustering
            checkProgress(); // Start checking the progress
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.error('Error:', textStatus, errorThrown);
            alert('Clustering could not be started.');
        });
    });

    // Helper function to generate a search query for IDs
    function generateSearchQuery(ids) {
        return ids.map(id => `%5C%22${id}%5C%22`).join('%3AOR%3A');
    }

    // Function to populate the table with cluster data
    function populateTable(data) {
        const TABLE_BODY = $('#cluster-table tbody');
        TABLE_BODY.empty(); // Clear existing table content

        // Sort clusters by the lexicographically smallest ID in each cluster
        data.clusters.sort((a, b) => {
            const minIdA = a.ids.sort()[0]; // Get the lexicographically smallest ID in cluster A
            const minIdB = b.ids.sort()[0]; // Get the lexicographically smallest ID in cluster B
            return minIdA.localeCompare(minIdB);
        });

        data.clusters.forEach(cluster => {
            // Sort the IDs within the cluster lexicographically
            cluster.ids.sort((a, b) => a.localeCompare(b));

            // Rename the cluster based on the smallest ID
            cluster.name = `Cluster ${cluster.ids[0]}`; // Set the name based on the smallest ID

            const tr = $('<tr></tr>');
            const clusterName = `<td>${cluster.name}</td>`; // Display the new name

            // Generate the IDs as links
            const idsHtml = cluster.ids.map(id =>
                `<span class="badge bg-info">
                    <a href="${base_url}?command=search&col=2&q=%5C%22${id}%5C%22" target="_blank" class="link-light">${id}</a>
                </span>`
            ).join(' ');

            // Generate the combined search query for all IDs
            const searchQuery = generateSearchQuery(cluster.ids);

            // Add "Show all" link if there are multiple IDs
            const showAllLink = cluster.ids.length > 1
                ? `<span class="badge bg-info">
                    <a href="${base_url}?command=search&col=2&q=${searchQuery}" target="_blank" class="link-light">Show all</a>
                </span>`
                : '';

            // Append rows to the table
            tr.append(clusterName);
            tr.append(`<td>${idsHtml} ${showAllLink}</td>`); // Add formatted IDs with "Show all" link if applicable
            TABLE_BODY.append(tr);
        });
    }



    // Function to load table data from the API
    function loadTableData() {
        $.get('/api/ai_display?type=clusters').done(function (data) {
            if (data.clusters) {
                populateTable(data); // Populate the table with received data
                checkProgress(); // Continue checking the progress
            } else {
                console.error('Unexpected response format:', data);
            }
        }).fail(function (jqXHR) {
            console.error('Error loading table data:', jqXHR.responseText);
        });
    }

    // Initial load of table data and progress check
    loadTableData();
    checkProgress();
});
