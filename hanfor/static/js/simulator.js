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
    let time = data['time']
    let variables = data['var_mapping'][time]
    let active_dc_phases = data['active_dc_phases']

    let simulator_modal = $(data['html'])
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

    simulator_step_check_btn.click(function () {
        $.ajax({
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

                time = response['data']['time']
                variables = response['data']['var_mapping'][time]
                update_variable_inputs(variable_inputs, variables)

                active_dc_phases = response['data']['active_dc_phases']
                update_dc_phases(dc_phase_codes, active_dc_phases)
            }
        })
    })

    simulator_step_back_btn.click(function () {
        $.ajax({
            type: 'POST', url: 'simulator', async: false, data: {
                command: 'step_back', simulator_id: simulator_id
            }, success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                simulator_step_transition_select.empty()

                time = response['data']['time']
                variables = response['data']['var_mapping'][time]
                update_variable_inputs(variable_inputs, variables)

                active_dc_phases = response['data']['active_dc_phases']
                update_dc_phases(dc_phase_codes, active_dc_phases)
            }
        })
    })

    simulator_modal.find('#simulator-countertraces-accordion').sortable();
    simulator_modal.find('#simulator-variables-form-row').sortable();

    simulator_modal.modal('show')
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