MY_BUTTON = $('#my-button')

$(document).ready(function () {
    MY_BUTTON.click(function () {

        $.ajax({
            type: 'POST',
            url: '',
            data: {
                command: 'my_command'
            }
        }).done(function(data, textStatus, jqXHR) {
            console.log(
                data, textStatus, jqXHR
            )
            alert('done')
        }).fail(function(jqXHR, textStatus, errorThrown) {
            alert(errorThrown)
        })
    })
})