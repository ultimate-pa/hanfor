//const {Button} = require('bootstrap')
require('bootstrap')
const bootstrap = require('bootstrap')

const AWESOME_MESSAGE_BUTTON = $('#awesome-message-button')
const bsButton = bootstrap.Button.getOrCreateInstance('#awesome-message-button')

$(document).ready(function () {
    AWESOME_MESSAGE_BUTTON.click(function () {
        /**
         * Performs an asynchronous HTTP request: https://api.jquery.com/jquery.ajax
         * HTTP response status codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
         */
        $.ajax({
            type: 'POST',
            url: '/api/example_blueprint' + '',
            data: {
                id: '0123',
                data: 'some data'
            }
        }).done(function (data, textStatus, jqXHR) {
            console.log('data:', data, 'textStatus:', textStatus, 'jqXHR:', jqXHR)
            alert(data)
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.log('jqXHR:', jqXHR, 'textStatus:', textStatus, 'errorThrown:', errorThrown)
            alert(errorThrown + '\n\n' + jqXHR['responseText'])
        })
    })
})