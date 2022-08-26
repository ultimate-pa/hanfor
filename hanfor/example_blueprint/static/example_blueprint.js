MY_BUTTON = $('#my-button')

$(document).ready(function () {
    MY_BUTTON.click(function () {

        $.ajax({
            type: 'GET',
            //url: 'get_awesome_message',
            url: 'api',
            data: {}
        }).done(function (data, textStatus, jqXHR) {
            console.log('data:', data, 'textStatus:', textStatus, 'jqXHR:', jqXHR)
            //alert(data['message'])
            alert(data)
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.log('jqXHR:', jqXHR, 'textStatus:', textStatus, 'errorThrown:', errorThrown)
            alert(errorThrown)
        })
    })
})