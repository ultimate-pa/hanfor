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
    let siumlator_start_btn = $('#simulator-start-btn')
    let requirements_table = $('#requirements_table')

    update_simulator_select(simulator_select)

    simulator_create_btn.click(function () {
        $.ajax({
            type: 'POST', url: 'simulator', data: {
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
            type: 'DELETE', url: 'simulator', data: {
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

    siumlator_start_btn.click(function () {
        let simulator_id = simulator_select.val()

        $.ajax({
            type: 'GET',
            url: 'simulator',
            data: {command: 'start_simulator', simulator_id: simulator_id},
            success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                init_simulator_modal(simulator_id, response['data'])
            }
        })
    })
}

function init_simulator_modal(simulator_id, data) {
    let simulator_modal = $(data['html'])
    let simulator_next_step_btn = simulator_modal.find('#simulator-next-step-btn')
    let simulator_previous_step_btn = simulator_modal.find('#simulator-previous-step-btn')

    simulator_modal.find('#simulator-countertraces-accordion').sortable();
    simulator_modal.find('#simulator-variables-form-row').sortable();

    let var_mapping = data['var_mapping']
    let time = Object.keys(var_mapping)[Object.keys(var_mapping).length - 1]
    let variables = var_mapping[time]

    let variable_inputs = {}
    $.each(variables, function (variable, value) {
        variable_inputs[variable] = simulator_modal.find('#' + variable + '_input')
        variable_inputs[variable].val(value !== 'None' ? value : '')
    });

    simulator_next_step_btn.click(function () {
        $.ajax({
            type: 'POST',
            url: 'simulator',
            data: {command: 'next_step', simulator_id: simulator_id},
            success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                // TODO: next step
                alert('next step')
            }
        })
    })

    simulator_previous_step_btn.click(function () {
        $.ajax({
            type: 'POST',
            url: 'simulator',
            data: {command: 'previous_step', simulator_id: simulator_id},
            success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                // TODO: previous step
                alert('previous step')
            }
        })
    })

    simulator_modal.modal('show')
}

exports.init_simulator_tab = init_simulator_tab