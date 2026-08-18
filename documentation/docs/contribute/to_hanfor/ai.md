# AI Usage Guide

Hanfor provides abstractions that make it straightforward to integrate LLMs into features.
An abstraction layer handles provider setup, model selection, and threading - 
so you only need to send a prompt and handle the response.

Access `ai_request` via `current_app`:

```python
from flask import current_app
ai_request = current_app.ai_request  # AiRequest
```

---

## Sending AI Requests

### Fire & Forget with Callback

```python
from flask import current_app

def my_callback(result):
    response, status = result
    print(f"Status: {status}, Response: {response}")

current_app.ai_request.ask_ai(
    prompt="Explain Python in one sentence.",
    callback=my_callback,
    info_text="my-feature / explain-python",  # shown in the threading UI
)
```

### Wait for Result (Blocking)
Useful when you're already running in a background thread and need the AI response
before continuing. The current thread pauses until the response arrives or the timeout is reached.

```python
task_result = current_app.ai_request.ask_ai(
    prompt="What is the capital of France?",
    info_text="my-feature / capital-lookup",
)

response, status = task_result.result(timeout=30)
```

### With Explicit Provider / Model

```python
task_result = current_app.ai_request.ask_ai(
    prompt="Write a poem.",
    provider="ollama",                         # optional – falls back to default provider
    model_name="llama3",                       # optional – falls back to default model
    api_method_name="standard_ai_api",         # optional – falls back to first available
    info_text="my-feature / poem-generator",
)
```

### Non-Blocking Poll
Useful when you need to do work while waiting - for example, checking for a stop signal.

```python
task = current_app.ai_request.ask_ai(
    prompt="Hello!",
    info_text="my-feature / hello",
)

while not task.done():
    if is_stopped():
        return
    time.sleep(0.1)

response, status = task.result()
```

`query_api` runs as its own `ThreadTask` (submitted internally by `ask_ai`), so `is_stopped()` reacts to cancellation of that specific AI request via the returned `TaskResult`.

---

## Implementing a Custom API Method

Add a new file to `ai_request/api_request_methods/my_method.py`. It will be auto-discovered and registered on the next startup.

```python
from typing import Optional
from ai_request.ai_api_methods_abstract_class import AiApiMethod
from thread_handling.thread_function_decorator import is_stopped, set_status

class MyCustomMethod(AiApiMethod):

    def query_api(
        self,
        query: str,
        url: str,
        api_key: str,
        model_name: str,
        other_params: Optional[dict],
    ) -> tuple[str | None, str]:
        if is_stopped():
            return None, "cancelled"

        set_status("connecting...")
        # ... perform HTTP request ...

        set_status("streaming response...")
        # ... stream / parse response ...

        return "response text", "ai_response_received"
```

`query_api` runs as its own `ThreadTask` (submitted internally by `ask_ai`), so `is_stopped()` reacts to cancellation of that specific AI request via the returned `TaskResult`.

Return values of `query_api`:

| Return value | Meaning |
|---|---|
| `(str, "ai_response_received")` | success |
| `(None, "cancelled")` | stopped via `is_stopped()` |
| `(None, "error_...")` | any error condition |

---

## The Threading & AI UI

Available at **Threading & AI** in the navigation bar.

**Threading tab** – live thread pool state. Running and queued tasks show `info_text` and the current `set_status()` value. Per-group **STOP** buttons and per-task **X** cancel buttons.

**AI tab** – provider and model status, test and default buttons, rescan and full test sweep at the top. AI Addons list with activate/deactivate toggles below.

---

## Configurations

The configurations for AI are located in the `configurations` folder. There you can add new AI providers along with their corresponding information.