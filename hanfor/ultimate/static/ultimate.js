require('gasparesganga-jquery-loading-overlay')
require('bootstrap')
require('datatables.net-bs5')
require('jquery-ui/ui/widgets/autocomplete')
require('jquery-ui/ui/effects/effect-highlight')
require('../../static/js/bootstrap-tokenfield.js')
require('awesomplete')
require('awesomplete/awesomplete.css')
require('datatables.net-colreorder-bs5')
require('../../static/js/bootstrap-confirm-button')

$(document).ajaxStart(function () {
    $.LoadingOverlay('show')
})

$(document).ajaxStop(function () {
    $.LoadingOverlay('hide')
})

$(document).ready(function () {

    $('#btnTest').click(function () {
        console.log("test was pressed!")
        $('#btnTest').text("test was pressed")
        /*$.ajax({
            type: 'POST', url: '../api/tags/add_standard',
        }).done(function (data) {
            location.reload()
        }).fail(function (jqXHR, textStatus, errorThrown) {
            alert(errorThrown + '\n\n' + jqXHR['responseText'])
        })*/
    })
})