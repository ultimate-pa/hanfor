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
    "ThreadCancelResponse", {"info": fields.String(example="cancelled task: abc-123"), "found": fields.Boolean()}
)

# --- API Routes ---


@threading_api_namespace.route("/")
class ApiThreadingData(Resource):
    @threading_api_namespace.marshal_with(THREAD_DATA, code=200)
    def get(self):
        return current_app.thread_handler.threading_data()


@threading_api_namespace.route("/stop-group/<string:thread_group>")
class ApiThreadingStopGroup(Resource):
    @threading_api_namespace.marshal_with(THREAD_STOP_RESPONSE, code=200)
    @threading_api_namespace.response(404, "Unknown thread group")
    def post(self, thread_group: str):
        try:
            group = ThreadGroup[thread_group]
        except KeyError:
            threading_api_namespace.abort(404, f"Unknown thread group: {thread_group}")

        current_app.thread_handler.stop_group(group)
        return {"info": f"stopped thread_group: {group}"}


@threading_api_namespace.route("/cancel-task/<string:task_id>")
class ApiThreadingCancelTask(Resource):
    @threading_api_namespace.marshal_with(THREAD_CANCEL_RESPONSE, code=200)
    def post(self, task_id: str):
        found = current_app.thread_handler.cancel_task(task_id)
        return {"info": f"cancel requested: {task_id}", "found": found}


# ---- TEMP DEBUG ---------
@threading_api_namespace.route("/dummy-task")
class ApiThreadingDummy(Resource):
    @threading_api_namespace.response(204, "Success")
    def post(self):
        from thread_handling.threading_core import ThreadTask, SchedulingClass
        import random

        sleep = int(random.uniform(2000, 10000000))
        seconds = sleep / 1000

        task = ThreadTask(
            thread_function=_dummy_task,
            scheduling_class=random.choice(list(SchedulingClass)),
            group=random.choice(list(ThreadGroup)),
            semaphore=None,
            callback=None,
            args=(sleep,),
            kwargs={},
            info_text=f"{seconds:.1f}s sleep",
        )
        current_app.thread_handler.submit(task)
        return None, 204


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
