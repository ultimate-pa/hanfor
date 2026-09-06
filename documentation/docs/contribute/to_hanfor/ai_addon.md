# Writing a New AI Addon

The easiest way to get started is to copy the `example_ai_addon/` folder and rename everything.
This guide walks through what each file does and what you need to change — using the example addon as a reference.

---

## Quickstart

```
1. Copy example_ai_addon/ -> ai_addons/my_addon/
2. Rename all files:        example_ai_addon.py -> my_addon.py  (and so on)
3. Rename all classes/IDs:  ExampleAiAddon -> MyAddon  (see checklist below)
4. Add config flag:         ADDON_MY_ADDON = False 
5. npm run build
6. Enable via web UI
```

### Rename Checklist

| What | Example | Your addon                          |
|---|---|-------------------------------------|
| Folder | `example_ai_addon/` | `my_addon/`                         |
| Python file | `example_ai_addon.py` | `my_addon.py`                       |
| API file | `example_ai_addon_api.py` | `my_addon_api.py`                   |
| JS file | `static/example_ai_addon.js` | `static/my_addon.js`                |
| HTML file | `templates/ai_addons/example_ai_addon.html` | `templates/ai_addons/my_addon.html` |
| Class name | `ExampleAiAddon` | `MyAddon`                           |
| `addon_name` property | `"Example AI addon"` | `"My Addon"`                        |
| `addon_description` property | `"This is an example AI addon"` | `"[YOUR DESC]]"`                    |
| Config flag | `ADDON_EXAMPLE_AI_ADDON` | `ADDON_MY_ADDON`                    |
| Namespace path | `path="/example-ai-addon"` | `path="/my-addon"`                  |
| `TAB_ID` (JS) | `"ai_addons_example_ai_addon"` | `"ai_addons_my_addon"`              |
| `ADDON_NAME` (JS) | `"example-ai-addon"` | `"my-addon"`                        |

---

## File Structure

```
ai_addons/
└── my_addon/
    ├── my_addon.py               # Addon logic
    ├── my_addon_api.py           # REST endpoints
    ├── static/
    │   └── my_addon.js           # Frontend — built to dist/my_addon-bundle.js
    └── templates/
        └── ai_addons/
            └── my_addon.html     # UI fragment (no <html>/<body> tags)
```

Everything here is **auto-discovered** — no registration needed anywhere.
Just create the folder, build, and enable via the web UI.

---

## How the Parts Connect

```
addon_name property  ──>  "My Addon"
                            │
                            ├──> addon_html:  "ai_addons/my_addon.html"
                            └──> addon_js:    "dist/my_addon-bundle.js"

Folder name (my_addon)  ──>  addon ID  ──>  config key: ADDON_MY_ADDON
                                         ──>  get_addon("my_addon", MyAddon)
```

The `addon_name` property controls which template and JS bundle get loaded.
The folder name controls the config key and how the addon is looked up at runtime.
Both must be consistent.

---

## 1. Addon Class (`my_addon.py`)

This is where your addon's logic lives.

**From the example:**

```python
from ai_addons.ai_addon_abstract_class import AiAddonAbstractClass
from ai_addons.threading_ai_socketio import SendUpdateThreadingAndAi


class ExampleAiAddon(AiAddonAbstractClass):
    required_dependencies = ["send_update_threading_and_ai"]
    send_update_threading_and_ai: SendUpdateThreadingAndAi

    @property
    def addon_name(self) -> str:
        return "Example AI addon"

    @property
    def addon_description(self) -> str:
        return "This is an example AI addon"

    def _do_initialize(self):
        self.global_counter = 0
        self._sid_map = {}  # { sid: count }
```

**What to change:**

- Rename the class (`ExampleAiAddon` -> `MyAddon`)
- Update `addon_name` and `addon_description`
- Declare the dependencies you need in `required_dependencies`
- Set up your initial state in `_do_initialize()`

**Rules:**

- No `__init__` — the base class owns it
- `_do_initialize()` is called once when the addon is enabled; your injected dependencies are available there
- Methods that should silently do nothing when the addon is disabled get the decorator:

```python
@AiAddonAbstractClass.requires_enabled
def my_method(self):
    ...
```

**Available dependencies:** `thread_handler`, `ai_request`, `send_update_threading_and_ai`, `db`

### Sending Socket Events

To push data to clients from your addon logic:

```python
# Broadcast to all clients
self.send_update_threading_and_ai.send_ai_update(
    {"counter": self.global_counter, "scope": "global"},
    "socket_my_event",
)

# Send to one specific client only
self.send_update_threading_and_ai.send_ai_update(
    {"counter": current, "scope": "private"},
    "socket_my_event",
    sid=sid,
)
```

The second argument (`"socket_my_event"`) is the event name the frontend listens to.

---

## 2. Configuration

Add the feature flag to **both** config files:

```
configuration/ai_config.py
configuration/ai_config.dist.py
```

```python
ADDON_MY_ADDON = False
```

Naming rule: folder name -> uppercase + `ADDON_` prefix (`my_addon` -> `ADDON_MY_ADDON`).

If the flag is missing, the addon defaults to disabled and logs a warning.

---

## 3. API Routes (`my_addon_api.py`)

This file exposes your addon's methods as HTTP endpoints.

**From the example:**

```python
from flask import Blueprint
from flask_restx import Namespace, Resource
from http import HTTPStatus
from ai_addons.ai_addon_abstract_class import AiAddonAbstractClass
from ai_addons.example_ai_addon.example_ai_addon import ExampleAiAddon
from hanfor_flask import current_app

# Blueprint: only needed if you serve addon-specific static files (e.g. CSS)
blueprint = Blueprint(
    "example_ai_addon", __name__,
    static_folder="static",
    static_url_path="/ai_addons/example_ai_addon/static"
)

# Namespace: defines the URL prefix for all your endpoints
example_ai_addon_api_namespace = Namespace(
    "AI Addon: Example", "Example AI ADDON Description",
    path="/example-ai-addon", ordered=True
)

_handle_disabled = AiAddonAbstractClass.handle_disabled(example_ai_addon_api_namespace)

def _get_addon() -> ExampleAiAddon:
    return current_app.ai_addons.get_addon("example_ai_addon", ExampleAiAddon)
```

**What to change:**

- Replace `example_ai_addon` with your folder name (Blueprint, import, and `get_addon` call)
- Replace `ExampleAiAddon` with your class name
- Update the Namespace name, description, and `path`

**Adding endpoints:**

```python
@example_ai_addon_api_namespace.route("/increment-global-counter")
class ApiExampleAiAddonGlobalCounter(Resource):
    @example_ai_addon_api_namespace.response(HTTPStatus.NO_CONTENT, "Success")
    @example_ai_addon_api_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def post(self):
        _get_addon().increment_global_counter()
        return None, HTTPStatus.NO_CONTENT
```

`@_handle_disabled` is **required on every endpoint** that touches the addon instance.
It automatically returns `403 Forbidden` when the addon is disabled.

Before adding new endpoints, check `core_ui/ai_core_addon_api.py` — it already provides shared endpoints (provider data, request IDs, etc.).

---

## 4. Frontend (`my_addon.js`)

### Tab ID and Addon Name

These two constants are used throughout the frontend:

```javascript
const TAB_ID = "ai_addons_example_ai_addon";   // template path, slashes -> underscores
const ADDON_NAME = "example-ai-addon";          // namespace path (without leading /)
```

Derive them from your own addon:

- `TAB_ID`: template path `ai_addons/my_addon/templates/ai_addons/my_addon.html` -> keep only `ai_addons/my_addon` -> replace `/` with `_` -> `"ai_addons_my_addon"`
- `ADDON_NAME`: the `path` of your Namespace without the leading slash (`path="/my-addon"` -> `"my-addon"`)

### Receiving Socket Events

```javascript
window.tabSubs.register(TAB_ID, [
    {
        event: "socket_example_counter",  // must match the event name sent from Python
        handler: (data) => {
            if (data.scope === "private") {
                document.getElementById("private-counter").textContent = data.counter;
            } else {
                document.getElementById("global-counter").textContent = data.counter;
            }
        },
    },
]);
```

Events registered here are **only active while the tab is visible**.
Never use `window.appSocket.on(...)` directly.

### Tab Lifecycle

```javascript
// Called every time the user opens this tab
window.tabSubs.onActivate(TAB_ID, async () => {
    await window.post(ADDON_NAME, window.appSocket.id);  // register sid
});

// Called when the user leaves the tab
window.tabSubs.onDeactivate(TAB_ID, async () => {
    await window.del(ADDON_NAME, window.appSocket.id);   // unregister sid
});
```

Use `onActivate` to load data and register your sid. Use `onDeactivate` to clean up.
Don't call load functions at the bottom of the file — put them in `onActivate` instead.

### Making API Calls

```javascript
// GET /example-ai-addon/data
const data = await window.get(ADDON_NAME, "data");

// POST /example-ai-addon/increment-global-counter
await window.post(ADDON_NAME, "increment-global-counter");

// POST /example-ai-addon/<sid>  (sid as URL segment)
await window.post(ADDON_NAME, window.appSocket.id);

// DELETE /example-ai-addon/<sid>
await window.del(ADDON_NAME, window.appSocket.id);
```

Built-in error handling:

| Status | Result |
|---|---|
| `2xx` (e.g. `200`) | Returns parsed JSON |
| `204` | Returns `null` |
| `403` | Throws `"Addon is disabled"` |
| Other errors | Throws `"Request failed: <status>"` |

```javascript
try {
    await window.post(ADDON_NAME, "increment-global-counter");
} catch (e) {
    if (e.message === "Addon is disabled") return;
    console.error(e);
}
```

User-facing notifications:

```javascript
window.showBanner("Something went wrong", "danger");
window.showBanner("Saved successfully", "success");
```

---

## 5. HTML Template (`my_addon.html`)

The template is a plain HTML fragment — no `<html>`, `<head>`, or `<body>` tags.
It gets included via `{% include page %}` into the tab system.

**From the example:**

```html
<div class="card mb-3">
  <div class="card-header fw-semibold">Example Addon - Counter</div>
  <div class="card-body d-flex gap-4">

    <div>
      <div class="text-muted small text-uppercase fw-semibold">My Counter</div>
      <div class="fs-4 fw-semibold mb-2" id="private-counter">0</div>
      <button class="btn btn-sm btn-outline-secondary" id="btn-private">Increment mine</button>
    </div>

    <div>
      <div class="text-muted small text-uppercase fw-semibold">Global Counter</div>
      <div class="fs-4 fw-semibold mb-2" id="global-counter">0</div>
      <button class="btn btn-sm btn-outline-secondary" id="btn-global">Increment for everyone</button>
    </div>

  </div>
</div>
```

Use Bootstrap classes for layout and styling to stay consistent with the rest of the UI.
For addon-specific CSS, add a stylesheet:

```html
<link rel="stylesheet" href="/ai_addons/my_addon/static/my_addon.css">
```

---

## 6. Build

```bash
npm run build
```

Webpack picks up all `.js` files in `my_addon/static/` automatically:

```
static/my_addon.js  ->  dist/my_addon-bundle.js
```

---

## Appendix: sid Tracking

The example addon demonstrates how to send socket events to **one specific client** instead of broadcasting to all.

The pattern:

1. When the user opens the tab (`onActivate`), the frontend POSTs its `socket.id` (= sid) to the backend
2. The backend stores it in `_sid_map`
3. When sending an update, the backend passes `sid=` to target only that client
4. When the user leaves the tab (`onDeactivate`), the frontend DELETEs its sid

**Backend:**

```python
def _do_initialize(self):
    self._sid_map = {}

@AiAddonAbstractClass.requires_enabled
def set_sid(self, sid: str):
    self._sid_map[sid] = 0  # initial state for this client

@AiAddonAbstractClass.requires_enabled
def clear_sid(self, sid: str):
    self._sid_map.pop(sid, None)
```

**API:**

```python
@my_addon_namespace.route("/<string:socket_io_sid>")
class ApiSocket(Resource):
    @_handle_disabled
    def post(self, socket_io_sid: str):
        _get_addon().set_sid(socket_io_sid)
        return None, HTTPStatus.NO_CONTENT

    @_handle_disabled
    def delete(self, socket_io_sid: str):
        _get_addon().clear_sid(socket_io_sid)
        return None, HTTPStatus.NO_CONTENT
```

**Frontend:**

```javascript
window.tabSubs.onActivate(TAB_ID, async () => {
    await window.post(ADDON_NAME, window.appSocket.id);
});
window.tabSubs.onDeactivate(TAB_ID, async () => {
    await window.del(ADDON_NAME, window.appSocket.id);
});
```

If you don't need per-client targeting (broadcast-only is fine), you can skip the entire sid tracking pattern.