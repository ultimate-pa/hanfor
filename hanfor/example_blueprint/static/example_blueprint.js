const AWESOME_MESSAGE_BUTTON = $('#awesome-message-button')

$(document).ready(function () {
    AWESOME_MESSAGE_BUTTON.click(function () {
        /**
         * Performs an asynchronous HTTP request: https://api.jquery.com/jquery.ajax
         * HTTP response status codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
         */
        $.ajax({
            type: 'GET',
            url: '/api/example_blueprint' + '/0123x',
            data: {
                id: '0123x',
                data: 'some data'
            }
        }).done(function (data, textStatus, jqXHR) {
            console.log('data:', data, 'textStatus:', textStatus, 'jqXHR:', jqXHR)
            alert(data)
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.log('jqXHR:', jqXHR, 'textStatus:', textStatus, 'errorThrown:', errorThrown)
            alert(
                errorThrown + '\n\n' +
                jqXHR['responseJSON']['errormsg']
            )
            console.log(jqXHR['responseJSON']['errormsg'])
        })
    })
})