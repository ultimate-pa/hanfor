require('chart.js/auto')
require('jquery-ui-sortable')
require('../css/floating-labels.css') // TODO: Remove in Bootstrap version >= 5.1

function get_selected_requirement_ids(requirements_table) {
    let ids = []
    requirements_table.DataTable().rows({selected: true}).every(function () {
        ids.push(this.data()['id'])
    })

    return ids
}

function update_simulator_select(simulator_select) {
    $.ajax({
        // TODO: Allow async.
        type: 'GET', url: 'simulator', async: false, data: {command: 'get_simulators'}, success: function (response) {
            if (response['success'] === false) {
                alert(response['errormsg'])
                return
            }

            simulator_select.empty()
            $.each(response['data']['simulators'], function (index, value) {
                simulator_select.append($('<option></option>').val(index).text(value + ' (' + index + ')'))
            })
        }
    })
}

function init_simulator_tab() {
    let simulator_name_input = $('#simulator-name-input')
    let simulator_select = $('#simulator-select')
    let simulator_create_btn = $('#simulator-create-btn')
    let simulator_delete_btn = $('#simulator-delete-btn')
    let simulator_start_btn = $('#simulator-start-btn')
    let requirements_table = $('#requirements_table')

    update_simulator_select(simulator_select)

    simulator_create_btn.click(function () {
        $.ajax({
            // TODO: Allow async.
            type: 'POST', url: 'simulator', async: false, data: {
                command: 'create_simulator',
                simulator_name: simulator_name_input.val() || 'unnamed',
                requirement_ids: JSON.stringify(get_selected_requirement_ids(requirements_table))
            }, success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                let id = response['data']['simulator_id']
                let name = response['data']['simulator_name']
                simulator_select.prepend($('<option></option>').val(id).text(name + ' (' + id + ')'))
                simulator_select.prop('selectedIndex', 0)
            }
        })
    })

    simulator_delete_btn.click(function () {
        $.ajax({
            // TODO: Allow async.
            type: 'DELETE', url: 'simulator', async: false, data: {
                command: 'delete_simulator', simulator_id: simulator_select.val()
            }, success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                update_simulator_select(simulator_select)
            }
        });
    });

    simulator_start_btn.click(function () {
        $.ajax({
            // TODO: Allow async.
            type: 'GET', url: 'simulator', async: false, data: {
                command: 'start_simulator', simulator_id: simulator_select.val()
            }, success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                init_simulator_modal(response['data'])
            }
        })
    })
}

function init_simulator_modal(data) {
    let simulator_id = data['simulator_id']
    let times = data['times']
    let variables = data['variables']
    let active_dc_phases = data['active_dc_phases']
    let types = data['types']
    let models = data['models']

    let simulator_modal = $(data['html'])
    let simulator_chart_canvas = simulator_modal.find('#chart-canvas')
    let simulator_step_transition_select = simulator_modal.find('#simulator-step-transition-select')
    let simulator_step_check_btn = simulator_modal.find('#simulator-step-check-btn')
    let simulator_step_next_btn = simulator_modal.find('#simulator-step-next-btn')
    let simulator_step_back_btn = simulator_modal.find('#simulator-step-back-btn')

    let variable_inputs = {}
    $.each(simulator_modal.find('input[id$=_variable]'), function (index, value) {
        id = $(value).attr('id').replace('_variable', '')
        variable_inputs[id] = $(value)
    })

    update_variable_inputs(variable_inputs, variables)

    let dc_phase_codes = {}
    $.each(simulator_modal.find('code[id$=_dc_phase]'), function (index, value) {
        id = $(value).attr('id').replace('_dc_phase', '')
        dc_phase_codes[id] = $(value)
    })

    update_dc_phases(dc_phase_codes, active_dc_phases)

    let chart = init_chart(simulator_chart_canvas, times, models, types)

    simulator_step_check_btn.click(function () {
        $.ajax({
            // TODO: Allow async.
            type: 'POST', url: 'simulator', async: false, data: {
                command: 'step_check',
                simulator_id: simulator_id,
                variables: JSON.stringify(read_variable_inputs(variable_inputs))
            }, success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                simulator_step_transition_select.empty()
                $.each(response['data']['transitions'], function (index, value) {
                    simulator_step_transition_select.append($('<option></option>').val(index).text(value).addClass('text-break'))
                })
            }
        })
    })

    simulator_step_next_btn.click(function () {
        $.ajax({
            // TODO: Allow async.
            type: 'POST', url: 'simulator', async: false, data: {
                command: 'step_next',
                simulator_id: simulator_id,
                transition_id: simulator_step_transition_select.val()
            }, success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                simulator_step_transition_select.empty()

                times = response['data']['times']
                variables = response['data']['variables']
                update_variable_inputs(variable_inputs, variables)

                active_dc_phases = response['data']['active_dc_phases']
                update_dc_phases(dc_phase_codes, active_dc_phases)

                addData(chart, times, response['data']['models'])

                //chart.options.scales.y_blinkingMode.stackWeight = 0
                //chart.options.scales.y_blinkingMode.display = false
                //chart.update();
            }
        })
    })

    simulator_step_back_btn.click(function () {
        $.ajax({
            // TODO: Allow async.
            type: 'POST', url: 'simulator', async: false, data: {
                command: 'step_back', simulator_id: simulator_id
            }, success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                simulator_step_transition_select.empty()

                times = response['data']['times']
                variables = response['data']['variables']
                update_variable_inputs(variable_inputs, variables)

                active_dc_phases = response['data']['active_dc_phases']
                update_dc_phases(dc_phase_codes, active_dc_phases)

                removeData(chart)

                //chart.options.scales.y_blinkingMode.stackWeight = 1
                //chart.options.scales.y_blinkingMode.display = true
                //chart.update();
            }
        })
    })

    simulator_modal.find('#simulator-countertraces-accordion').sortable();
    simulator_modal.find('#simulator-variables-form-row').sortable();

    simulator_modal.modal('show')
}

function init_chart(chart_canvas, times, models, types) {
    let scales = {}
    let datasets = []

    $.each(types, function (index, value) {
        let color = generateRandomColor()

        const type = types[index] === 'Bool' ? 'category' : 'linear'
        const labels = types[index] === 'Bool' ? ['True', 'False'] : []
        models[index][0] = types[index] === 'Bool' ? 'False' : '0'

        scales['y_' + index] = {
            type: type,
            labels: labels,
            offset: true,
            stack: 'demo',
            stackWeight: 1,
            grid: {
                borderDash: [4, 6]
            }
        }

        datasets.push({
            label: index,
            backgroundColor: color,
            borderColor: color,
            data: models[index],
            stepped: 'after',
            yAxisID: 'y_' + index,
        })
    })

    const data = {
        labels: times,
        datasets: datasets
    }

    const config = {
        type: 'line',
        data: data,
        options: {
            scales: Object.assign(
                {},
                scales,
                {
                    x: {
                        grid: {
                            borderDash: [4, 6]
                        }
                    }
                }),
            borderWidth: 1,
            plugins: {
                legend: {
                    position: 'top',
                    align: 'start',
                    onClick: onChartLegendClick
                },
                chartAreaBorder: {
                    borderColor: 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 2
                },
            }
        },
        plugins: [
            {
                id: 'chartAreaBorder',
                beforeDraw(chart, args, options) {
                    const {ctx, chartArea: {left, top, width, height}} = chart;
                    ctx.save();
                    ctx.strokeStyle = options.borderColor;
                    ctx.lineWidth = options.borderWidth;
                    ctx.setLineDash(options.borderDash || []);
                    ctx.lineDashOffset = options.borderDashOffset;
                    ctx.strokeRect(left, top, width, height);
                    ctx.restore();
                }
            }
        ]
    }

    const ctx = chart_canvas[0].getContext('2d')
    return new Chart(ctx, config)
}

const getOrCreateLegendList = (chart, id) => {
    const legendContainer = document.getElementById(id);
    let listContainer = legendContainer.querySelector('ul');

    if (!listContainer) {
        listContainer = document.createElement('ul');
        listContainer.style.display = 'flex';
        listContainer.style.flexDirection = 'row';
        listContainer.style.margin = 0;
        listContainer.style.padding = 0;

        legendContainer.appendChild(listContainer);
    }

    return listContainer;
};


function onChartLegendClick(evt, item, legend) {
    //console.log('evt', evt)
    //console.log('item', item)
    //console.log('legend', legend)

    const chart = legend.chart
    const y_scale = chart.options.scales['y_' + item.text]

    $.each(chart.data.datasets, function (index, value) {
        if (value.yAxisID === 'y_' + item.text) {

            if (value.hidden === false) {
                value.hidden = true
                y_scale.display = false
                y_scale.stackWeight = 0.0000000000001
            } else {
                value.hidden = false
                y_scale.display = true
                y_scale.stackWeight = 1
            }
            console.log('found', item.text)
        }
    })

    chart.update();
}

function addData(chart, times, models) {
    chart.data.labels.push(times[times.length - 1])

    chart.data.datasets.forEach((dataset) => {
        const label = dataset.label
        dataset.data.push(models[label][models[label].length - 1])

        console.log(label, models[label][models[label].length - 1])
    })

    chart.update()
}

function removeData(chart) {
    chart.data.labels.pop()

    chart.data.datasets.forEach((dataset) => {
        dataset.data.pop()
    })

    chart.update()
}

function dynamicColor() {
    const r = Math.floor(Math.random() * 255)
    const g = Math.floor(Math.random() * 255)
    const b = Math.floor(Math.random() * 255)
    return "rgb(" + r + "," + g + "," + b + ")"
}

function generateRandomColor() {
    var letters = '0123456789ABCDEF'
    var color = '#'

    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)]
    }
    return color
}

function read_variable_inputs(variable_inputs) {
    result = {}

    $.each(variable_inputs, function (index, value) {
        result[index] = value.val() === '' ? null : value.val()
    })

    return result
}

function update_variable_inputs(variable_inputs, variables) {
    $.each(variables, function (index, value) {
        value = value[value.length - 1]
        variable_inputs[index].val(value === 'None' ? '' : value)
    })
}

function update_dc_phases(dc_phase_codes, active_dc_phases) {
    $.each(dc_phase_codes, function (index, value) {
        value.removeClass('alert-success')

        if ($.inArray(index, active_dc_phases) !== -1) {
            value.addClass('alert-success')
        }
    })
}

exports.init_simulator_tab = init_simulator_tab