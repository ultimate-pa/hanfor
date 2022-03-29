function get_selected_requirement_ids() {
    let requirements_table = $('#requirements_table').DataTable()

    let ids = []
    requirements_table.rows({selected: true}).every(function () {
        ids.push(this.data()['id'])
    })

    return ids
}

function update_simulator_select() {
    let simulator_select = $('#simulator-select')

    $.ajax({
        type: 'GET',
        url: 'simulator',
        data: {command: 'get_simulators'},
        success: function (response) {
            if (response['success'] === false) {
                alert(response['errormsg']);
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

    update_simulator_select()

    $('#create-simulator-btn').click(function () {
        $.ajax({
            type: 'POST',
            url: 'simulator',
            data: {
                command: 'create_simulator',
                simulator_name: simulator_name_input.val() || 'unnamed',
                requirement_ids: JSON.stringify(get_selected_requirement_ids())
            },
            success: function (response) {
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

    $('#delete-simulator-btn').click(function () {
        $.ajax({
            type: 'DELETE',
            url: 'simulator',
            data: {
                command: 'delete_simulator',
                simulator_id: simulator_select.val()
            },
            success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }

                update_simulator_select()
            }
        });
    });

    $('#start-simulator-btn').click(function () {
        let simulator_id = simulator_select.val()

        init_simulator_modal(simulator_id)
    })
}

function init_simulator_modal(simulator_id) {
    let simulator_title = $('#simulator_modal_title')
    let simulator_modal = $('#simulator_modal')

    simulator_title.html('Simulator: ' + simulator_id)

    let accordion = $('#simulator-accordion')
    let accordion_card = $('.simulator-accordion-card')

    accordion_card.clone().html(accordion_card.html().replaceAll('{requirement_id}', 'REQ1')).appendTo(accordion)
    accordion_card.clone().html(accordion_card.html().replaceAll('{requirement_id}', 'REQ2')).appendTo(accordion)

    simulator_modal.modal('show')
}

exports.init_simulator_tab = init_simulator_tab