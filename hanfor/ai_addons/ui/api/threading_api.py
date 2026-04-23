from flask import Blueprint
from flask_restx import Resource, fields, Namespace

from hanfor_flask import current_app
from thread_handling.threading_core import ThreadGroup

threading_blueprint = Blueprint(
    "threading",
    __name__,
    url_prefix="/threading",
)

threading_api_namespace = Namespace("Threading", "Dashboard data threading", path="/threading", ordered=True)


TASK_MODEL = threading_api_namespace.model(
    "Task",
    {
        "function": fields.String(example="process_job"),
        "group": fields.String(example="workers"),
        "scheduling_class": fields.String(example="REALTIME"),
        "priority": fields.Integer(example=1),
        "status": fields.String(example=""),
    },
)

THREAD_DATA = threading_api_namespace.model(
    "ThreadData",
    {
        "max_threads": fields.Integer(example=8),
        "groups": fields.List(fields.String, example=["workers", "io"]),
        "active_tasks": fields.List(fields.Nested(TASK_MODEL)),
        "queued_tasks": fields.List(fields.Nested(TASK_MODEL)),
    },
)

THREAD_STOP_RESPONSE = threading_api_namespace.model(
    "Info", {"info": fields.String(example=f"stopping thread_group: AI")}
)


@threading_api_namespace.route("/")
class ApiThreadingData(Resource):
    @threading_api_namespace.response(200, "Success", THREAD_DATA)
    def get(self):
        return current_app.thread_handler.threading_data()


@threading_api_namespace.route("/stop_group/<string:thread_group>")
class ApiThreadingStopGroup(Resource):
    @threading_api_namespace.response(200, "Success", THREAD_STOP_RESPONSE)
    def post(self, thread_group: str):
        group = ThreadGroup[thread_group]
        current_app.thread_handler.stop_group(group)
        return {"info": f"stopped thread_group: {group}"}


# ---- temp---------
@threading_blueprint.route("/dummy_task", methods=["POST"])
def threading_dummy_task():
    from thread_handling.threading_core import ThreadTask, SchedulingClass
    import random

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


def _dummy_task(stop_event):
    import random
    import time

    for i in range(int(random.uniform(2000, 10000))):
        time.sleep(0.001)
        if stop_event.is_set():
            break
