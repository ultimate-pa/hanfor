require('chart.js');
window.chartColors = {
            red: 'rgb(255, 99, 132)',
            orange: 'rgb(255, 159, 64)',
            yellow: 'rgb(255, 205, 86)',
            green: 'rgb(75, 192, 192)',
            blue: 'rgb(54, 162, 235)',
            purple: 'rgb(153, 102, 255)',
            grey: 'rgb(201, 203, 207)'
        };

$(document).ready(function () {
    statistics_request = $.get('api/stats/gets', function (data) {
        var processed_pie = new Chart(
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
                responsive: true
            }
        });
        var types_pie = new Chart(
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
                responsive: true
            }
        });
        var top_variables = new Chart(
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
                responsive: true
            }
        });
    });
});