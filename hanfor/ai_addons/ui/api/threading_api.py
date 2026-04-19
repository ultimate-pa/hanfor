import random
import time
from flask import Blueprint, request
from hanfor_flask import current_app
from thread_handling.threading_core import ThreadGroup, ThreadTask, SchedulingClass

threading_blueprint = Blueprint(
    "threading",
    __name__,
    url_prefix="/threading",
)


def _dummy_task(stop_event):
    for i in range(int(random.uniform(2000, 10000))):
        time.sleep(0.001)
        if stop_event.is_set():
            break


@threading_blueprint.route("/initial", methods=["GET"])
def threading_data_initial():
    return current_app.thread_handler.threading_data()


@threading_blueprint.route("/stop_group", methods=["POST"])
def threading_stop_group():
    group = ThreadGroup[request.json.get("group")]
    current_app.thread_handler.stop_group(group)
    return current_app.thread_handler.threading_data()


@threading_blueprint.route("/dummy_task", methods=["POST"])
def threading_dummy_task():
    task = ThreadTask(
        thread_function=_dummy_task,
        scheduling_class=random.choice(list(SchedulingClass)),
        group=random.choice(list(ThreadGroup)),
        semaphore=None,
        callback=None,
        args=(),
        kwargs={},
    )
    current_app.thread_handler.submit(task)
    return "", 200
