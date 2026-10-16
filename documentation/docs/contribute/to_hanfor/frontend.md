# Frontend Cards Guide
The requirement modal and the variable modal show lists of cards (formalizations, variables, constraints).
Both modals use the same workflow.
This guide explains the workflow, so that you can add a new card list or change an existing one.

The workflow has three parts:

| Part | File | Task |
|---|---|---|
| `TemplateRenderer` | `static/js/template/TemplateRenderer.js` | Makes the HTML of a card from a Mustache template. |
| `TrackedStore` | `static/js/store/TrackedStore.js` | Keeps the new, the changed and the deleted cards (drafts) until the user clicks Save. Then it sends them. |
| `ApiClient` | `static/js/api/ApiClient.js` | Sends the REST requests to the server. |

The code that the two modals share is in `static/js/formalizations/`.
The templates are in `static/templates/formalizations/`.

---

## Flow

```text
open modal   GET data          -> renderer.build(type, entry) for each entry
edit         add a card        -> store.create(type)        (draft, not on the server)
             delete a card     -> store.delete(type, id)    (draft, not on the server)
             change a card     -> store.edit(type, id)      (bind_card_events does this)
Save         store.commit(parentId)     at the same time, for all types:
                                          DELETE each deleted card
                                          POST all new cards in one request
                                          PATCH each changed card
             then PATCH the main object (requirement or variable)
close        store.reset()              discard all drafts
```

The server gets no data before the user clicks Save.
If the user closes the modal without Save, the drafts are discarded.

---

## Templates and TemplateRenderer

### Templates

A template is a plain `.mustache` file in `static/templates/<folder>/`.
The browser loads the templates at runtime. Thus, after you change a template, you do not have to build the bundle again.
Reload the page without the browser cache.

A card has two templates:

- The container: `container.mustache`. It is the Bootstrap accordion item with the header button.
- The content: for example `formalization.mustache` or `variable.mustache`. The renderer puts the content into the element of the container that `contentSelector` selects.

Put each logical block of HTML (a card, a toast, a list entry) into a template.
For a small HTML part of one line, for example a `<span>`, a JavaScript string is sufficient. A template for it gives no advantage.

### Register a card type

Make one renderer for each page, and register each card type one time:

```js
import TemplateRenderer from "./template/TemplateRenderer.js"
import { FORMALIZATION_TYPE } from "./formalizations/formalization-card.js"

const renderer = new TemplateRenderer({ baseUrl: "/static/templates/formalizations" })
renderer.registerType("formalization", FORMALIZATION_TYPE)
```

The configuration of a type has these fields:

| Field | Description |
|---|---|
| `defaults` | The values for an empty entry. `build` merges the entry over these values. |
| `template` | The name of the content template (without `.mustache`). |
| `container` | Optional. The name of the container template. |
| `contentSelector` | The selector in the container that gets the content. |
| `requires` | Optional. The names of more templates to load, for example `save_error_toast`. |
| `withPatterns` | If `true`, the entry gets the scopes and pattern groups from `/api/v1/patterns`. |
| `afterRender($el, entry)` | Optional. Runs after the HTML is made. Use it to set select values, to hide fields and to attach events to the card. |

You can use a type again with different defaults.
The variable modal uses the formalization card for constraints. The value `variable_constraint: true` hides the "Mark as constraint" checkbox:

```js
renderer.registerType("formalization", {
    ...FORMALIZATION_TYPE,
    defaults: {...FORMALIZATION_TYPE.defaults, variable_constraint: true},
})
```

### Make a card

| Method | Description |
|---|---|
| `ready()` | Loads all templates of all registered types and the patterns. Returns a promise. Call it before the first `build`. |
| `build(type, entry)` | Returns a jQuery element of the card. The template uses the fields of `entry`, for example `{{ id }}` or `{{ text }}`. |
| `getTemplate(name)` | Returns the text of a loaded template, for example to render a toast with `Mustache.render`. |

```js
await renderer.ready()
const constraints = await api.getVariableConstraints(vid)
$("#formalization_accordion").html("")
    .append(constraints.map(constraint => renderer.build("formalization", constraint)))
```

---

## TrackedStore

The store keeps the ids of the new, the changed and the deleted cards for each type.
It does not keep the content of a card. The content is in the DOM. The store reads it on Save with `readDOM`.
The name of a store type must be the same as the `data-type` of its cards, because `bind_card_events` uses `data-type` to call `store.edit`.

### Register a store type

```js
import TrackedStore from "./store/TrackedStore.js"

const store = new TrackedStore()
store.registerType("formalization", {
    readDOM(id) {
        const $item = $(`#formalization_accordion > .accordion-item[data-id="${id}"]`)
        return $item.length ? {temp_id: String(id), ...read_formalization_card($item)} : null
    },
    persistCreate: (vid, drafts) => api.createVariableConstraints(vid, drafts),
    persistDelete: (vid, cid) => api.deleteVariableConstraint(vid, cid),
    persistPatch: (vid, cid, entry) => api.patchVariableConstraint(vid, cid, entry),
})
```

| Function | Description |
|---|---|
| `readDOM(id)` | Returns the data of the card with this id, with the field `temp_id`. Returns `null` if the card is not in the DOM. The store uses it for creates and for patches (without `temp_id`). |
| `persistCreate(parentId, drafts)` | Sends all new cards in one request. Returns the request. |
| `persistDelete(parentId, id)` | Deletes one card on the server. Returns the request. |
| `persistPatch(parentId, id, entry)` | Sends the changes of one card that is on the server. Returns the request. |

### Methods

| Method | Description |
|---|---|
| `create(type)` | Makes a temporary id (`tmp-1`, `tmp-2`, ...) and records it as new. Use this id for the new card. |
| `edit(type, id)` | Records the card as changed. A new card is not recorded, because the create sends its content. |
| `delete(type, id)` | Records the card as deleted. If the card is new, the store only forgets it. |
| `isCreated(type, id)` | Returns `true` if the card is new and not on the server. |
| `hasNoDrafts(type)` | Returns `true` if the type has no new, no changed and no deleted cards. Without `type`, it checks all types. |
| `commit(parentId)` | Sends all deletes, creates and patches of all types at the same time (see below). Returns a promise. |
| `resolveId(id)` | Returns the server id for a temporary id after a create. Other ids do not change. |
| `resolveKeys(object)` | Changes the temporary ids in the keys of an object to server ids, for example for an order list. |
| `reset()` | Discards all drafts. Call it when the modal closes. |

### Server contract for a batch create

`persistCreate` sends a list of drafts. Each draft has a `temp_id`.

- If all drafts are correct, the server stores them and sends `201` with `{"ids": {"<temp_id>": <id>}}`.
- If one or more drafts are not correct, the server sends `400` with:
    - `ids`: the drafts that the server stored,
    - `errors`: `{"<temp_id>": "<message>"}` for each draft that the server did not store,
    - `errormsg`: one message for all errors.

The store takes the ids of the stored drafts in both cases. The drafts with an error stay drafts.
Examples: `POST /api/v1/req/<rid>/formalizations/<subtype>` and `POST /api/v1/variables/<vid>/constraints`.

### commit

`commit(parentId)` starts all requests at the same time. The creates and the patches do not depend on each other: a new card is never recorded as changed, and the ids from an earlier save are already known.

- If all requests are successful, the promise resolves and the store has no drafts.
- If one or more requests fail, the promise rejects with `{responseJSON: {errors}}`. `errors` has one message for each card that failed, with the card id (the `data-id` in the DOM) as the key. The failed changes stay drafts, so the next Save sends them again.

Give the error to `handle_save_error` (see [Shared card code](#shared-card-code)).

---

## ApiClient

`ApiClient` sends all requests to `/api/v1`. Each endpoint has one short method:

```js
const url = (strings, ...values) => strings.reduce((out, part, i) => out + encodeURIComponent(values[i - 1]) + part)

getVariableConstraints(id) { return this.get(url`/variables/${id}/constraints`) }
createVariableConstraints(id, drafts) { return this.post(url`/variables/${id}/constraints`, { json: drafts }) }
```

- Use the `url` tag for each path that contains a value. It encodes the value, for example a requirement id with a space.
- Send JSON with `{ json: body }`. Some older endpoints use form data with `{ form: body }`.
- Each method returns a jQuery request. You can use it with `.then`, `.done`, `.fail` and `await`.
- `api.onError` is an optional function that runs for each failed request.

When you add an endpoint, make a class-based flask-restx `Resource` with a REST path on the server.
Then add one method for it to `ApiClient`.

---

## Shared card code

`static/js/formalizations/formalization-card.js`:

| Export | Description |
|---|---|
| `FORMALIZATION_TYPE` | The renderer configuration of a formalization card. |
| `read_formalization_card($item)` | Returns `scope`, `pattern`, `is_constraint` and `expression_mapping` of a card. |
| `update_previews($accordion, available_vars)` | Writes the formalization text of each card into its preview and header. |
| `update_var_groups($accordion, type_inference_errors)` | Shows the expression fields (P, Q, R, ...) that the scope and the pattern need, and marks type errors. |

`static/js/formalizations/card-accordion.js`:

| Export | Description |
|---|---|
| `bind_card_events(selector, {store, onChange, onDelete})` | Attaches the events of the accordion: the "draft" class and `store.edit` when the user changes a card, change, delete with confirmation, and copy. Call it one time for each page. |
| `handle_save_error(renderer, $accordion, err)` | Removes the "draft" class from the saved cards. Then it shows the card errors with `show_save_errors`, or an alert for other errors. |
| `show_save_errors(renderer, $accordion, errors)` | Marks the cards with errors and shows a toast. The page needs a `#save_error_toasts` element. |
| `read_copied_formalization()` | Returns the formalization that the user copied with the Copy button, or `{}`. |
| `setCopyBtnEnable()` | Enables the `#add_copied_formalization` button if the user copied a formalization. |

---

## Step by step: add a card list to a modal

The variable modal (`static/js/variables.js`) is a full example. It shows the constraints of a variable as cards.

1. **Template.** Use an existing template, or add a `.mustache` file to `static/templates/formalizations/`.
2. **Renderer type.** Register the type with `renderer.registerType`.
3. **Store type.** Register the type with `store.registerType`, with `readDOM`, `persistCreate`, `persistDelete` and `persistPatch`. Use the `data-type` of the cards as the name of the type.
4. **Load.** In the function that opens the modal, call `await renderer.ready()`, get the data with `ApiClient` and append `renderer.build(...)` for each entry.
5. **Add.** Make the card with the id from the store, and mark it as a draft:
    ```js
    function add_constraint(entry = {}) {
        const $card = renderer.build('formalization', {...entry, id: store.create('formalization')});
        $card.addClass('draft');
        $('#formalization_accordion').append($card);
        refresh_cards();
    }
    ```
6. **Delete.** Call `store.delete(type, id)` and remove the card from the DOM.
7. **Events.** Call `bind_card_events` one time when the page loads, with the store. If other code marks a card as changed, it must also call `store.edit(type, id)`.
8. **Save.** Commit the cards first, then send the main PATCH:
    ```js
    store.commit(vid).then(() =>
        api.patchVariable(vid, {...}),
    ).then(function (data) {
        // close the modal, update the table
    }, function (err) {
        handle_save_error(renderer, $accordion, err);
    });
    ```
    The main PATCH must come after the cards, for two reasons:
    - The requirement PATCH sends the order of the cards with `store.resolveKeys(...)`. This needs the server ids of the new cards.
    - The variable PATCH can rename the variable or change its type. Then the server checks the types of the stored constraints again.

    If a card request fails, the main PATCH is not sent. The user corrects the card and clicks Save again.
9. **Close.** Call `store.reset()` in the `hidden.bs.modal` event of the modal.

---

## Rules

- Put logical blocks of HTML into templates. Use a JavaScript string only for a small HTML part of one line.
- Do not send drafts to the server before the user clicks Save.
- Call `bind_card_events` one time for each page, not each time the modal opens.
- After you change a JavaScript file, build the bundle again: `cd static && npm run build`.
- Use `marked` only for text that the user writes as Markdown (for example a description).
