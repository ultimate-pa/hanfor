const {init_rti_modal} = require('./rti-modal.js')

function init_rti_tab() {
    const depth_input = $('#rti-tab-rti-check-input')
    const rti_check_btn = $('#rti-tab-rti-check-btn')
    const requirements_table = $('#requirements_table')
    const rti_start_btn = $('#rti-tab-start-btn')



        rti_check_btn.click(function () {
        console.log('RTI check button clicked...');
        $.ajax({
            // TODO: Allow async.
            type: 'POST', url: 'simulator', async: false, data: {
                command: 'do_rti_check',
                rti_depth: depth_input.val() || '2',

                requirement_ids: JSON.stringify(get_selected_requirement_ids(requirements_table))
            }, success: function (response) {

                if (response['success'] === false) {
                    alert(response['errormsg'])
                }

            }
        })})


        rti_start_btn.click(function () {
        console.log('RTI check button clicked');
        $.ajax({
            // TODO: Allow async.
            type: 'GET', url: 'simulator', async: false, data: {
                command: 'load_rti_check',
            }, success: function (response) {
                if (response['success'] === false) {
                    alert(response['errormsg'])
                    return
                }
                console.log('sucess');
                // Update the DOM with the new HTML content
                $('#rti-modal-container').html(response['html']);
                init_rti_modal(response.data)
                console.log('sucess2');




            }

        })
    })}

    function get_selected_requirement_ids(requirements_table) {
        let result = []

        requirements_table.DataTable().rows({selected: true}).every(function () {
            result.push(this.data()['id'])
        })

    return result

    }


exports.init_rti_tab = init_rti_tab






