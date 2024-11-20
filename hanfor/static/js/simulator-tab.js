const {init_simulator_modal} = require('./simulator-modal.js')

function init_simulator_tab() {
    const name_input = $('#simulator-tab-name-input')
    const simulator_select = $('#simulator-tab-select')
    const create_btn = $('#simulator-tab-create-btn')
    const delete_btn = $('#simulator-tab-delete-btn')
    const start_btn = $('#simulator-tab-start-btn')
    const requirements_table = $('#requirements_table')

    $.ajax({
        type: 'GET', url: 'simulator', async: false, data: { // TODO: Allow async.
            command: 'get_simulators'
        }, success: function (response) {
            if (response.success === false) {
                alert(response.errormsg)
                return
            }

            update_simulator_select(simulator_select, response.data)
        }
    })

    create_btn.click(function () {
        $.ajax({
            type: 'POST', url: 'simulator', async: false, data: { // TODO: Allow async.
                command: 'create_simulator',
                simulator_name: name_input.val() || 'unnamed',
                requirement_ids: JSON.stringify(get_selected_requirement_ids(requirements_table))
            }, success: function (response) {
                if (response.success === false) {
                    alert(response.errormsg)
                    return
                }

                update_simulator_select(simulator_select, response.data, true)
            }
        })
    })


    delete_btn.click(function () {
        $.ajax({
            type: 'DELETE', url: 'simulator', async: false, data: { // TODO: Allow async.
                command: 'delete_simulator', simulator_id: simulator_select.val()
            }, success: function (response) {
                if (response.success === false) {
                    alert(response.errormsg)
                    return
                }

                update_simulator_select(simulator_select, response.data)
            }
        });
    });

    start_btn.click(function () {
        $.ajax({
            // TODO: Allow async.
            type: 'GET', url: 'simulator', async: false, data: {
                command: 'start_simulator', simulator_id: simulator_select.val()
            }, success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                init_simulator_modal(response.data)
            }
        })
    })
}

function update_simulator_select(simulator_select, data, is_created = false) {
    id = data.simulator_id
    name = data.simulator_name

    if (is_created) {
        simulator_select.prepend($('<option></option>').val(id).text(name + ' (' + id + ')'))
        simulator_select.prop('selectedIndex', 0)
        return
    }

    simulator_select.empty()
    $.each(data['simulators'], function (id, name) {
        simulator_select.prepend($('<option></option>').val(id).text(name + ' (' + id + ')'))
    })
}

// TODO: Use the function in requirements.js
function get_selected_requirement_ids(requirements_table) {
    let result = []

    requirements_table.DataTable().rows({selected: true}).every(function () {
        result.push(this.data()['id'])
    })

    return result
}

exports.init_simulator_tab = init_simulator_tab