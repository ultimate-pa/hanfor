import Mustache from "mustache"
import { read_formalization_card } from "./formalization-card.js"

const { Toast } = require("bootstrap")
require("../bootstrap-confirm-button")

export function bind_card_events(selector, { store, onChange, onDelete }) {
  $(document).on("input change", `${selector} > .accordion-item :input`, function () {
    const $item = $(this).closest(".accordion-item")
    $item.addClass("draft")
    store.edit($item.data("type"), $item.data("id"))
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
  $(selector).on("click", ".copy_formalization", function () {
    copy_formalization($(this).closest(".accordion-item"))
    $(this).addClass("animate-success")
    setTimeout(() => {
      $(this).removeClass("animate-success")
    }, 600)
  })
}

export function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(";").shift()
}

export function setCopyBtnEnable() {
  const button = document.getElementById("add_copied_formalization")
  button.disabled = !getCookie("copied_formalization")
}

export function read_copied_formalization() {
  const cookie = getCookie("copied_formalization")
  return cookie ? JSON.parse(cookie) : {}
}

function copy_formalization($item) {
  const card = read_formalization_card($item)
  const formalization = {
    scope: card.scope,
    pattern: card.pattern,
    is_constraint: card.is_constraint,
  }
  for (const [key, value] of Object.entries(card.expression_mapping)) {
    formalization[`expr_${key}`] = value
  }

  const d = new Date()
  d.setTime(d.getTime() + 8 * 3600 * 1000)
  const expires = "expires=" + d.toUTCString()
  document.cookie = "copied_formalization=" + JSON.stringify(formalization) + ";" + expires + ";path=/"
  localStorage.setItem("cookieUpdate", Date.now())
  setCopyBtnEnable()
}

export function handle_save_error(renderer, $accordion, err) {
  const errors = err?.responseJSON?.errors ?? {}
  $accordion.children(".accordion-item.draft").each(function () {
    if (!(String($(this).data("id")) in errors)) {
      $(this).removeClass("draft border-danger")
    }
  })
  if (Object.keys(errors).length) {
    show_save_errors(renderer, $accordion, errors)
    return
  }
  alert(`Save failed (${err?.status}): ${err?.responseJSON?.errormsg || err?.statusText || "Unknown error"}`)
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
