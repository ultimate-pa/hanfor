"""
Provides the @thread_function decorator and three helpers that work inside
any decorated function (and anywhere deeper in its call stack):

    stop_events()  -> list[threading.Event]
    is_stopped()   -> bool
    set_status(text: str) -> None

The ContextVars are populated by ThreadHandler.__run_task before the task
function is called, so no plumbing through function arguments is needed.
"""

import functools
import threading
from contextvars import ContextVar
from typing import Callable, Optional

# ---------------------------------------------------------------------------
# ContextVars – set once per thread by ThreadHandler.__run_task
# ---------------------------------------------------------------------------

_stop_events_var: ContextVar[list[threading.Event]] = ContextVar("_stop_events_var", default=[])
_set_status_var: ContextVar[Optional[Callable[[str], None]]] = ContextVar("_set_status_var", default=None)


# ---------------------------------------------------------------------------
# Public helpers – import and call freely inside @thread_function bodies
# ---------------------------------------------------------------------------


def stop_events() -> list[threading.Event]:
    """Return the stop-event list for the currently running task."""
    return _stop_events_var.get()


def is_stopped() -> bool:
    """True if any stop event has been set."""
    return any(e.is_set() for e in _stop_events_var.get())


def set_status(text: str) -> None:
    """Write text to the live task.status field (shows up in get_running_tasks())."""
    fn = _set_status_var.get()
    if fn is not None:
        fn(text)


# ---------------------------------------------------------------------------
# Decorator
# ---------------------------------------------------------------------------


def thread_function(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
