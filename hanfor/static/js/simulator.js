require('jquery-ui-sortable')

// TODO: Remove in Bootstrap version >= 5.1
require('../css/floating-labels.css')

function get_selected_requirement_ids(requirements_table) {
    let ids = []
    requirements_table.DataTable().rows({selected: true}).every(function () {
        ids.push(this.data()['id'])
    })

    return ids
}

function update_simulator_select(simulator_select) {
    $.ajax({
        type: 'GET', url: 'simulator', data: {command: 'get_simulators'}, success: function (response) {
            if (response['success'] === false) {
                alert(response['errormsg'])
                return
            }

            simulator_select.empty()
            $.each(response['data']['simulators'], function (index, value) {
                simulator_select.append($('<option></option>').val(value[0]).text(value[1] + ' (' + value[0] + ')'))
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
                simulator_select.prepend($('<option></option>').val(id).text(name + ' (' + id + ')')).val(id)
            }
        })
    })

    simulator_delete_btn.click(function () {
        $.ajax({
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
            type: 'GET', url: 'simulator', async: false, data: {
                command: 'start_simulator',
                simulator_id: simulator_select.val()
            },
            success: function (response) {
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
    let simulator_modal = $(data['html'])
    let simulator_next_step_btn = simulator_modal.find('#simulator-next-step-btn')
    let simulator_previous_step_btn = simulator_modal.find('#simulator-previous-step-btn')

    simulator_modal.find('#simulator-countertraces-accordion').sortable();
    simulator_modal.find('#simulator-variables-form-row').sortable();

    let simulator_id = data['simulator_id']
    let time = data['time']
    let variables = data['var_mapping'][time]
    let active_dc_phases = data['active_dc_phases']

    let variable_inputs = {}
    update_variable_inputs(simulator_modal, variable_inputs, variables)

    let dc_phase_codes = {}
    update_dc_phases(simulator_modal, dc_phase_codes, active_dc_phases)

    simulator_next_step_btn.click(function () {
        $.ajax({
            type: 'POST', url: 'simulator', async: false, data: {
                command: 'next_step',
                simulator_id: simulator_id,
                variables: JSON.stringify(read_variable_inputs(variable_inputs))
            },
            success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                time = response['data']['time']
                variables = response['data']['var_mapping'][time]
                update_variable_inputs(simulator_modal, variable_inputs, variables)

                active_dc_phases = response['data']['active_dc_phases']
                update_dc_phases(simulator_modal, dc_phase_codes, active_dc_phases)
            }
        })
    })

    simulator_previous_step_btn.click(function () {
        $.ajax({
            type: 'POST', url: 'simulator', async: false, data: {
                command: 'previous_step',
                simulator_id: simulator_id
            },
            success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                time = response['data']['time']
                variables = response['data']['var_mapping'][time]
                update_variable_inputs(simulator_modal, variable_inputs, variables)

                active_dc_phases = response['data']['active_dc_phases']
                update_dc_phases(simulator_modal, dc_phase_codes, active_dc_phases)
            }
        })
    })

    simulator_modal.modal('show')
}

function read_variable_inputs(variable_inputs) {
    result = {}
    $.each(variable_inputs, function(index, value) {
        result[index] = value.val() === '' ? null : value.val()
    })

    return result
}

function update_variable_inputs(simulator_modal, variable_inputs, variables) {
    $.each(variables, function (index, value) {
        if (!(index in variable_inputs)) {
            variable_inputs[index] = simulator_modal.find('#' + index + '_input')
        }

        variable_inputs[index].val(value === 'None' ? '' : value)
    })
}

function update_dc_phases(simulator_modal, dc_phase_codes, active_dc_phases) {
    $.each(dc_phase_codes, function (index, value) {
        value.removeClass('alert-success')
    })

    $.each(active_dc_phases, function (index, value) {
        if (!(value in dc_phase_codes)) {
            dc_phase_codes[value] = simulator_modal.find('#' + value + '_code')
        }

        dc_phase_codes[value].addClass('alert-success')
    })
}

exports.init_simulator_tab = init_simulator_tab