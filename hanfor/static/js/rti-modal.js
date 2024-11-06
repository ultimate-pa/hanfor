require('../css/simulator-modal.css')
const {Modal} = require('bootstrap')
const {Chart, registerables} = require('chart.js')
const annotationPlugin = require('chartjs-plugin-annotation')

Chart.register(...registerables, annotationPlugin)

function init_rti_modal(data) {
    const rti_modal = $(data['html'])
    console.log('wholoolasdasdo');
    console.log(data)

    Modal.getOrCreateInstance(rti_modal[0]).show();

    rti_modal[0].addEventListener('hidden.bs.modal', function () {
        $('#rti_modal').remove();
    });



}



module.exports.init_rti_modal = init_rti_modal;