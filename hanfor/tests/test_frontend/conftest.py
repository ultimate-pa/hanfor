"""
Test configuration for the test fixtures that do all the wiring so that
when a url is supplied, a hanfor server instance with the right context gets spun up
"""

import socket
import threading

import pytest
from werkzeug.serving import make_server

from app import app
from tests.mock_hanfor import MockHanfor


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def hanfor_server(request):
    mock_hanfor = MockHanfor(session_tags=["simple"], test_session_source="test_formalization_process")
    request.addfinalizer(mock_hanfor.tear_down)
    mock_hanfor.set_up()
    mock_hanfor.startup_hanfor("simple.csv", "simple", [])

    port = free_port()
    server = make_server("127.0.0.1", port, app, threaded=True)
    request.addfinalizer(server.shutdown)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{port}"


@pytest.fixture(scope="session")
def base_url(hanfor_server):
    return hanfor_server
