const autosize = require("autosize/dist/autosize")
const utils = require("../hanfor-utils")

const EXPRESSION_KEYS = ["P", "Q", "R", "S", "T", "U", "V"]
const PATTERN_KEYS = ["R", "S", "T", "U", "V"]

export const FORMALIZATION_TYPE = {
  // define the defaults for generating an empty entry
  defaults: {
    order: 0,
    text: "// None, no pattern set",
    formalization_type: "formalization",
    scope: "NONE",
    pattern: "NotFormalizable",
  },
  // a selector that fetches the correct template for the type
  template: "formalization",
  container: "container",
  contentSelector: ".accordion-collapse",
  requires: ["save_error_toast"],
  withPatterns: true,
  // each function can define after render behavior function that gets applied
  // after mustache renders it, i.e setting the required variable placeholders as visible
  afterRender: ($container, entry) => {
    if (entry.scope) $container.find(`#requirement_scope${entry.id}`).val(entry.scope)
    if (entry.pattern) $container.find(`#requirement_pattern${entry.id}`).val(entry.pattern)
    $container.find(`#is_constraint${entry.id}`).prop("checked", !!entry.is_constraint)
    EXPRESSION_KEYS.forEach((v) => {
      const val = entry[`expr_${v}`]
      if (!val) {
        $container.find(`#requirement_var_group_${v.toLowerCase()}${entry.id}`).hide()
      }
    })
    // this is the title observer for changing the text of the drafts so the users
    // have easier time knowing which drafts did they create
    const preview = $container.find(`#current_formalization_textarea${entry.id}`)
    const accordionItem = $container.closest(".accordion-item")
    const updateTitle = () => {
      const text = preview.text().trim() || "// None, no pattern set"
      accordionItem.attr("title", text)
      accordionItem.find(".accordion-button").text(text)
    }
    updateTitle()
    // if preview gets updated dynamically, watch it
    const observer = new MutationObserver(updateTitle)
    observer.observe(preview[0], {
      childList: true,
      subtree: true,
      characterData: true,
    })
  },
}

/**
 * Updates the formalization preview of each card based on the selected scope, pattern and expressions.
 */
export function update_previews($accordion, available_vars) {
  $accordion.find(".formalization_card").each(function () {
    const id = $(this).attr("title")
    const selected = (name) => $(`#requirement_${name}${id}`).find("option:selected").text().replace(/\s\s+/g, " ")
    const scope = selected("scope")
    const pattern = selected("pattern")

    let formalization = scope !== "None" && pattern !== "None" ? `${scope}, ${pattern}.` : ""
    EXPRESSION_KEYS.forEach((key) => {
      const value = $(`#formalization_var_${key.toLowerCase()}${id}`).val().trim()
      if (value.length > 0) {
        formalization = formalization.replace(new RegExp(`{${key}}`, "g"), parse_vars_to_link(value, available_vars))
      }
    })

    const preview = $(`#current_formalization_textarea${id}`)
    preview.html(formalization)
    autosize.update(preview)
  })
  $accordion.closest(".modal").data("unsaved_changes", true)
}

/**
 * Replace variables in a formalization string by links to that variable.
 * Example: foo || bar -> <a href ...>foo</a> || <a href ...>bar</a>
 */
function parse_vars_to_link(formal_string, available_vars) {
  let result = ""

  // Split the formalization string on possible variable delimiters given by the boogie grammar.
  // We enclose the regular expression by /()/g to yield the delimiters itself: We want to keep them in the result.
  formal_string.split(/([\s&<>!()=:\[\]{}\-|+*,])/g).forEach(function (chunk) {
    if (available_vars.includes(chunk)) {
      let query = "?command=search&col=1&q=%5C%22" + chunk + "%5C%22"
      result +=
        '<a href="./variables' +
        query +
        '" target="_blank"' +
        '  title="Go to declaration of ' +
        chunk +
        '" class="alert-link">' +
        chunk +
        "</a>"
    } else {
      // We need to escape potential HTML special chars to prevent a broken display.
      result += utils.escapeHtml(chunk)
    }
  })
  return result
}

/**
 * Show the expression fields (P, Q, R, ...) each card needs for its scope and pattern.
 */
export function update_var_groups($accordion, type_inference_errors) {
  $accordion.find(".requirement_var_group").hide().removeClass("type-error")

  $accordion.find(".formalization_card").each(function () {
    const id = $(this).attr("title")
    const group = (key) => $(`#requirement_var_group_${key.toLowerCase()}${id}`)
    const header = $(`#formalization_heading-formalization-${id}`)

    // Set the red boxes for type inference failed expressions.
    if (id in type_inference_errors) {
      type_inference_errors[id].forEach((key) => {
        $(`#formalization_var_${key}${id}`).addClass("type-error")
        header.addClass("type-error-head")
      })
    } else {
      header.removeClass("type-error-head")
    }

    const scope = $(`#requirement_scope${id}`).val()
    if (["BEFORE", "AFTER", "BETWEEN", "AFTER_UNTIL"].includes(scope)) group("P").show()
    if (["BETWEEN", "AFTER_UNTIL"].includes(scope)) group("Q").show()

    Object.keys(_PATTERNS[$(`#requirement_pattern${id}`).val()]["env"])
      .filter((key) => PATTERN_KEYS.includes(key))
      .forEach((key) => group(key).show())
  })
}

export function read_formalization_card($item) {
  const formalization = {
    scope: $item.find(".scope_selector").val(),
    pattern: $item.find(".pattern_selector").val(),
    is_constraint: $item.find(".is-constraint-checkbox").is(":checked"),
    expression_mapping: {},
  }
  $item.find("textarea.reqirement-variable").each(function () {
    const title = $(this).attr("title")
    if (title) formalization.expression_mapping[title] = $(this).val()
  })
  return formalization
}
