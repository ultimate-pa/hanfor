import inspect
import logging
import threading
import time
import config
from dataclasses import dataclass, field
from enum import Enum
from queue import PriorityQueue
from typing import Optional, Callable, Any


class ThreadGroup(Enum):
    """Represents logical groups of threads for batch stopping or categorization."""

    AI_FORMALIZATION = 0
    CLUSTERING = 1
    VARIABLE_HIGHLIGHTING = 2
    OTHER = 3


class SchedulingClass(Enum):
    """
    Represents the scheduling class of a thread.

    Attributes:
        label (str): Human-readable label for logging.
        priority (int): Priority for task selection; lower numbers = higher priority.
        min_free_ratio (float): Minimum free thread ratio required before this task can start.
    """

    SYSTEM_CALL = ("syscall", 0, 0.0)
    CALLER_DEPTH_1 = ("depth1", 20, 0.7)
    CALLER_DEPTH_2 = ("depth2", 10, 0.2)

    def __init__(self, label: str, priority: int, min_free_ratio: float):
        self.label = label
        self.priority = priority
        self.min_free_ratio = min_free_ratio


@dataclass
class ThreadTask:
    """
    Represents a single task to be executed in a ThreadHandler.

    Attributes:
        thread_function: The function to execute; must accept `stop_event`.
        scheduling_class: Determines priority and resource constraints.
        group: Logical group for collective stopping.
        callback: Optional callback called with result.
        args: Positional arguments for the thread function.
        kwargs: Keyword arguments for the thread function.
        status: Current status of the task (internal tracking).
        priority: Cached priority from scheduling_class.
    """

    thread_function: Callable[..., Any]
    scheduling_class: SchedulingClass
    group: ThreadGroup
    callback: Optional[Callable[[Any], None]]
    args: tuple
    kwargs: dict

    status: str = field(default="", init=False)
    priority: int = field(init=False)

    def __post_init__(self):
        self.priority = self.scheduling_class.priority

        sig = inspect.signature(self.thread_function)
        if "stop_event" not in sig.parameters:
            raise ValueError(f"Thread function {self.thread_function.__name__} must accept 'stop_event'")


class TaskResult:
    """Mimics threading.Thread's interface with `.done()` and `.result()` to track task completion and results."""

    def __init__(self):
        self._event = threading.Event()
        self._result = None
        self._exception = None

    def set_result(self, result: Any):
        self._result = result
        self._event.set()

    def set_exception(self, exception: Exception):
        self._exception = exception
        self._event.set()

    def result(self, timeout: float = None) -> Any:
        if not self._event.wait(timeout):
            raise TimeoutError("Task did not complete in time.")
        if self._exception:
            raise self._exception
        return self._result

    def done(self) -> bool:
        return self._event.is_set()


class PrioritizedTask:
    """Internal helper class to wrap tasks with priority and result tracking."""

    def __init__(self, thread_task: ThreadTask, result: TaskResult):
        self.priority = thread_task.priority
        self.task = thread_task
        self.result = result

    def __lt__(self, other):
        return self.priority < other.priority


class ThreadHandler:
    def __init__(self, max_threads: int = config.MAX_THREADS):
        self.max_threads = max_threads
        self.semaphore = threading.Semaphore(max_threads)
        self.queue = PriorityQueue()
        self.lock = threading.Lock()
        self.active_threads = 0
        self.active_by_priority = {sc.priority: 0 for sc in SchedulingClass}
        self.group_stop_events: dict[ThreadGroup, threading.Event] = {group: threading.Event() for group in ThreadGroup}
        self.running_tasks: list[PrioritizedTask] = []

        self.dispatcher_thread = threading.Thread(target=self.__dispatcher, daemon=True)
        self.dispatcher_thread.start()

    def stop_group(self, group: ThreadGroup):
        """Stops an entire group of tasks, when running or in queue"""
        with self.lock:
            stop_event = self.group_stop_events[group]
            stop_event.set()
            remaining_tasks = []
            while not self.queue.empty():
                task = self.queue.get_nowait()
                if task.task.group != group:
                    remaining_tasks.append(task)
                else:
                    if task.result:
                        task.result.set_result(None)
                    task.task.status = "terminated in queue"
            for task in remaining_tasks:
                self.queue.put(task)

        running_tasks = [t for t in self.running_tasks if t.task.group == group]
        for task in running_tasks:
            try:
                logging.info("Waiting for thread %s to terminate", task.task)
                task.result.result()
            except Exception:
                pass

    def submit(self, thread_task: ThreadTask) -> TaskResult:
        """
        Submits a new task to the queue with a given priority.
        Returns a TaskResult object to query task completion and result.
        """
        result = TaskResult()

        task = PrioritizedTask(thread_task, result)
        self.queue.put(task)
        queued = list(self.queue.queue)
        logging.warning(
            f"Queued tasks: {[ (t.priority, getattr(t.task.thread_function, '__name__', str(t.task.thread_function))) for t in queued ]}"
        )
        return result

    def __can_start(self, sched_class: SchedulingClass) -> bool:
        """Check if a task of a given scheduling class can start based on current load."""

        total_active = self.active_threads
        max_threads = self.max_threads
        free_slots = max_threads - total_active
        free_ratio = free_slots / max_threads
        return free_ratio >= sched_class.min_free_ratio

    def __dispatcher(self):
        """Continuously dispatches tasks from the queue, obeying priority rules and resource limits."""
        while True:
            task = self.queue.get()

            # Acquire semaphore to limit total threads
            self.semaphore.acquire()
            started = False
            while not started:
                with self.lock:
                    if self.__can_start(task.task.scheduling_class):
                        # Update counters
                        self.active_threads += 1
                        self.active_by_priority[task.task.priority] = (
                            self.active_by_priority.get(task.task.priority, 0) + 1
                        )
                        started = True
                    else:
                        # Cannot start now, release semaphore and wait
                        self.semaphore.release()
                if not started:
                    time.sleep(0.1)  # short wait before retry
                    self.semaphore.acquire()

            # Start the actual worker thread
            logging.info(
                f"Starting task {task.task.thread_function.__name__} of type {task.task.scheduling_class.label}"
            )
            t = threading.Thread(target=self.__run_task, args=(task,), daemon=True)
            with self.lock:
                self.running_tasks.append(task)
            t.start()

    def __run_task(self, task: PrioritizedTask):
        """Runs the given funktion and sets the result and calls callback"""
        try:
            output = task.task.thread_function(
                *task.task.args, stop_event=self.group_stop_events[task.task.group], **task.task.kwargs
            )
            if task.result:
                task.result.set_result(output)
            if task.task.callback:
                task.task.callback(output)
        except Exception as e:
            logging.exception(f"Exception in task: {e}")
            if task.result:
                task.result.set_exception(e)
        finally:
            with self.lock:
                self.active_threads -= 1
                self.active_by_priority[task.task.priority] -= 1
                self.running_tasks.remove(task)
            self.semaphore.release()

    def get_active_count(self) -> int:
        with self.lock:
            return self.active_threads

    def is_idle(self) -> bool:
        return self.queue.empty() and self.get_active_count() == 0
