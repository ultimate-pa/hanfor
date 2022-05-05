require('../css/simulator-modal.css')
require('chart.js/dist/chart.min')
require('chartjs-plugin-annotation')

function init_simulator_modal(data) {
    const simulator_modal = $(data['html'])
    const modal_title_span = simulator_modal.find('#simulator-modal-title span')
    const chart_canvas = simulator_modal.find('#chart-canvas')
    const scenario_save_btn = simulator_modal.find('#simulator-scenario-save-btn')
    const scenario_load_input = simulator_modal.find('#simulator-scenario-load-input')
    const scenario_exit_btn = simulator_modal.find('#simulator-scenario-exit-btn')
    const transitions_table = simulator_modal.find('#simulator-transitions-table')
    const step_transition_select = simulator_modal.find('#simulator-step-transition-select')
    const max_results_input = simulator_modal.find('#simulator-max-results-input')
    const time_step_input = simulator_modal.find('#simulator-time-step-input')
    const step_check_btn = simulator_modal.find('#simulator-step-check-btn')
    const step_next_btn = simulator_modal.find('#simulator-step-next-btn')
    const step_back_btn = simulator_modal.find('#simulator-step-back-btn')

    const variable_colors = generate_random_colors(data.variables)
    const variable_inputs = find_variable_inputs(simulator_modal, data.variables)
    const variable_input_prepends = find_variable_input_prepends(simulator_modal, data.variables)
    const dc_phase_codes = find_dc_phase_codes(simulator_modal)

    update(modal_title_span, transitions_table, step_transition_select, scenario_exit_btn, max_results_input, time_step_input,
        variable_inputs, dc_phase_codes, data)

    init_variable_input_prepends(variable_input_prepends, variable_colors)

    let chart = init_chart(chart_canvas, data, variable_colors)

    scenario_load_input.change(function () {
        const file_reader = new FileReader()
        file_reader.onload = function () {
            $.ajax({
                type: 'POST', url: 'simulator', async: false, data: { // TODO: Allow async.
                    command: 'scenario_load',
                    simulator_id: data.simulator_id,
                    scenario_str: file_reader.result
                }, success: function (response) {
                    if (response['success'] === false) {
                        alert(response['errormsg'])
                        return
                    }

                    update(modal_title_span, transitions_table, step_transition_select, scenario_exit_btn, max_results_input,
                        time_step_input, variable_inputs, dc_phase_codes, response.data)

                    chart.destroy()
                    chart = init_chart(chart_canvas, response.data, variable_colors)
                }
            })
        }

        file_reader.readAsText(scenario_load_input.prop('files')[0]);
    })

    scenario_save_btn.click(function () {
        $.ajax({
            type: 'GET', url: 'simulator', async: false, data: { // TODO: Allow async.
                command: 'scenario_save',
                simulator_id: data.simulator_id
            }, success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                const a = document.createElement('a')
                const file = new Blob([response.data.scenario_str], {type: "text/plain;charset=utf-8"})
                a.href = URL.createObjectURL(file)
                a.download = 'name.json'
                a.click()
            }
        })
    })

    scenario_exit_btn.click(function () {
        $.ajax({
            type: 'POST', url: 'simulator', async: false, data: { // TODO: Allow async.
                command: 'scenario_exit',
                simulator_id: data.simulator_id
            }, success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                update(modal_title_span, transitions_table, step_transition_select, scenario_exit_btn, max_results_input,
                    time_step_input, variable_inputs, dc_phase_codes, response.data)

                chart.destroy()
                chart = init_chart(chart_canvas, response.data, variable_colors)
            }
        })
    })

    step_check_btn.click(function () {
        let isValid = true

        $.each(variable_inputs, function(index, value) {
            value.removeClass('is-invalid')

            if (!value[0].checkValidity()) {
                value.addClass('is-invalid')
                isValid = false
            }
        })

        time_step_input.removeClass('is-invalid')
        if (!time_step_input[0].checkValidity()) {
            time_step_input.addClass('is-invalid')
            isValid = false
        }

        max_results_input.removeClass('is-invalid')
        if (!max_results_input[0].checkValidity()) {
            max_results_input.addClass('is-invalid')
            isValid = false
        }

        if (!isValid) {
            return
        }

        step_transition_select.empty()

        $.ajax({
            type: 'POST', url: 'simulator', async: false, data: { // TODO: Allow async.
                command: 'step_check',
                simulator_id: data.simulator_id,
                time_step: time_step_input.val(),
                max_results: max_results_input.val(),
                variables: JSON.stringify(read_variable_inputs(variable_inputs))
            }, success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                update(modal_title_span, transitions_table, step_transition_select, scenario_exit_btn, max_results_input,
                    time_step_input, variable_inputs, dc_phase_codes, response.data)
            }
        })
    })

    step_next_btn.click(function () {
        $.ajax({
            type: 'POST', url: 'simulator', async: false, data: { // TODO: Allow async.
                command: 'step_next',
                simulator_id: data.simulator_id,
                transition_id: read_transitions_table(transitions_table) //step_transition_select.val()
            }, success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                update(modal_title_span, transitions_table, step_transition_select, scenario_exit_btn, max_results_input,
                    time_step_input, variable_inputs, dc_phase_codes, response.data)

                add_chart_data(chart, response.data)
            }
        })
    })

    step_back_btn.click(function () {
        $.ajax({
            type: 'POST', url: 'simulator', async: false, data: { // TODO: Allow async.
                command: 'step_back',
                simulator_id: data.simulator_id
            }, success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                update(modal_title_span, transitions_table, step_transition_select, scenario_exit_btn, max_results_input,
                    time_step_input, variable_inputs, dc_phase_codes, response.data)

                remove_chart_data(chart, response.data)
            }
        })
    })

    $.each(variable_input_prepends, function (variable, input_prepend) {
        input_prepend.click(function () {
            const y_scale = chart.options.scales['y_' + variable]

            for (const k in chart.data.datasets) {
                const dataset = chart.data.datasets[k]

                if (dataset.yAxisID !== 'y_' + variable)
                    continue

                if (dataset.hidden === true) {
                    dataset.hidden = false
                    y_scale.display = true
                    y_scale.stackWeight = undefined
                    input_prepend.css('background-color', variable_colors[variable])
                } else {
                    dataset.hidden = true
                    y_scale.display = false
                    y_scale.stackWeight = 0.001
                    input_prepend.css('background-color', '#e9ecef')
                }
            }

            chart.update();
        })
    })

    simulator_modal.modal('show')
    simulator_modal.on('hidden.bs.modal', function () {
        $('#simulator_modal').remove()
    })
}

function init_chart(chart_canvas, data, variable_colors) {
    const times = data.scenario == null ? data.times : data.scenario.times
    const models = data.scenario == null ? data.models : data.scenario.variables
    const types = data.types

    let scales = {}
    let datasets = []
    $.each(types, function (index) {
        const type = types[index] === 'Bool' ? 'category' : 'linear'
        const labels = types[index] === 'Bool' ? ['True', 'False'] : []
        models[index][0] = types[index] === 'Bool' ? 'False' : '0'

        scales['y_' + index] = {
            type: type,
            labels: labels,
            offset: true,
            stack: 'demo',
            grid: {
                borderDash: [4, 6]
            }
        }

        datasets.push({
            label: index,
            backgroundColor: variable_colors[index],
            borderColor: variable_colors[index],
            borderWidth: 2,
            data: models[index],
            stepped: 'after',
            yAxisID: 'y_' + index,
            normalized: true
        })
    })

    const config = {
        type: 'line',
        data: {
            labels: times,
            datasets: datasets
        },
        options: {
            layout: {
                padding: {
                    top: 35
                }
            },
            interaction: {
                intersect: false,
            },
            scales: Object.assign({}, scales, {
                x: {
                    type: 'linear',
                    min: 0.0,
                    grid: {
                        borderDash: [4, 6]
                    }
                }
            }),
            plugins: {
                tooltip: {
                    callbacks: {
                        title: function (context) {
                            return 'time: ' + context[0].label
                        }
                    }
                },
                tooltips: {
                    position: 'nearest'
                },
                legend: {
                    display: false
                },
                chartAreaBorder: {
                    borderColor: 'rgba(0, 0, 0, 0.1)',
                },
                annotation: {
                    annotations: {
                        time_line: {
                            type: 'line',
                            value: data.times[data.times.length - 1],
                            borderWidth: 3,
                            scaleID: 'x',
                            display: data.scenario != null,
                            drawTime: 'beforeDatasetsDraw',
                            label: {
                                enabled: true,
                                position: 'start',
                                content: (ctx) => 'time:' + ctx.chart.options.plugins.annotation.annotations.time_line.value,
                                drawTime: 'afterDatasetsDraw',
                                yAdjust: -35
                            },
                        }
                    }
                }
            }
        },
        plugins: [{
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
        }]
    }

    return new Chart(chart_canvas[0].getContext('2d'), config)
}

function add_chart_data(chart, data) {
    chart.options.plugins.annotation.annotations.time_line.value = data.times[data.times.length - 1]

    if (data.scenario == null) {
        chart.data.labels.push(data.times[data.times.length - 1])

        chart.data.datasets.forEach((dataset) => {
            const label = dataset.label
            dataset.data.push(data.models[label][data.models[label].length - 1])
        })
    }

    chart.update()
}

function remove_chart_data(chart, data) {
    chart.options.plugins.annotation.annotations.time_line.value = data.times[data.times.length - 1]

    if (data.scenario == null) {
        chart.data.labels.pop()

        chart.data.datasets.forEach((dataset) => {
            dataset.data.pop()
        })
    }

    chart.update()
}

function find_variable_inputs(simulator_modal, variables) {
    const result = {}

    for (const k in variables) {
        result[k] = simulator_modal.find('#' + k + '_variable_input')
    }

    return result
}

function find_variable_input_prepends(simulator_modal, variables) {
    const result = {}

    for (const k in variables) {
        result[k] = simulator_modal.find('#' + k + '_variable_input_prepend')
    }

    return result
}

function init_variable_input_prepends(variable_input_prepends, variable_colors) {
    for (const k in variable_input_prepends) {
        variable_input_prepends[k].css('background-color', variable_colors[k])
    }
}

function find_dc_phase_codes(simulator_modal) {
    const result = {}

    $.each(simulator_modal.find('code[id$=_dc_phase]'), function (k, v) {
        result[$(v).attr('id').replace('_dc_phase', '')] = $(v)
    })

    return result
}

function read_transitions_table(transitions_table) {
    return transitions_table.find("input:radio:checked").val()
}

function read_variable_inputs(inputs) {
    const result = {}

    $.each(inputs, function (index, value) {
        result[index] = value.val() === '' ? null : value.val()
    })

    return result
}

function update(modal_title_span, transitions_table, step_transition_select, scenario_exit_btn, max_results_input,
                time_step_input, variable_inputs, dc_phase_codes, data) {

    update_modal_title_span(modal_title_span, data)
    update_transitions_table(transitions_table, data)
    update_step_transition_select(step_transition_select, data)
    update_scenario_exit_btn(scenario_exit_btn, data)
    update_max_results_input(max_results_input, data)
    update_time_step_input(time_step_input, data)
    update_variable_inputs(variable_inputs, data)
    update_dc_phases(dc_phase_codes, data)
}

function update_modal_title_span(modal_title_span, data) {
    modal_title_span.text(
        '[' + (data.scenario != null ? 'Scenario mode' : 'Manual mode')
        + ', Cartesian product: ' + parseInt(data['cartesian_size']).toLocaleString('de-DE') + ']'
    )
}

function update_step_transition_select(step_transition_select, data) {
    step_transition_select.empty()

    $.each(data.transitions, function (index, value) {
        step_transition_select.append($('<option></option>').val(index).text(value).addClass('text-break'))
    })
}

function update_transitions_table(transitions_table, data) {
    transitions_table.children('tbody').empty()

    $.each(data.transitions, function (index, value) {
        transitions_table.append(
            `<tr>
    	        <td><input type="radio" name="transition" value="${index}"></td>
    	        <td class="w-100">${value}</td>
            </tr>`
        )
    })

    tr_first = transitions_table.find('tbody tr:first')
    tr_first.children('td').css('border', 'none')
    tr_first.find('input:radio[name=transition]').prop('checked', true)
    tr_first.addClass('table-active')

    transitions_table.on('click', 'tr', function () {
        transitions_table.find('tr').removeClass('table-active')

        $(this).find('input:radio[name=transition]').prop('checked', true)
        $(this).addClass('table-active')
    })
}

function update_scenario_exit_btn(scenario_exit_btn, data) {
    scenario_exit_btn.prop('disabled', data.scenario == null)
}

function update_max_results_input(max_results_input, data) {
    max_results_input.val(data.max_results)
    max_results_input.prop('disabled', data.scenario != null)
}

function update_time_step_input(time_step_input, data) {
    time_step_input.val(data.time_step)
    time_step_input.prop('disabled', data.scenario != null)
}

function update_variable_inputs(variable_inputs, data) {
    $.each(data.variables, function (index, value) {
        value = value[value.length - 1]
        variable_inputs[index].val(value === 'None' ? '' : value)
        variable_inputs[index].prop('disabled', data.scenario != null)
    })
}

function update_dc_phases(dc_phase_codes, data) {
    $.each(dc_phase_codes, function (index, value) {
        value.removeClass('alert-success')
        if ($.inArray(index, data['active_dc_phases']['complete']) !== -1) {
            value.addClass('alert-success')
        }

        value.removeClass('alert-warning')
        if ($.inArray(index, data['active_dc_phases']['waiting']) !== -1) {
            value.addClass('alert-warning')
        }

        value.removeClass('alert-danger')
        if ($.inArray(index, data['active_dc_phases']['exceeded']) !== -1) {
            value.addClass('alert-danger')
        }
    })
}

function generate_random_colors(variables) {
    const result = {}

    for (const k in variables) {
        result[k] = generate_dynamic_color()
    }

    return result
}

function generate_dynamic_color() {
    const r = Math.floor(Math.random() * 255)
    const g = Math.floor(Math.random() * 255)
    const b = Math.floor(Math.random() * 255)

    return "rgb(" + r + "," + g + "," + b + ")"
}

/*
function generate_random_color() {
    const letters = '0123456789ABCDEF'
    let result = '#'

    for (let i = 0; i < 6; i++) {
        result += letters[Math.floor(Math.random() * 16)]
    }

    return result
}

function onChartLegendClick(evt, item, legend) {
    const chart = legend.chart
    const y_scale = chart.options.scales['y_' + item.text]

    $.each(chart.data.datasets, function (index, value) {
        if (value.yAxisID === 'y_' + item.text) {

            if (value.hidden === true) {
                value.hidden = false
                y_scale.display = true
                y_scale.stackWeight = undefined
            } else {
                value.hidden = true
                y_scale.display = false
                y_scale.stackWeight = 0.0000000000001
            }
        }
    })

    chart.update();
}
 */

exports.init_simulator_modal = init_simulator_modal