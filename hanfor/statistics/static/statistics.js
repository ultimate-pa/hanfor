require('bootstrap')
require('../../telemetry/static/telemetry')
const cytoscape = require('cytoscape')
const fcose = require('cytoscape-fcose')
const download = require('downloadjs')
const {Chart, registerables} = require('chart.js')

cytoscape.use(fcose)
Chart.register(...registerables)

window.chartColors = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(201, 203, 207)'
};

let dynamicColors = function () {
    const r = Math.floor(Math.random() * 255);
    const g = Math.floor(Math.random() * 255);
    const b = Math.floor(Math.random() * 255);
    return "rgb(" + r + "," + g + "," + b + ")";
};

$(document).ready(function () {


    $.ajax({
        type: 'GET', url: 'api/statistics/', contentType: 'application/json'
    }).done(function (data, textStatus, jqXHR) {
        // Processed requirements pie
        new Chart(
            document.getElementById("processed_pie").getContext('2d'),
            {
                type: 'pie',
                data: {
                    datasets: [{
                        data: [data.todo, data.review, data.done],
                        backgroundColor: [
                            window.chartColors.red,
                            window.chartColors.orange,
                            window.chartColors.green
                        ],
                        label: 'Processed requirements.'
                    }],

                    // These labels appear in the legend and in the tooltips when hovering different arcs
                    labels: [
                        'Todo',
                        'Review',
                        'Done'
                    ]
                },
                options: {
                    responsive: true,
                    show_total: true
                }
            });

        // Tags per type statistics
        let tags_per_type_div = $('#tags_per_type');
        let count = 0;
        $.each(data["tags_per_type"], function (req_type, item) {
            const tag_count = Object.keys(item).length;
            count += 1;

            if (tag_count > 0) {
                $('<div class="col-lg-6 col-md-12">' +
                    '<div class="card"><div class="card-body">' +
                    '<h5 class="card-title">Type: ' + req_type + '</h5>' +
                    '<canvas id="tags_per_type_' + count + '" width="50%"></canvas>' +
                    '</div></div></div>').appendTo(tags_per_type_div);

                let tag_counts = [];
                let tag_names = [];
                let tag_colors = [];
                $.each(item, function (tag_name, tag_count) {
                    tag_names.push(tag_name);
                    tag_counts.push(tag_count);
                    tag_colors.push(dynamicColors());
                });
                new Chart(
                    document.getElementById("tags_per_type_" + count).getContext('2d'),
                    {
                        type: 'pie',
                        data: {
                            datasets: [{
                                data: tag_counts,
                                backgroundColor: tag_colors,
                                label: 'Tag names.'
                            }],
                            labels: tag_names
                        },
                        options: {
                            responsive: true,
                            show_total: true
                        }
                    });
            }
        });

        // Status per type statistics
        let status_per_type_div = $('#status_per_type');
        count = 0;
        $.each(data["status_per_type"], function (req_type, item) {
            const tag_count = Object.keys(item).length;
            count += 1;

            if (tag_count > 0) {
                $('<div class="col-lg-6 col-md-12">' +
                    '<div class="card"><div class="card-body">' +
                    '<h5 class="card-title">Type: ' + req_type + '</h5>' +
                    '<canvas id="status_per_type_' + count + '" width="50%"></canvas>' +
                    '</div></div></div>').appendTo(status_per_type_div);

                let status_counts = [];
                let status_names = [];
                let status_colors = [];
                $.each(item, function (tag_name, tag_count) {
                    status_names.push(tag_name);
                    status_counts.push(tag_count);
                    status_colors.push(dynamicColors());
                });
                new Chart(
                    document.getElementById("status_per_type_" + count).getContext('2d'),
                    {
                        type: 'pie',
                        data: {
                            datasets: [{
                                data: status_counts,
                                backgroundColor: status_colors,
                                label: 'Tag names.'
                            }],
                            labels: status_names
                        },
                        options: {
                            responsive: true,
                            show_total: true
                        }
                    });
            }
        });

        // Types Statistics
        new Chart(
            document.getElementById("requirement_types").getContext('2d'),
            {
                type: 'pie',
                data: {
                    datasets: [{
                        data: data.type_counts,
                        backgroundColor: data.type_colors,
                        label: 'Requirement types.'
                    }],
                    labels: data.type_names
                },
                options: {
                    responsive: true,
                    show_total: true
                }
            });

        // Most used Variables statistics
        new Chart(
            document.getElementById("top_variables").getContext('2d'),
            {
                type: 'polarArea',
                data: {
                    datasets: [{
                        data: data.top_variables_counts,
                        backgroundColor: data.top_variable_colors,
                        label: 'Top 10 used variables.'
                    }],
                    labels: data.top_variable_names
                },
                options: {
                    responsive: true,
                    show_total: true
                }
            });

        // cytoscape variable graph.
        var varReqGraph = cytoscape({
            container: $('#cy'),

            layout: {
                name: 'fcose',
                quality: "proof",
                // Use random node positions at beginning of layout
                // if this is set to false, then quality option must be "proof"
                randomize: true,
                // Whether or not to animate the layout
                animate: false,
                // Fit the viewport to the repositioned nodes
                fit: true,
                // Padding around layout
                padding: 30,
                // Whether or not simple nodes (non-compound nodes) are of uniform dimensions
                uniformNodeDimensions: false,

                avoidOverlap: true, // prevents node overlap, may overflow boundingBox if not enough space
                avoidOverlapPadding: 100, // extra spacing around nodes when avoidOverlap: true
                nodeDimensionsIncludeLabels: true, // Excludes the label when calculating node bounding boxes for the layout algorithm
                spacingFactor: undefined,

                // False for random, true for greedy sampling
                samplingType: false,
                // Sample size to construct distance matrix
                sampleSize: 25,
                // Separation amount between nodes
                nodeSeparation: 400,
                // Power iteration tolerance
                piTol: 0.0000001,

                /* incremental layout options */

                // Node repulsion (non overlapping) multiplier
                nodeRepulsion: function (node) {
                    return node._private.data.calculatedrepulsion;
                },
                // Ideal edge (non nested) length
                idealEdgeLength: function (edge) {
                    return edge._private.data.calculatedlength;
                },
                // Divisor to compute edge forces
                edgeElasticity: function (edge) {
                    return edge._private.data.calculatedelasticity;
                },
                // Nesting factor (multiplier) to compute ideal edge length for nested edges
                nestingFactor: 0.1,
                // Maximum number of iterations to perform - this is a suggested value and might be adjusted by the algorithm as required
                numIter: 5000,
                // For enabling tiling
                tile: true,
                // Represents the amount of the vertical space to put between the zero degree members during the tiling operation(can also be a function)
                tilingPaddingVertical: 1000,
                // Represents the amount of the horizontal space to put between the zero degree members during the tiling operation(can also be a function)
                tilingPaddingHorizontal: 1000,
                // Gravity force (constant)
                gravity: 0.25,
                // Gravity range (constant) for compounds
                gravityRangeCompound: 1.5,
                // Gravity force (constant) for compounds
                gravityCompound: 1.0,
                // Gravity range (constant)
                gravityRange: 3.8,
                // Initial cooling factor for incremental layout
                initialEnergyOnIncremental: 0.3,
            },

            elements: data.variable_graph,
            wheelSensitivity: 0.05,

            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': 'data(color)',
                        'label': 'data(id)',
                        'height': 'data(size)',
                        'font-size': 10,
                        'width': 'data(size)'
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': '5px',
                        'line-color': 'data(color)',
                        'curve-style': 'heystack',
                        'haystack-radius': '0',
                        'opacity': '0.4',
                        'overlay-padding': '3px'
                    }
                }
            ]
        });

        $("#save-graph").click(function () {
                var png64 = varReqGraph.png({full: true, scale: 1});
                download(png64, "requirementgraph.png", "image/png")
            }
        )
    }).fail(function (jqXHR, textStatus, errorThrown) {
        console.log('jqXHR:', jqXHR, 'textStatus:', textStatus, 'errorThrown:', errorThrown)
        alert(errorThrown + '\n\n' + jqXHR['responseText'])
    })
});