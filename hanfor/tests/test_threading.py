import json
from threading import Semaphore
from unittest import TestCase
import time

from ai_addons.threading_ai_socketio import SendUpdateThreadingAndAi
from tests.mock_hanfor import MockHanfor
from thread_handling.thread_function_decorator import thread_function, is_stopped
from thread_handling.threading_core import ThreadHandler, ThreadTask, ThreadGroup, SchedulingClass


@thread_function
def timeout_task(seconds, rtn):
    time.sleep(seconds)
    return rtn


@thread_function
def stopping_task(milliseconds):
    for _ in range(milliseconds):
        if is_stopped():
            return "stopped"
        time.sleep(0.001)
    return "completed"


@thread_function
def failing_task():
    raise ValueError("something went wrong")


@thread_function
def failing_task_stop_event():
    while True:
        if is_stopped():
            raise ValueError("something went wrong")


class TestThreadHandler(TestCase):
    def setUp(self):
        self.handler = ThreadHandler(SendUpdateThreadingAndAi(), max_threads=5)

    def test_simple_task_execution(self):
        results = []
        tasks = [
            ThreadTask(
                thread_function=timeout_task,
                scheduling_class=SchedulingClass.SYSTEM_CALL,
                group=ThreadGroup("OTHER"),
                semaphore=None,
                callback=lambda r: results.append(r),
                args=(0.1, "done"),
                kwargs={},
            )
            for _ in range(15)
        ]

        for task in tasks:
            self.handler.submit(task)

        time.sleep(0.15)
        self.assertCountEqual(results, ["done"] * 5)
        time.sleep(0.1)
        self.assertCountEqual(results, ["done"] * 10)
        time.sleep(0.2)
        self.assertCountEqual(results, ["done"] * 15)

    def test_multiple_callbacks(self):
        results = []

        for i in range(3):
            task = ThreadTask(
                timeout_task,
                SchedulingClass.SYSTEM_CALL,
                ThreadGroup("OTHER"),
                None,
                lambda r, idx=i: results.append((idx, r)),
                args=(0.1, f"done{i}"),
                kwargs={},
            )
            self.handler.submit(task)

        time.sleep(0.15)
        self.assertCountEqual([r[1] for r in results], ["done0", "done1", "done2"])

    def test_idle_detection(self):
        task = ThreadTask(
            timeout_task, SchedulingClass.SYSTEM_CALL, ThreadGroup("OTHER"), None, None, args=(0.1, "x"), kwargs={}
        )
        self.handler.submit(task)
        time.sleep(0.01)
        self.assertFalse(self.handler.is_idle())
        time.sleep(0.12)
        self.assertTrue(self.handler.is_idle())

    def test_priority_order(self):
        results = []

        low_task = ThreadTask(
            timeout_task,
            SchedulingClass.CALLER_DEPTH_2,
            ThreadGroup("OTHER"),
            None,
            lambda r: results.append(("low", r)),
            args=(0.1, "low"),
            kwargs={},
        )
        high_task = ThreadTask(
            timeout_task,
            SchedulingClass.CALLER_DEPTH_1,
            ThreadGroup("OTHER"),
            None,
            lambda r: results.append(("high", r)),
            args=(0.1, "high"),
            kwargs={},
        )

        self.handler.submit(low_task)
        self.handler.submit(high_task)

        time.sleep(0.02)
        self.assertTrue(("high", "high") in results or len(results) == 0)
        time.sleep(0.15)
        self.assertCountEqual([r[1] for r in results], ["high", "low"])

    def test_group_stop_with_other_groups(self):
        task1 = ThreadTask(
            stopping_task,
            SchedulingClass.CALLER_DEPTH_1,
            ThreadGroup("VARIABLE_HIGHLIGHTING"),
            None,
            None,
            args=(20,),
            kwargs={},
        )
        task2 = ThreadTask(
            stopping_task, SchedulingClass.CALLER_DEPTH_1, ThreadGroup("OTHER"), None, None, args=(20,), kwargs={}
        )

        for _ in range(10):
            res_var_highlight = self.handler.submit(task1)
            self.handler.submit(task2)

        time.sleep(0.01)
        self.handler.stop_group(ThreadGroup("OTHER"))
        time.sleep(0.01)
        result_1 = task2.status
        result_2 = res_var_highlight.result()
        self.assertEqual(result_1, "terminated thread")
        self.assertEqual(result_2, "completed")

    def test_task_exception_propagation(self):
        result = self.handler.submit(
            ThreadTask(failing_task, SchedulingClass.SYSTEM_CALL, ThreadGroup("OTHER"), None, None, (), {})
        )
        time.sleep(0.1)
        self.assertTrue(result.done())
        with self.assertRaises(ValueError):
            result.result()

    def test_task_result_timeout(self):
        result = self.handler.submit(
            ThreadTask(stopping_task, SchedulingClass.SYSTEM_CALL, ThreadGroup("OTHER"), None, None, (10000,), {})
        )
        with self.assertRaises(TimeoutError):
            result.result(timeout=0.1)

    def test_cancel_task_not_found(self):
        result = self.handler.cancel_task("nonexistent_id")
        self.assertFalse(result)

    def test_stop_group_catches_exception_from_result(self):
        self.handler.submit(
            ThreadTask(failing_task_stop_event, SchedulingClass.SYSTEM_CALL, ThreadGroup("AI"), None, None, (), {})
        )
        time.sleep(0.1)
        self.handler.stop_group(ThreadGroup("AI"))
        self.assertTrue(self.handler.is_idle())

    def test_group_stop(self):
        self.handler._max_threads = 1
        task1 = ThreadTask(
            stopping_task, SchedulingClass.CALLER_DEPTH_1, ThreadGroup("OTHER"), None, None, args=(500,), kwargs={}
        )
        task2 = ThreadTask(
            stopping_task, SchedulingClass.CALLER_DEPTH_1, ThreadGroup("OTHER"), None, None, args=(500,), kwargs={}
        )
        self.handler.submit(task1)
        self.handler.submit(task2)

        time.sleep(0.1)
        self.handler.stop_group(ThreadGroup("OTHER"))

        result1 = task1.status
        result2 = task2.status
        self.assertIn(result1, "terminated thread")
        self.assertIn(result2, "terminated in queue")

    def test_with_additional_semaphore(self):
        self.handler._max_threads = 15
        semaphore = Semaphore(6)
        for i in range(20):
            task = ThreadTask(
                timeout_task, SchedulingClass.SYSTEM_CALL, ThreadGroup("AI"), semaphore, None, (0.1, f"Test{i}"), {}
            )
            self.handler.submit(task)
        time.sleep(0.05)
        self.assertEqual(self.handler.get_active_count(), 6)
        time.sleep(0.1)
        self.assertEqual(self.handler.get_active_count(), 6)

    def test_id_task_stop(self):
        self.handler._max_threads = 2
        tasks = [
            self.handler.submit(
                ThreadTask(stopping_task, SchedulingClass.SYSTEM_CALL, ThreadGroup("OTHER"), None, None, (1000,), {})
            )
            for _ in range(5)
        ]
        time.sleep(0.1)
        for task in tasks:
            self.handler.cancel_task(task.task_id())
        time.sleep(0.1)
        self.assertTrue(self.handler.is_idle())


class TestThreadGroup(TestCase):
    def setUp(self):
        ThreadGroup._registry.clear()

    def test_thread_group_get_known(self):
        ThreadGroup("CLUSTERING")
        result = ThreadGroup.get("clustering")
        self.assertIsNotNone(result)
        self.assertEqual(result, ThreadGroup("CLUSTERING"))

    def test_thread_group_get_unknown(self):
        result = ThreadGroup.get("DOES_NOT_EXIST")
        self.assertIsNone(result)

    def test_thread_group_same_instance(self):
        g1 = ThreadGroup("AI")
        g2 = ThreadGroup("AI")
        self.assertIs(g1, g2)


class TestThreadingApi(TestCase):
    def setUp(self) -> None:
        self.mock_hanfor = MockHanfor(session_tags=["simple"], test_session_source="test_api_threading")
        self.mock_hanfor.set_up()

    def tearDown(self) -> None:
        self.mock_hanfor.tear_down()

    def test_api_get(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])
        self.assertListEqual(
            list(json.loads(self.mock_hanfor.app.get("api/v1/threading/").data).keys()),
            ["max_threads", "groups", "active_tasks", "queued_tasks"],
        )

    def test_stop_group(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])
        self.assertTrue(
            json.loads(self.mock_hanfor.app.post("api/v1/threading/stop-group/TEST_NOT_EXISTING").data)[
                "message"
            ].startswith("Unknown thread group: TEST_NOT_EXISTING.")
        )
        ThreadTask(lambda x: None, SchedulingClass.SYSTEM_CALL, ThreadGroup("TEST_EXISTING"), None, None, (), {})
        self.assertEqual(
            json.loads(self.mock_hanfor.app.post("api/v1/threading/stop-group/TEST_EXISTING").data),
            {"info": "stopped thread_group: TEST_EXISTING"},
        )

    def test_cancel_task(self):
        self.mock_hanfor.startup_hanfor("simple.csv", "simple", [])
        self.assertEqual(
            json.loads(self.mock_hanfor.app.delete("api/v1/threading/task/123456").data),
            {"info": "task: 123456 not found"},
        )
