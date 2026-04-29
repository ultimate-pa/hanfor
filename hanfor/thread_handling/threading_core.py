import inspect
import logging
import threading
import time
import uuid

from ai_addons.threading_ai_socketio import send_ai_update
from configuration import threading_config
from dataclasses import dataclass, field
from enum import Enum
from queue import PriorityQueue
from typing import Optional, Callable, Any


class ThreadGroup(Enum):
    """Represents logical groups of threads for batch stopping or categorization."""

    AI = 0
    CLUSTERING = 1
    VARIABLE_HIGHLIGHTING = 2
    PATTERN_PREDICTION = 3
    OTHER = 4


class SchedulingClass(Enum):
    """Scheduling class defining priority (smaller == higher) and minimum free thread ratio required to start."""

    SYSTEM_CALL = ("syscall", 0, 0.0)
    CALLER_DEPTH_1 = ("depth1", 20, 0.7)
    CALLER_DEPTH_2 = ("depth2", 10, 0.2)

    def __init__(self, label: str, priority: int, min_free_ratio: float):
        self.label = label
        self.priority = priority
        self.min_free_ratio = min_free_ratio


@dataclass
class ThreadTask:
    """Task submitted to ThreadHandler, carrying the function, scheduling metadata, and callback."""

    thread_function: Callable[..., Any]
    scheduling_class: SchedulingClass
    group: ThreadGroup
    semaphore: Optional[threading.Semaphore]
    callback: Optional[Callable[[Any], None]]
    args: tuple
    kwargs: dict

    task_id: str = field(default_factory=lambda: str(uuid.uuid4().hex[:8]))
    task_stop_event: threading.Event = field(default_factory=threading.Event)

    queued_at: float = field(default_factory=time.time, init=False)
    started_at: Optional[float] = field(default=None, init=False)

    info_text: str = field(default="")

    status: str = field(default="", init=False)
    priority: int = field(init=False)

    def __post_init__(self):
        self.priority = self.scheduling_class.priority

        sig = inspect.signature(self.thread_function)
        if "stop_events" not in sig.parameters:
            raise ValueError(f"Thread function {self.thread_function.__name__} must accept 'stop_events'")


class TaskResult:
    """Mimics threading.Thread's interface with `.done()` and `.result()` to track task completion and results."""

    def __init__(self, task_id: str):
        self._event = threading.Event()
        self._result = None
        self._exception = None
        self._task_id: str = task_id

    def task_id(self) -> str:
        return self._task_id

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
        self.thread_task = thread_task
        self.result = result

    def __lt__(self, other):
        return self.priority < other.priority


class ThreadHandler:
    """Schedules and dispatches tasks across a fixed thread pool, respecting priority and resource limits."""

    def __init__(self, max_threads: int = threading_config.MAX_THREADS):
        self._max_threads = max_threads
        self.__queue: PriorityQueue[PrioritizedTask] = PriorityQueue()  # type: ignore
        self.__lock = threading.Lock()
        self.__active_threads = 0
        self.__active_by_priority = {sc.priority: 0 for sc in SchedulingClass}
        self.__group_stop_events: dict[ThreadGroup, threading.Event] = {
            group: threading.Event() for group in ThreadGroup
        }
        self.__running_tasks: list[PrioritizedTask] = []
        self.__socketio = None

        self.__dispatcher_thread = threading.Thread(target=self.__dispatcher, daemon=True)
        self.__dispatcher_thread.start()

    def set_socketio(self, socketio):
        self.__socketio = socketio

    def cancel_task(self, task_id: str) -> bool:
        with self.__lock:
            for prio_task in list(self.__queue.queue):
                if prio_task.thread_task.task_id == task_id:
                    prio_task.thread_task.task_stop_event.set()
                    prio_task.thread_task.status = "cancelled in queue"
                    self.__queue.queue.remove(prio_task)
                    if prio_task.result:
                        prio_task.result.set_result(None)
                    if self.__socketio:
                        send_ai_update(self.threading_data(), "socket_threading", self.__socketio)
                    return True

            for prio_task in self.__running_tasks:
                if prio_task.thread_task.task_id == task_id:
                    prio_task.thread_task.task_stop_event.set()
                    prio_task.thread_task.status = "cancel requested"
                    if self.__socketio:
                        send_ai_update(self.threading_data(), "socket_threading", self.__socketio)
                    return True

        return False

    def stop_group(self, group: ThreadGroup):
        """Stops an entire group of tasks, when running or in queue"""
        with self.__lock:
            stop_event = self.__group_stop_events[group]
            stop_event.set()
            remaining_tasks = []
            while not self.__queue.empty():
                prio_task = self.__queue.get_nowait()
                if prio_task.thread_task.group != group:
                    remaining_tasks.append(prio_task)
                else:
                    prio_task.thread_task.task_stop_event.set()
                    if prio_task.result:
                        prio_task.result.set_result(None)
                    prio_task.thread_task.status = "terminated in queue"
            for prio_task in remaining_tasks:
                self.__queue.put(prio_task)

        running_tasks_within_group = [t for t in self.__running_tasks if t.thread_task.group == group]
        for running_task in running_tasks_within_group:
            try:
                logging.info("Waiting for thread %s to terminate", running_task.thread_task)
                running_task.result.result()
                running_task.thread_task.status = "terminated thread"
            except Exception as e:
                logging.error(e)
        stop_event.clear()
        if self.__socketio:
            send_ai_update(self.threading_data(), "socket_threading", self.__socketio)

    def submit(self, thread_task: ThreadTask) -> TaskResult:
        """Queues a task and returns a TaskResult to track completion."""
        result = TaskResult(thread_task.task_id)
        prio_task = PrioritizedTask(thread_task, result)
        self.__queue.put(prio_task)
        queued = list(self.__queue.queue)
        logging.info(
            f"Queued tasks: {[(t.priority, getattr(t.thread_task.thread_function, '__name__', str(t.thread_task.thread_function))) for t in queued]}"
        )
        if self.__socketio:
            send_ai_update(self.threading_data(), "socket_threading", self.__socketio)
        return result

    def threading_data(self):
        return {
            "max_threads": self.get_max_threads(),
            "groups": [group.name for group in ThreadGroup],
            "active_tasks": self.get_running_tasks(),
            "queued_tasks": self.get_queue(),
        }

    def __what_can_start(self) -> list[SchedulingClass]:
        """
        Returns all SchedulingClass values that are allowed to start based on the current system load.
        """
        free_ratio = (self._max_threads - self.__active_threads) / self._max_threads
        return [sc for sc in SchedulingClass if free_ratio > sc.min_free_ratio]

    def __dispatcher(self):
        """
        Continuously dispatches tasks from the queue, obeying priority rules and resource limits.

        If high-priority tasks cannot start due to limited resources, lower-priority tasks may be processed instead.
        """

        while True:
            selected_task = None
            with self.__queue.not_empty:
                while not self.__queue.queue:
                    self.__queue.not_empty.wait()

                with self.__lock:
                    what_can_start = set(self.__what_can_start())
                    for task in list(self.__queue.queue):
                        thread_task = task.thread_task

                        if thread_task.scheduling_class in what_can_start:
                            if thread_task.semaphore is None or thread_task.semaphore.acquire(blocking=False):
                                selected_task = task
                                self.__queue.queue.remove(selected_task)
                                self.__active_threads += 1
                                self.__active_by_priority[selected_task.priority] = (
                                    self.__active_by_priority.get(selected_task.priority, 0) + 1
                                )
                                self.__running_tasks.append(selected_task)
                                break

            if not selected_task:
                time.sleep(0.1)
                continue

            # Start the actual worker thread
            logging.info(
                f"Starting task {selected_task.thread_task.thread_function.__name__} "
                f"(id={selected_task.thread_task.task_id}) "
                f"of type {selected_task.thread_task.scheduling_class.label}"
            )
            if self.__socketio:
                send_ai_update(self.threading_data(), "socket_threading", self.__socketio)
            thread = threading.Thread(target=self.__run_task, args=(selected_task,), daemon=True)
            thread.start()

    def __run_task(self, prio_task: PrioritizedTask):
        """Executes the task, sets the result, calls the callback, and releases if present the semaphore."""
        task = prio_task.thread_task
        task.started_at = time.time()

        stop_events: list[threading.Event] = [
            task.task_stop_event,
            self.__group_stop_events[task.group],
        ]
        if self.__socketio:
            send_ai_update(self.threading_data(), "socket_threading", self.__socketio)
        try:
            output = task.thread_function(
                *task.args,
                stop_events=stop_events,
                **task.kwargs,
            )
            if prio_task.result:
                prio_task.result.set_result(output)
            if task.callback:
                task.callback(output)
        except Exception as e:
            logging.exception(f"Exception in task: {e}")
            if prio_task.result:
                prio_task.result.set_exception(e)
            if self.__socketio:
                send_ai_update(self.threading_data(), "socket_threading", self.__socketio)
        finally:
            with self.__lock:
                self.__active_threads -= 1
                self.__active_by_priority[task.priority] -= 1
                self.__running_tasks.remove(prio_task)
                if task.semaphore:
                    task.semaphore.release()
                if self.__socketio:
                    send_ai_update(self.threading_data(), "socket_threading", self.__socketio)

    @staticmethod
    def __prioritized_task_to_dict(task: PrioritizedTask) -> dict:
        t = task.thread_task
        return {
            "function": t.thread_function.__name__,
            "group": t.group.name,
            "scheduling_class": t.scheduling_class.name,
            "status": t.status,
            "task_id": t.task_id,
            "queued_at": t.queued_at,
            "started_at": t.started_at,
            "info_text": t.info_text,
        }

    def get_queue(self) -> list[dict]:
        return [self.__prioritized_task_to_dict(task) for task in self.__queue.queue]

    def get_running_tasks(self) -> list[dict]:
        return [self.__prioritized_task_to_dict(task) for task in self.__running_tasks]

    def get_max_threads(self) -> int:
        return self._max_threads

    def get_active_count(self) -> int:
        """Returns the number of currently running threads."""
        with self.__lock:
            return self.__active_threads

    def is_idle(self) -> bool:
        """Returns True if no tasks are queued or running."""
        return self.__queue.empty() and self.get_active_count() == 0
