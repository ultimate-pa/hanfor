jQuery.fn.bootstrapConfirmButton = function(options) {
    $(this).on('click', options.selector, function () {
        if ($(this).data('html') === undefined) {
            $(this).outerWidth($(this).outerWidth()).data('html', $(this).html()).html('Do it!')

            setTimeout(function () {
                $(this).html($(this).data('html')).removeData('html')
            }, 2000)
        } else {
            $(this).html($(this).data('html')).removeData('html')
            options.onConfirm.call($(this))
        }
    })
}