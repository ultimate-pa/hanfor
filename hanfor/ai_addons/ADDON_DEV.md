# Writing a New AI Addon

There is a sample AI addon (`example_ai_addon`) that you can use to get an idea of the structure of an AI addon.

If you follow the instructions, you don't need to do anything else. Your addon will be automatically detected and will be accessible via the web.
You can enable or disable the add-on via the web.


## 1. File Structure
`my_addon` is only a placeholder name. You can name your addon however you want.

The filename of the file containing the implementation of `AiAddonAbstractClass` (more in 2.) will be the id of this addon.

    ai_addon/
    ├── my_addon/                # your own folder
    │   ├── my_addon.py          # addon class
    │   └── (any other files)
    │
    └── ui/
        └── api/
            ├── my_addon_api.py  # blueprint + routes
            ├── __init__.py      # register blueprint here
            ├── static/
            │   └── my_addon.js  # bundled to dist/my_addon-bundle.js
            └── templates/
                └── ai_addons/
                    └── my_addon.html

---

## 2. Addon Class

Create **one class per addon**, implementing `AiAddonAbstractClass`.

The base class handles:
- `enabled` property
- `toggle_addon()` (flips `_enabled`, triggers `initialize()`)
- `initialize()` (calls `_do_initialize()` exactly once while enabled)
- dependency injection via `required_dependencies`

Declare `required_dependencies` with the names of what you need - they are injected
automatically into `__init__` together with `enabled`.

Never define `__init__` in your subclass. Put all initialization logic in `_do_initialize()` instead.

```python
from ai_addon.ai_addon_abstract_class import AiAddonAbstractClass

class MyAddon(AiAddonAbstractClass):

    # Declare dependencies - injected automatically from **kwargs
    required_dependencies = ["thread_handler", "ai_request", "socketio"]

    # Type hints for IDE support (no runtime effect)
    thread_handler: ThreadHandler
    ai_request: AiRequest
    socketio: SocketIO

    def __init__(self, enabled: bool, **kwargs):
        super().__init__(enabled, **kwargs)

    @property
    def addon_name(self) -> str:
        return "My Addon"

    @property
    def addon_description(self) -> str:
        return "Does something useful."

    @property
    def addon_html(self) -> str:
        return "ai_addons/my_addon.html"

    @property
    def addon_js(self) -> str:
        return "dist/my_addon-bundle.js"

    def _do_initialize(self):
        # Called automatically once when the addon is enabled.
        # self.thread_handler, self.ai_request, self.socketio are available here.
        pass
```

### What the base class provides

| Member | Description                                            |
|---|--------------------------------------------------------|
| `self.enabled` | Returns `self._enabled`                                |
| `toggle_addon()` | Flips `_enabled`, calls `initialize()`                 |
| `initialize()` | Calls `_do_initialize()` once while enabled            |
| `_do_initialize()` | **Abstract** - your initialization logic goes here     |
| `requires_enabled` | Decorator - function will not be called if not enabled |

### Available dependencies

    thread_handler
    ai_request
    socketio

Use the decorator below for methods that should **do nothing when the addon is disabled**:

```python
@AiAddonAbstractClass.requires_enabled
def do_something(self):
    pass
```

---

## 3. API Routes

Create `ui/api/my_addon_api.py`.

```python
from flask import Blueprint

my_addon_blueprint = Blueprint(
    "my_addon", __name__, url_prefix="/ai_addons/my_addon"
)

@my_addon_blueprint.route("/data")
def get_data():
    ...
```

Then **register the blueprint** in:

    ui/api/__init__.py

There you need to add your blueprint into the `all_threading_ai_addon_blueprints` list.

Before creating new endpoints, check:

    ai_core_addon_api.py

It already contains **shared endpoints** (e.g. provider data, request IDs).

---

## 4. Frontend JS

### Tab ID

The tab ID is always derived from `addon_html`.

    "ai_addons/my_addon.html" -> "ai_addons_my_addon"

This is used for the socket connection.

---

### Socket + Lifecycle

```javascript
// Socket events - only active while the tab is visible
window.tabSubs.register('ai_addons_my_addon', [ //<- tab-id
  {
    event: 'socket_my_event',
    handler: (data) => {
      // update UI
    }
  }
]);

// Runs every time the user switches to your tab
window.tabSubs.onActivate('ai_addons_my_addon', () => {
  loadMyData();
});

window.tabSubs.onDeactivate('ai_addons_my_addon', () => {
  unloadSomething();
});

// Bottom of file: one-time loads only (static data that never changes)
loadStaticData();
```

### Important rules

**Never do this:**

```javascript
window.appSocket.on(...)
```

Always use:

    tabSubs.register(...)

Also **never call `load()` at the bottom of the file**.
Use `onActivate()` instead.

---

## 5. Configuration

Add a feature flag to:

    configuration/ai_config.py

```python
ADDON_MY_ADDON = False
```

Naming convention:

    my_addon  →  ADDON_MY_ADDON

---

## 6. Webpack

Register the JS file in:

    static/webpack.config.js

```javascript
my_addon: __dirname + '/../ai_addon/ui/api/static/my_addon.js',
```

The bundle name must match what `addon_js` returns.

Example:

    my_addon → dist/my_addon-bundle.js

---

## 7. Sending Socket Events

Use `send_ai_update` from:

    ai_addon/threading_ai_socketio.py

```python
from ai_addon.threading_ai_socketio import send_ai_update

# broadcast to all clients
send_ai_update({"key": "value"}, "socket_my_event", self.socketio)

# send to one client only
send_ai_update({"key": "value"}, "socket_my_event", self.socketio, sid=sid)
```

---

## 8. Targeting a Specific Client (sid)

If you want to send updates **only to one client**, you must track the `sid`.

The pattern is:

1. Client sends `window.appSocket.id`
2. Addon stores it
3. Addon uses it when emitting events

### Backend

```python
def _do_initialize(self):
    self._sid_map = {}  # example: { req_id: sid }

def set_sid(self, key, sid):
    self._sid_map[key] = sid

def clear_sid(self, key):
    self._sid_map.pop(key, None)
```

```python
@my_addon_blueprint.route("/set_sid", methods=["POST"])
def set_sid():
    payload = request.json
    _get_addon().set_sid(payload.get("key"), payload.get("sid"))
    return "", 204


@my_addon_blueprint.route("/clear_sid", methods=["POST"])
def clear_sid():
    payload = request.json
    _get_addon().clear_sid(payload.get("key"))
    return "", 204
```

### Frontend

```javascript
await fetch('/ai_addons/my_addon/set_sid', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    key: myKey,
    sid: window.appSocket.id
  })
});
```

```javascript
await fetch('/ai_addons/my_addon/clear_sid', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    key: myKey
  })
});
```

---

## 9. Auto-Discovery

Addons are **automatically discovered and instantiated**.

The handler:

1. Scans every subdirectory in `ai_addon/`
2. Finds classes implementing `AiAddonAbstractClass`
3. Instantiates them with dependencies + `enabled` flag

### Addon Key

    ai_addon/my_addon/my_addon.py

→ key:

    "my_addon"

### Config Mapping

    my_addon → ADDON_MY_ADDON

If the flag is missing:

- addon defaults to **disabled**
- a **warning is logged**

---

## 10. Accessing Addons at Runtime

Get **all addons**:

```python
current_app.ai_addons.get_all_addons()
```

Example return:

    {
      "my_addon": instance,
      ...
    }

Get **one addon**:

```python
current_app.ai_addons.get_addon("my_addon")
```

### Typical API Pattern

```python
def _get_addon():
    return current_app.ai_addons.get_addon("my_addon")


@my_addon_blueprint.route("/data")
def get_data():
    return jsonify(_get_addon().some_method())
```

---

## 11. HTML Template

Always include the shared stylesheet at the top:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/ai_addons.css') }}">
```

`ai_addons.css` already provides:
- CSS variables (`--bg-primary`, `--success`, `--warning`, `--danger`, `--radius-md`, ...)
- Layout utilities: `.page`, `.section`, `.section-header`, `.metrics`, `.hscroll`
- Components: `.badge`, `.led`, `.dot`, `.bar-wrap`, `.group-card`, `.task-row`
- Addon cards: `.addon-grid`, `.addon-card`, `.status-tag`
- Provider/model cards: `.provider-card`, `.model-card`, `.test-btn`, `.default-btn`

The template is rendered via `{% include page %}` inside the tab system - no `<html>`, `<head>`, or `<body>` tags, just your content fragment.