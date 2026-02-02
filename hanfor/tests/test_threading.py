from unittest import TestCase
import time
from thread_handling.threading_core import ThreadHandler, ThreadTask, ThreadGroup, SchedulingClass, TaskResult


def timout_task(seconds, rtn, stop_event):
    time.sleep(seconds)
    return rtn


def stopping_task(mseconds, stop_event):
    for _ in range(mseconds):
        if stop_event.is_set():
            return "stopped"
        time.sleep(0.001)
    return "completed"


class TestThreadHandler(TestCase):
    def setUp(self):
        self.handler = ThreadHandler(max_threads=5)

    def test_simple_task_execution(self):
        self.handler.max_threads = 5
        results = []

        tasks = [
            ThreadTask(
                thread_function=timout_task,
                scheduling_class=SchedulingClass.SYSTEM_CALL,
                group=ThreadGroup.OTHER,
                callback=lambda r: results.append(r),
                args=(
                    1,
                    "done",
                ),
                kwargs={},
            )
            for _ in range(15)
        ]

        for task in tasks:
            self.handler.submit(task)

        time.sleep(1.5)
        print(self.handler.get_active_count())
        self.assertCountEqual(results, ["done"] * 5)
        time.sleep(1)
        self.assertCountEqual(results, ["done"] * 10)
        time.sleep(1)
        self.assertCountEqual(results, ["done"] * 15)

    def test_group_stop(self):
        self.handler.max_threads = 1
        task1 = ThreadTask(
            stopping_task, SchedulingClass.CALLER_DEPTH_1, ThreadGroup.OTHER, None, args=(5000,), kwargs={}
        )
        task2 = ThreadTask(
            stopping_task, SchedulingClass.CALLER_DEPTH_1, ThreadGroup.OTHER, None, args=(5000,), kwargs={}
        )
        self.handler.submit(task1)
        self.handler.submit(task2)

        time.sleep(1)
        self.handler.stop_group(ThreadGroup.OTHER)

        result1 = task1.status
        result2 = task2.status
        self.assertIn(result1, "terminated thread")
        self.assertIn(result2, "terminated in queue")

    def test_multiple_callbacks(self):
        self.handler.max_threads = 5
        results = []

        for i in range(3):
            task = ThreadTask(
                timout_task,
                SchedulingClass.SYSTEM_CALL,
                ThreadGroup.OTHER,
                lambda r, idx=i: results.append((idx, r)),
                args=(1, f"done{i}"),
                kwargs={},
            )
            self.handler.submit(task)

        time.sleep(1.5)
        self.assertCountEqual([r[1] for r in results], ["done0", "done1", "done2"])

    def test_idle_detection(self):
        self.handler.max_threads = 5
        task = ThreadTask(timout_task, SchedulingClass.SYSTEM_CALL, ThreadGroup.OTHER, None, args=(1, "x"), kwargs={})
        self.handler.submit(task)
        time.sleep(0.1)
        self.assertFalse(self.handler.is_idle())
        time.sleep(1.2)
        self.assertTrue(self.handler.is_idle())

    def test_priority_order(self):
        self.handler.max_threads = 5
        results = []

        low_task = ThreadTask(
            timout_task,
            SchedulingClass.CALLER_DEPTH_2,
            ThreadGroup.OTHER,
            lambda r: results.append(("low", r)),
            args=(1, "low"),
            kwargs={},
        )
        high_task = ThreadTask(
            timout_task,
            SchedulingClass.CALLER_DEPTH_1,
            ThreadGroup.OTHER,
            lambda r: results.append(("high", r)),
            args=(1, "high"),
            kwargs={},
        )

        self.handler.submit(low_task)
        self.handler.submit(high_task)

        time.sleep(0.2)
        self.assertTrue(("high", "high") in results or len(results) == 0)
        time.sleep(1.5)
        self.assertCountEqual([r[1] for r in results], ["high", "low"])

    def test_group_stop_with_other_groups(self):
        self.handler.max_threads = 5
        task1 = ThreadTask(
            stopping_task,
            SchedulingClass.CALLER_DEPTH_1,
            ThreadGroup.VARIABLE_HIGHLIGHTING,
            None,
            args=(2000,),
            kwargs={},
        )
        task2 = ThreadTask(
            stopping_task, SchedulingClass.CALLER_DEPTH_1, ThreadGroup.OTHER, None, args=(2000,), kwargs={}
        )

        for _ in range(10):
            res_var_highlite = self.handler.submit(task1)
            self.handler.submit(task2)

        time.sleep(1)
        self.handler.stop_group(ThreadGroup.OTHER)
        time.sleep(1)
        result_1 = task2.status
        result_2 = res_var_highlite.result()
        print(result_1, result_2)
