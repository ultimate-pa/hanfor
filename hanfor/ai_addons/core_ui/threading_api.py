from http import HTTPStatus

from flask_restx import Resource, fields, Namespace

from hanfor_flask import current_app
from thread_handling.thread_function_decorator import thread_function, is_stopped, set_status
from thread_handling.threading_core import ThreadGroup

threading_api_namespace = Namespace("Threading", "Dashboard data threading", path="/threading", ordered=True)

# --- Models ---

TASK_MODEL = threading_api_namespace.model(
    "Task",
    {
        "function": fields.String(example="process_job"),
        "group": fields.String(example="workers"),
        "scheduling_class": fields.String(example="REALTIME"),
        "status": fields.String(example=""),
        "task_id": fields.String(example="abc-123"),
        "queued_at": fields.Float(example=1234567890.123),
        "started_at": fields.Float(example=1234567890.123),
        "info_text": fields.String(example="something usefully"),
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
    "ThreadStopResponse", {"info": fields.String(example="stopped thread_group: AI")}
)

THREAD_CANCEL_RESPONSE = threading_api_namespace.model(
    "ThreadCancelResponse", {"info": fields.String(example="cancelled task: abc-123")}
)

# --- API Routes ---


@threading_api_namespace.route("/")
class ApiThreadingData(Resource):
    @threading_api_namespace.marshal_with(THREAD_DATA, code=HTTPStatus.OK)
    def get(self):
        return current_app.thread_handler.threading_data()


@threading_api_namespace.route("/stop-group/<string:thread_group>")
class ApiThreadingStopGroup(Resource):
    @threading_api_namespace.marshal_with(THREAD_STOP_RESPONSE, code=HTTPStatus.OK)
    @threading_api_namespace.response(HTTPStatus.NOT_FOUND, "Unknown thread group")
    def post(self, thread_group: str):
        group = ThreadGroup.get(thread_group)
        if group is None:
            threading_api_namespace.abort(HTTPStatus.NOT_FOUND, f"Unknown thread group: {thread_group}")
        current_app.thread_handler.stop_group(group)
        return {"info": f"stopped thread_group: {group}"}


@threading_api_namespace.route("/task/<string:task_id>")
class ApiThreadingCancelTask(Resource):
    @threading_api_namespace.marshal_with(THREAD_CANCEL_RESPONSE, code=HTTPStatus.OK)
    @threading_api_namespace.marshal_with(THREAD_CANCEL_RESPONSE, code=HTTPStatus.NOT_FOUND)
    def delete(self, task_id: str):
        found = current_app.thread_handler.cancel_task(task_id)
        if found:
            return {"info": f"cancel requested: {task_id}"}, HTTPStatus.OK
        return {"info": f"task: {task_id} not found"}, HTTPStatus.NOT_FOUND


# ---- TEMP DEBUG ---------
@threading_api_namespace.route("/dummy-task")
class ApiThreadingDummy(Resource):
    @threading_api_namespace.response(HTTPStatus.NO_CONTENT, "Success")
    def post(self):
        from thread_handling.threading_core import ThreadTask, SchedulingClass
        import random

        sleep = int(random.uniform(HTTPStatus.OK, 10000))
        seconds = sleep / 1000

        task = ThreadTask(
            thread_function=_dummy_task,
            scheduling_class=random.choice(list(SchedulingClass)),
            group=ThreadGroup(random.choice(["AI", "CLUSTERING", "OTHER"])),
            semaphore=None,
            callback=None,
            args=(sleep,),
            kwargs={},
            info_text=f"{seconds:.1f}s sleep",
        )
        current_app.thread_handler.submit(task)
        return None, HTTPStatus.NO_CONTENT


@thread_function
def _dummy_task(sleep):
    import time

    c = 0
    for i in range(sleep):
        if c % 100 == 0:
            set_status(f"{c/100}s")
        time.sleep(0.01)
        c += 1
        if is_stopped():
            break
