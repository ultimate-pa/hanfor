# Threading Usage Guide
Hanfor runs background tasks like AI calls and batch jobs in a managed thread pool.
This guide explains how to submit tasks, track their state, and cancel them cleanly.
Scheduling and capacity are handled automatically.
You only need to define your task and choose the right scheduling class.

Access `thread_handler` via `current_app`:

```python
from flask import current_app
thread_handler = current_app.thread_handler  # ThreadHandler
```

---

## Concepts

### ThreadGroup

A `ThreadGroup` is a named label that groups related tasks together. It allows you to stop all tasks of a certain kind at once (e.g. all AI calls, all background jobs).

```python
from thread_handling.threading_core import ThreadGroup

ThreadGroup("AI")
ThreadGroup("MY_SPETIAL_TASK")
```

You define the group name yourself - use consistent names across your feature.

### SchedulingClass

The `SchedulingClass` controls when a task is allowed to start based on how many threads are currently free.

| Class | Priority | Starts when |
|---|---|---|
| `SYSTEM_CALL` | high (0) | at least 1 thread free |
| `CALLER_DEPTH_2` | medium (10) | > 20% of threads free |
| `CALLER_DEPTH_1` | low (20) | > 70% of threads free |

Use `SYSTEM_CALL` for tasks which are not spawning new threads. Use `CALLER_DEPTH_1` for threads that spawn new threads. Use `CALLER_DEPTH_2` for threads spawned by another thread. This way spawner threads cannot overfill the thread pool.

### `is_stopped()` and `set_status()`

These helpers are available anywhere in the call stack of a `@thread_function` (see [Submitting Custom Tasks](#submitting-custom-tasks)) - including helper methods called from it, without passing anything through parameters.

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

### TaskResult

`TaskResult` is the object returned by `submit()` and `ask_ai()`. It lets you track the state of a running task and retrieve its result.

```python
task_result = current_app.thread_handler.submit(...)
```

| Method | Description |
|---|---|
| `.done()` | Returns `True` if the task has finished (non-blocking) |
| `.result(timeout=None)` | Blocks until the task finishes and returns its return value. Raises `TimeoutError` if the timeout (in seconds) is exceeded. Raises the original exception if the task failed. |
| `.task_id()` | Returns the task's ID string, used for cancellation |

---

## Submitting Custom Tasks

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
        info_text="my-feature / my-task",  # shown in the Threading UI
    )
)

return_value = task_result.result(timeout=10)  # blocks; raises TimeoutError if exceeded
```

## Cancel a Task

```python
task_id = task_result.task_id()
current_app.thread_handler.cancel_task(task_id)
```

## Cancelling Spawned Sub-Tasks on Abort

If your task spawns multiple child tasks (e.g. a batch of AI calls), you are responsible for cancelling them when your task is stopped or aborted. Collect all `TaskResult` references and cancel them explicitly in your abort/cleanup path:

```python
from thread_handling.threading_core import TaskResult

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

    results = [r.result(timeout=30) for r in spawned]
```

Cancel all entries in `spawned` before returning, regardless of whether they have already started or are still queued.

## Stop an Entire Group

Signals all queued and running tasks in that group to stop.

```python
current_app.thread_handler.stop_group(ThreadGroup("AI"))
```

## Query Status

```python
current_app.thread_handler.get_active_count()   # number of running threads
current_app.thread_handler.is_idle()            # True if queue and running tasks are empty
current_app.thread_handler.get_queue()          # list of waiting tasks
current_app.thread_handler.get_running_tasks()  # list of active tasks
```

---

## Threading UI

Available at **Threading & AI** in the navigation bar, under the **Threading** tab.

Shows the live state of the thread pool:

- All running and queued tasks with their `info_text` and current `set_status()` value
- Per-group **STOP** buttons to cancel all tasks in a group
- Per-task **X** buttons to cancel individual tasks

## Configuration

Threading settings are managed in the configurations folder, where you can define the maximum number of threads. The minimum allowed value is 2.