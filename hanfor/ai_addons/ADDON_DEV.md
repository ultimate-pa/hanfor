# Writing a New AI Addon

> **Starting point:** Copy `example_ai_addon/` and use it as your base. The sections
> below explain what each file does and what you need to change.

> **Important:** You don't have to provide a frontend, but it is highly recommended to interact with the addon.
---

## Overview: What happens automatically?

Everything in your addon folder is **auto-discovered** - nothing needs to be registered
anywhere. All you need to do:

1. Create a folder under `ai_addons/`
2. Run `npm run build`
3. Enable the addon via the web UI

| What | How it's discovered |
|---|---|
| Addon class | Any class implementing `AiAddonAbstractClass` |
| API routes | Any file ending in `_api.py` |
| JS bundle | Any `.js` file in `my_addon/static/` |
| Templates | Any `templates/` folder |
| Static files | Served under `/ai_addons/my_addon/static/` |

---

## File Structure

```
ai_addons/
└── my_addon/
    ├── my_addon.py            # Addon class
    ├── my_addon_api.py        # API routes
    ├── static/
    │   └── my_addon.js        # built to dist/my_addon-bundle.js
    └── templates/
        └── ai_addons/
            └── my_addon.html
```

The filename of `my_addon.py` (without `.py`) becomes the **addon ID** and determines
the config key (`my_addon -> ADDON_MY_ADDON`).

`addon_html` and `addon_js` are derived from the `addon_name` **property** inside your
class (lowercased and `_` instead of spaces).

---

## 1. Addon Class (`my_addon.py`)

Implement `AiAddonAbstractClass`. The base class handles:
- `enabled` property and `toggle_addon()`
- Dependency injection (no `__init__` needed - or allowed; the base class owns it)
- Deriving `addon_html` and `addon_js` from `addon_name`

```python
from ai_addons.ai_addon_abstract_class import AiAddonAbstractClass

class MyAddon(AiAddonAbstractClass):

    # Which dependencies you need - injected automatically
    required_dependencies = ["thread_handler", "ai_request", "send_update_threading_and_ai"]

    # Type hints for IDE support only, no runtime effect
    thread_handler: ThreadHandler
    ai_request: AiRequest
    send_update_threading_and_ai: SendUpdateThreadingAndAi

    @property
    def addon_name(self) -> str:
        # Lowercased + spaces replaced with underscores:
        # "My Addon" -> addon_html: "ai_addons/my_addon.html"
        #            -> addon_js:   "dist/my_addon-bundle.js"
        return "My Addon"

    @property
    def addon_description(self) -> str:
        return "Does something useful."

    def _do_initialize(self):
        # Called once when the addon is enabled.
        # self.thread_handler, self.ai_request, self.send_update_threading_and_ai are available here.
        pass
```

**Available dependencies:** `thread_handler`, `ai_request`, `send_update_threading_and_ai`, `db`

For methods that should do nothing when the addon is disabled:

```python
@AiAddonAbstractClass.requires_enabled
def do_something(self):
    pass
```

### What the base class provides

| Member | Description |
|---|---|
| `self.enabled` | Returns `self._enabled` |
| `toggle_addon()` | Flips `_enabled`, calls `initialize()` |
| `initialize()` | Calls `_do_initialize()` once while enabled |
| `_do_initialize()` | **Abstract** - your initialization logic |
| `requires_enabled` | Decorator - method does nothing when disabled |
| `addon_html` | `f"ai_addons/{name}.html"` where `name = addon_name.lower().replace(" ", "_")` |
| `addon_js` | `f"dist/{name}-bundle.js"` - same transformation |
| `get_template_folder()` | Path to the `templates/` folder |
| `get_static_folder()` | Path to the `static/` folder |

---

## 2. Configuration (`ai_config.py`)

Add the feature flag to **both** files:

```
configuration/ai_config.py
configuration/ai_config.dist.py   ← template for new instances
```

```python
ADDON_MY_ADDON = False
```

Naming convention: `my_addon -> ADDON_MY_ADDON`

If the flag is missing, the addon defaults to disabled and a warning is logged.

---

## 3. API Routes (`my_addon_api.py`)

Use a **Namespace** for REST endpoints. A **Blueprint** is only needed if you want to
serve your own static files or additional HTML pages.

Before adding new endpoints, check `core_ui/ai_core_addon_api.py` - it already contains
**shared endpoints** (e.g. provider data, request IDs).

```python
from ai_addons.ai_addon_abstract_class import AiAddonAbstractClass
from http import HTTPStatus
from flask_restx import Namespace, Resource, fields
from current_app import ai_addons

my_addon_namespace = Namespace("MyAddon", "Description MyAddon", path="/my_addon", ordered=True)

_handle_disabled = AiAddonAbstractClass.handle_disabled(my_addon_namespace)

def _get_addon() -> MyAddon:
    return ai_addons.get_addon("my_addon", MyAddon)


@my_addon_namespace.route("/data")
class MyAddonData(Resource):

    @my_addon_namespace.response(HTTPStatus.OK, "Success")
    @my_addon_namespace.response(HTTPStatus.FORBIDDEN, "Addon is disabled")
    @_handle_disabled
    def get(self):
        return _get_addon().some_method()
```

`@_handle_disabled` must be on **every endpoint** that accesses the addon instance -
it automatically returns `HTTPStatus.FORBIDDEN` when the addon is disabled.

---

## 4. Frontend (`my_addon.js`)

### Tab ID

The tab ID is derived from the template path - slashes become underscores:

```
ai_addons/my_addon/templates/ai_addons/my_addon.html  ->  "ai_addons_my_addon"
```

### Socket Events and Lifecycle

```javascript
// Events - only active while the tab is visible
window.tabSubs.register('ai_addons_my_addon', [
  {
    event: 'socket_my_event',
    handler: (data) => {
      // update UI
    }
  }
]);

// Called every time the user switches to your tab
window.tabSubs.onActivate('ai_addons_my_addon', () => {
  loadMyData();
});

window.tabSubs.onDeactivate('ai_addons_my_addon', () => {
  unloadSomething();
});

// Bottom of file: one-time loads only (static data that never changes)
loadStaticData();
```

**Never do this:**
```javascript
window.appSocket.on(...)
```
**Always use:**
```javascript
window.tabSubs.register(...)
```

Also: don't call `load()` at the bottom of the file - use `onActivate()` instead.

### API Calls

```javascript
const data = await window.get("my-addon", "data");
await window.post("my-addon", "set_sid", { key: myKey, sid: window.appSocket.id });
await window.del("my-addon", "item", { id: myId });
```

The first argument is the `path` of your namespace (e.g. `path="/my-addon"` -> `"my-addon"`).

Error handling is built in:
- `403` -> throws `"Addon is disabled"`
- `204` -> returns `null`
- Other errors -> throws `"Request failed: <status>"`

```javascript
try {
  const data = await window.get("my-addon", "data");
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

The template is included via `{% include page %}` into the tab system. It contains **no** `<html>`, `<head>`, or `<body>` tags — just the content fragment itself.

### Including Stylesheets

For addon-specific CSS, an additional stylesheet can be included:

```html
<link rel="stylesheet" href="/ai_addons/my_addon/static/my_addon.css">
```

Prefer Bootstrap classes for layout and styling whenever possible to maintain consistency with the existing UI.

---

## 6. Build

```bash
npm run build
```

Webpack automatically picks up all `.js` files in `my_addon/static/`:

```
my_addon.js  ->  dist/my_addon-bundle.js
```

---

## Reference: Sending Socket Events

```python

# Broadcast to all clients
self.send_update_threading_and_ai.send_ai_update({"key": "value"}, "socket_my_event")

# Send to one specific client
self.send_update_threading_and_ai.send_ai_update({"key": "value"}, "socket_my_event", sid=sid)
```

---

## Reference: Targeting a Specific Client (sid Tracking)

If you want events to go to **one client only**:

1. Client registers its `sid` via POST when the tab activates
2. Addon stores it
3. Addon uses it when emitting events
4. Client unregisters via DELETE when the tab deactivates

**Backend:**
```python
def _do_initialize(self):
    self._sid_map = {}

@AiAddonAbstractClass.requires_enabled
def set_sid(self, sid: str):
    self._sid_map[sid] = some_state
    self.send_update_threading_and_ai.send_ai_update({"key": "value"}, "socket_my_event", sid=sid)

@AiAddonAbstractClass.requires_enabled
def clear_sid(self, sid: str):
    self._sid_map.pop(sid, None)
```

**Option A - sid as URL parameter**:

```python
@my_addon_namespace.route("/<string:socket_io_sid>")
class ApiSid(Resource):

    @my_addon_namespace.response(204, "Success")
    @my_addon_namespace.response(403, "Addon is disabled")
    @_handle_disabled
    def post(self, socket_io_sid: str):
        _get_addon().set_sid(socket_io_sid)
        return None, 204

    @my_addon_namespace.response(204, "Success")
    @my_addon_namespace.response(403, "Addon is disabled")
    @_handle_disabled
    def delete(self, socket_io_sid: str):
        _get_addon().clear_sid(socket_io_sid)
        return None, 204
```

```javascript
// Frontend - Option A
window.tabSubs.onActivate(TAB_ID, async () => {
    await window.post(ADDON_NAME, window.appSocket.id);
});
window.tabSubs.onDeactivate(TAB_ID, async () => {
    await window.del(ADDON_NAME, window.appSocket.id);
});
```

**Option B - sid + key in body**:

```python
SID_INPUT = my_addon_namespace.model("Sid Input", {
    "key": fields.String(),
    "sid": fields.String(),
})

@my_addon_namespace.route("/trace-sid")
class ApiTraceSid(Resource):

    @my_addon_namespace.expect(SID_INPUT)
    @my_addon_namespace.response(204, "Success")
    @my_addon_namespace.response(403, "Addon is disabled")
    @_handle_disabled
    def post(self):
        payload = my_addon_namespace.payload
        _get_addon().set_sid(payload.get("key"), payload.get("sid"))
        return None, 204

    @my_addon_namespace.expect(SID_INPUT)
    @my_addon_namespace.response(204, "Success")
    @my_addon_namespace.response(403, "Addon is disabled")
    @_handle_disabled
    def delete(self):
        payload = my_addon_namespace.payload
        _get_addon().clear_sid(payload.get("key"))
        return None, 204
```

```javascript
// Frontend - Option B
window.tabSubs.onActivate('ai_addons_my_addon', async () => {
    await window.post("my-addon", "trace-sid", { key: myKey, sid: window.appSocket.id });
});
window.tabSubs.onDeactivate('ai_addons_my_addon', async () => {
    await window.del("my-addon", "trace-sid", { key: myKey, sid: window.appSocket.id });
});
```