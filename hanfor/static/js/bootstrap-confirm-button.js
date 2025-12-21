jQuery.fn.bootstrapConfirmButton = function (options) {
  $(this).on("click", options.selector, function () {
    const btn = this
    if ($(btn).data("html") === undefined) {
      $(btn).data("html", $(btn).html()).html("Do it!")

      setTimeout(function () {
        $(btn).html($(btn).data("html")).removeData("html")
      }, 2000)
    } else {
      $(btn).html($(btn).data("html")).removeData("html")
      options.onConfirm.call($(btn))
    }
  })
}
