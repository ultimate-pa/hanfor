import Mustache from "mustache"

const { Toast } = require("bootstrap")
require("../bootstrap-confirm-button")

export function bind_card_events(selector, { onChange, onDelete }) {
  $(document).on("input change", `${selector} > .accordion-item :input`, function () {
    $(this).closest(".accordion-item").addClass("draft")
  })
  $(selector).on(
    "change",
    ".formalization_selector, .reqirement-variable, .req_var_type, .is-constraint-checkbox",
    onChange,
  )
  $(selector).bootstrapConfirmButton({
    selector: ".delete_formalization",
    onConfirm: function () {
      onDelete($(this).attr("name"), $(this).closest(".accordion-item"))
    },
  })
}

export async function patch_edited_cards($accordion, cards, patch) {
  const results = await Promise.allSettled(cards.map(([id, entry]) => patch(id, entry)))
  const errors = {}
  results.forEach((result, i) => {
    const [id] = cards[i]
    if (result.status === "fulfilled") {
      $accordion.children(`.accordion-item[data-id="${id}"]`).removeClass("draft")
    } else {
      errors[id] = result.reason?.responseJSON?.errormsg || result.reason?.statusText
    }
  })
  if (Object.keys(errors).length) {
    throw { responseJSON: { errors } }
  }
}

export function show_save_errors(renderer, $accordion, errors) {
  const items = Object.entries(errors).map(([temp_id, message]) => {
    const card = $accordion.children(`.accordion-item[data-id="${temp_id}"]`)
    card.addClass("border-danger")
    return { name: card.find(".accordion-button").first().text().trim() || temp_id, message }
  })
  const toast = $(Mustache.render(renderer.getTemplate("save_error_toast"), { errors: items }).trim())
  $("#save_error_toasts").append(toast)
  toast[0].addEventListener("hidden.bs.toast", () => toast.remove())
  Toast.getOrCreateInstance(toast[0], { autohide: false }).show()
}
