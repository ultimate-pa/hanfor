const cytoscape = require('cytoscape')
const {Chart, registerables} = require('chart.js')

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

/*
Chart.plugins.register({
    afterInit: function (chart) {
        if (chart.config.options.show_total) {
            //Get ctx from string
            let counts = chart.config.data.datasets[0].data;
            const total_count = counts.reduce((l, r) => l + r, 0);
            chart.config.options.title = {
                display: true,
                position: 'bottom',
                text: 'Total count: ' + total_count
            };
        }
    }
});
*/

$(document).ready(function () {
    $.get('api/stats/gets', function (result) {
        const data = result.data;
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
        cytoscape({
            container: $('#cy'),

            layout: {
                name: 'cose',
                idealEdgeLength: 150,
                nodeOverlap: 40,
                refresh: 20,
                fit: true,
                padding: 30,
                randomize: false,
                componentSpacing: 100,
                nodeRepulsion: 400000,
                edgeElasticity: 100,
                nestingFactor: 5,
                gravity: 80,
                numIter: 1000,
                initialTemp: 200,
                coolingFactor: 0.95,
                minTemp: 1.0
            },

            elements: data.variable_graph,

            wheelSensitivity: 0.05,

            style: [ // the stylesheet for the graph
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
                        "curve-style": "bezier",
                        "haystack-radius": "0.5",
                        "opacity": "0.4",
                        "line-color": "data(color)",
                        "width": "2px",
                        "overlay-padding": "3px"
                    }
                }
            ]
        });
    });
});