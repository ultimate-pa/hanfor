# AI & Threading Usage Guide

Access `ai_request` and `thread_handler` via `current_app`:

```python
from flask import current_app
ai_request     = current_app.ai_request      # AiRequest
thread_handler = current_app.thread_handler  # ThreadHandler
```

---

## Submitting Custom Tasks (`ThreadHandler`)

Decorate your function with `@thread_function`. No parameter changes needed - just write the function normally and use `is_stopped()` and `set_status()` directly.

```python
from flask import current_app
from thread_handling.thread_function_decorator import thread_function, is_stopped, set_status
from thread_handling.threading_core import ThreadTask, SchedulingClass, ThreadGroup

@thread_function
def my_task(*args, **kwargs):
    set_status("starting")
    if is_stopped():
        return "cancelled"
    # ... do work ...
    set_status("done")
    return "done"

task_result = current_app.thread_handler.submit(
    ThreadTask(
        thread_function=my_task,
        scheduling_class=SchedulingClass.SYSTEM_CALL,
        group=ThreadGroup("OTHER"),
        semaphore=None,
        callback=None,
        args=(),
        kwargs={},
        info_text="my-feature / my-task",  # shown in the threading UI
    )
)

result = task_result.result(timeout=10)
```

### `is_stopped()` and `set_status()`

These helpers are available anywhere in the call stack of a `@thread_function` - including helper methods called from it, without passing anything through parameters.

```python
from thread_handling.thread_function_decorator import is_stopped, set_status

def some_helper(data):
    set_status("processing data")   # works automatically
    if is_stopped():                # works automatically
        return None
    # ...
```

`set_status(text)` writes directly to the live `task.status` field and triggers a socket update - the new status is immediately visible in the Threading UI.

`is_stopped()` returns `True` if any stop event has been set (task cancelled, group stopped, etc.).

Both are no-ops when called outside of a `@thread_function` context, so helper functions are safe to call from anywhere.

### Scheduling classes

| Class | Priority | Starts when |
|---|---|---|
| `SYSTEM_CALL` | high (0) | at least 1 thread free |
| `CALLER_DEPTH_2` | medium (10) | > 20% of threads free |
| `CALLER_DEPTH_1` | low (20) | > 70% of threads free |

### Cancel a task

```python
task_id = task_result.task_id()
current_app.thread_handler.cancel_task(task_id)
```

### Cancelling spawned sub-tasks on abort

If your task spawns multiple child tasks (e.g. a batch of AI calls), you are responsible for cancelling them when your task is stopped or aborted. Collect all `TaskResult` references and cancel them explicitly in your abort/cleanup path:

```python
@thread_function
def my_task(*args, **kwargs):
    spawned: list[TaskResult] = []

    for item in work_items:
        if is_stopped():
            for r in spawned:
                current_app.thread_handler.cancel_task(r.task_id())
            return

        result = current_app.ai_request.ask_ai(
            prompt=item,
            info_text="my-feature / batch-item",
        )
        spawned.append(result)

    # collect results ...
```

Cancel all entries in `spawned` before returning, regardless of whether they have already started or are still queued.

### Stop an entire group

Signals all queued and running tasks in that group to stop.

```python
current_app.thread_handler.stop_group(ThreadGroup("AI"))
```

### Query status

```python
current_app.thread_handler.get_active_count()   # number of running threads
current_app.thread_handler.is_idle()            # True if queue and running tasks are empty
current_app.thread_handler.get_queue()          # list of waiting tasks
current_app.thread_handler.get_running_tasks()  # list of active tasks
```

---

## Sending AI Requests (`AiRequest`)

### Fire & forget with callback

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

### Wait for result (blocking)

```python
task_result = current_app.ai_request.ask_ai(
    prompt="What is the capital of France?",
    info_text="my-feature / capital-lookup",
)

response, status = task_result.result(timeout=30)
```

### With explicit provider / model

```python
task_result = current_app.ai_request.ask_ai(
    prompt="Write a poem.",
    provider="ollama",                         # optional – falls back to default provider
    model_name="llama3",                       # optional – falls back to default model
    api_method_name="standard_ai_api",         # optional – falls back to first available
    info_text="my-feature / poem-generator",
)
```

### Non-blocking poll

```python
task = current_app.ai_request.ask_ai(
    prompt="Hello!",
    info_text="my-feature / hello",
)

while not task.done():
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
- `(str, "ai_response_received")` - success
- `(None, "cancelled")` - stopped via `is_stopped()`
- `(None, "error_...")` - any error condition

---

## The Threading & AI Addons UI
 
Available at **Threading & AI Addons** in the navigation bar.
 
**Threading tab** - live thread pool state. Running and queued tasks show `info_text` and the current `set_status()` value. Per-group **STOP** buttons and per-task **X** cancel buttons.
 
**AI tab** - provider and model status, test and default buttons, rescan and full test sweep at the top. AI Addons list with activate/deactivate toggles below.

---

## Configurations

The configurations for threading and AI are located in the `configurations` folder.

There, you can:
- Add new AI providers along with their corresponding information.
- Configure threading settings, such as the maximum number of threads allowed.