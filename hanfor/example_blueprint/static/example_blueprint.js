MY_BUTTON = $('#my-button')

$(document).ready(function () {
    MY_BUTTON.click(function () {

        $.ajax({
            type: 'GET',
            url: 'get_awesome_message',
            data: {}
        }).done(function (data, textStatus, jqXHR) {
            console.log('data:', data, 'textStatus:', textStatus, 'jqXHR:', jqXHR)
            alert(data['message'])
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.log('jqXHR:', jqXHR, 'textStatus:', textStatus, 'errorThrown:', errorThrown)
            alert(errorThrown)
        })
    })
})