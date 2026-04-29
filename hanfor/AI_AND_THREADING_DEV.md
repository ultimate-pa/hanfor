# AI & Threading Usage Guide

Access `ai_request` and `thread_handler` via `current_app`:

```python
from flask import current_app
ai_request     = current_app.ai_request      # AiRequest
thread_handler = current_app.thread_handler  # ThreadHandler
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
    api_method_name="ollama_standard_api",     # optional – falls back to first available
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

`ask_ai` always returns a `TaskResult`. Use `.result(timeout)` to block or `.done()` to poll.

---

## Submitting Custom Tasks (`ThreadHandler`)

Every function submitted as a task **must** accept a `stop_events` parameter and check it regularly to support cancellation.

```python
from flask import current_app
from thread_handling.threading_core import ThreadTask, SchedulingClass, ThreadGroup

def my_task(*args, stop_events=None, **kwargs):
    if stop_events and any(e.is_set() for e in stop_events):
        return "cancelled"
    # ... do work ...
    return "done"

task_result = current_app.thread_handler.submit(
    ThreadTask(
        thread_function=my_task,
        scheduling_class=SchedulingClass.SYSTEM_CALL,
        group=ThreadGroup.OTHER,
        semaphore=None,
        callback=None,
        args=(),
        kwargs={},
        info_text="my-feature / my-task",  # shown in the threading UI
    )
)

result = task_result.result(timeout=10)
```

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

If your task spawns multiple child tasks (e.g. a batch of AI calls), you are responsible for cancelling them when your task is stopped or aborted. Simply checking `stop_events` and returning is not enough - any already-submitted child tasks will keep running otherwise.

Collect all `TaskResult` references and cancel them explicitly in your abort/cleanup path:

```python
def my_task(*args, stop_events=None, **kwargs):
    spawned: list[TaskResult] = []

    for item in work_items:
        if stop_events and any(e.is_set() for e in stop_events):
            # cancel everything submitted so far and bail out
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

The same pattern applies when aborting mid-collection - cancel all entries in `spawned` before returning, regardless of whether they have already started or are still queued.

### Stop an entire group

Signals all queued and running tasks in that group to stop via their `stop_events`.

```python
current_app.thread_handler.stop_group(ThreadGroup.AI)
```

### Query status

```python
current_app.thread_handler.get_active_count()   # number of running threads
current_app.thread_handler.is_idle()            # True if queue and running tasks are empty
current_app.thread_handler.get_queue()          # list of waiting tasks
current_app.thread_handler.get_running_tasks()  # list of active tasks
```

---

## Implementing a Custom API Method

Add a new file to `ai_request/api_request_methods/my_method.py`. It will be auto-discovered and registered on the next startup.

```python
import threading
from typing import Optional
from ai_request.ai_api_methods_abstract_class import AiApiMethod

class MyCustomMethod(AiApiMethod):

    @property
    def provider_names_which_work_with_api_method(self) -> list[str]:
        return ["my_provider"]  # must match the provider name in ai_config

    def query_api(
        self,
        query: str,
        url: str,
        api_key: str,
        model_name: str,
        other_params: Optional[dict],
        stop_events: Optional[list[threading.Event]],
    ) -> tuple[str | None, str]:
        if stop_events and any(e.is_set() for e in stop_events):
            return None, "cancelled"

        # ... perform HTTP request ...
        return "response text", "ai_response_received"
```

Return values of `query_api`:
- `(str, "ai_response_received")` - success
- `(None, "cancelled")` - stopped via stop_events
- `(None, "error_...")` - any error condition

---

## The Threading & AI Addons UI

Available at **Threading & AI Addons** in the navigation bar. At least 2 tabs:

### Threading tab

Shows the live state of the thread pool.

**Thread Dashboard** - active thread count, free threads, tasks in queue, and max threads, plus a utilisation bar.

**Groups** - one badge per `ThreadGroup` (`AI`, `CLUSTERING`, `VARIABLE_HIGHLIGHTING`, `PATTERN_PREDICTION`, `OTHER`) for now. Each badge shows how many tasks are running / queued in that group and has a **STOP** button that calls `stop_group()` for that group.

**Running Tasks / Queued Tasks** - each row shows:
- the function name and `info_text` (e.g. `query_api() - PP for ELS-1 - ollama | llama3.1:8b`)
- the `ThreadGroup` badge and `SchedulingClass` label
- how long the task has been running
- a **X** button to cancel that individual task

This is where `info_text` matters - a descriptive value like `"PP for ELS-1"` makes it immediately clear which feature and which item a task belongs to, without having to guess from the function name alone.

### AI tab

Shows all configured LLM providers and their models.

Each provider card displays the provider name, max concurrent requests, API method, and URL. Each model within it has a colored status dot (green = active, yellow = not Tested red = inactive/not found), a **test** button to re-run the reachability check for that model, and a **set default** button. Provider-level **test** and **set default** buttons work the same way at the provider level.

The **Rescan Provider Config** and **Test All Providers** buttons at the top trigger a full config reload and a full reachability sweep respectively.

**AI Addons** section below lists all registered addons with their description and an activate/deactivate toggle.

---

## Configurations

The configurations for threading and AI are located in the `configurations` folder.

There, you can:
- Add new AI providers along with their corresponding information.
- Configure threading settings, such as the maximum number of threads allowed.