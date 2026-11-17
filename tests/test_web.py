import pytest

pytest.importorskip("fastapi")
pytest.importorskip("jinja2")

from fastapi.testclient import TestClient

from rps.web.app import SESSIONS, app


@pytest.fixture(autouse=True)
def clean_sessions():
    SESSIONS.clear()
    yield
    SESSIONS.clear()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_index_serves_page(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Rock, Paper, Scissors" in r.text
    assert "rock" in r.text


def test_play_redirects_and_updates_state(client):
    client.get("/")
    r = client.post("/play", data={"move": "rock"}, follow_redirects=False)
    assert r.status_code == 303
    page = client.get("/")
    assert "You played" in page.text


def test_invalid_move_ignored(client):
    client.get("/")
    client.post("/play", data={"move": "banana"}, follow_redirects=True)
    assert "You played" not in client.get("/").text


def test_reset_clears_state(client):
    client.get("/")
    client.post("/play", data={"move": "rock"})
    r = client.post("/reset", follow_redirects=True)
    assert r.status_code == 200
    assert "You played" not in r.text


def test_settings_change_rules(client):
    client.get("/")
    r = client.post(
        "/settings",
        data={"rules": "startrek", "bot": "random"},
        follow_redirects=True,
    )
    assert r.status_code == 200
    assert "startrek" in r.text


def test_settings_invalid_ignored(client):
    client.get("/")
    client.post(
        "/settings",
        data={"rules": "nope", "bot": "random"},
        follow_redirects=True,
    )
    assert "classic" in client.get("/").text


def test_sessions_are_independent(client):
    other = TestClient(app)
    client.get("/")
    other.get("/")
    client.post("/play", data={"move": "rock"})
    assert "You played" in client.get("/").text
    assert "You played" not in other.get("/").text