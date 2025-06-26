import threading
import logging
from queue import PriorityQueue
from typing import Callable, Any, Tuple


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

    def __init__(self, priority: int, func: Callable, args: Tuple[Any, ...] = (), result: "TaskResult" = None):
        self.priority = priority
        self.func = func
        self.args = args
        self.result = result

    def __lt__(self, other: "PrioritizedTask") -> bool:
        return self.priority < other.priority


class AiThreadManager:
    """Manages concurrent AI tasks with resource-limited priority-based scheduling."""

    def __init__(self, max_threads: int):
        self.max_threads = max_threads
        self.semaphore = threading.Semaphore(max_threads)
        self.queue = PriorityQueue()
        self.lock = threading.Lock()
        self.active_threads = 0
        # Track active threads per priority
        self.active_by_priority = {1: 0, 2: 0, 3: 0}
        self.dispatcher_thread = threading.Thread(target=self.__dispatcher, daemon=True)
        self.dispatcher_thread.start()

    def submit(self, func: Callable, args: Tuple[Any, ...] = (), priority: int = 3) -> TaskResult:
        """
        Submits a new task to the queue with a given priority.
        Returns a TaskResult object to query task completion and result.
        """
        result = TaskResult()
        task = PrioritizedTask(priority, func, args, result)
        self.queue.put(task)
        queued = list(self.queue.queue)
        logging.warning(f"Queued tasks: {[ (t.priority, getattr(t.func, '__name__', str(t.func))) for t in queued ]}")
        return result

    def __can_start(self, priority: int) -> bool:
        """Checks if a task with given priority is allowed to start"""

        total_active = self.active_threads
        max_threads = self.max_threads
        free_slots = max_threads - total_active
        free_ratio = free_slots / max_threads
        if priority == 1:
            # Priority 1 can start if there is at least one free resource (Human interaction)
            return free_slots > 0

        elif priority == 2:
            # Priority 2 can start only if more than 20% of resources are free
            return free_ratio > 0.2

        else:
            # Priority 3 and higher can start only if more than 70% of resources are free
            return free_ratio > 0.7

    def __dispatcher(self):
        """Continuously dispatches tasks from the queue, obeying priority rules and resource limits."""
        while True:
            task = self.queue.get()

            # Acquire semaphore to limit total threads
            self.semaphore.acquire()
            started = False
            while not started:
                with self.lock:
                    print(self.__can_start(task.priority))
                    if self.__can_start(task.priority):
                        # Update counters
                        self.active_threads += 1
                        self.active_by_priority[task.priority] += 1
                        started = True
                    else:
                        # Cannot start now, release semaphore and wait
                        self.semaphore.release()
                if not started:
                    threading.Event().wait(0.1)  # short wait before retry
                    self.semaphore.acquire()

            # Start the actual worker thread
            t = threading.Thread(target=self.__run_task, args=(task,), daemon=True)
            t.start()

    def __run_task(self, task: PrioritizedTask):
        try:
            output = task.func(*task.args)
            if task.result:
                task.result.set_result(output)
        except Exception as e:
            logging.exception(f"Exception in task: {e}")
            if task.result:
                task.result.set_exception(e)
        finally:
            with self.lock:
                self.active_threads -= 1
                self.active_by_priority[task.priority] -= 1
            self.semaphore.release()

    def get_active_count(self) -> int:
        with self.lock:
            return self.active_threads

    def is_idle(self) -> bool:
        return self.queue.empty() and self.get_active_count() == 0
