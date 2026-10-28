"""Password gate checks. Run from contexta_demo_backend/:  python -m pytest test_auth.py

/api/doctors is the probe route: a plain GET over static data, so these tests
need no API keys and make no network calls.
"""
import time

import pytest
from fastapi.testclient import TestClient

import auth
from main import app

client = TestClient(app)
PASSWORD = "correct horse battery"


@pytest.fixture(autouse=True)
def fresh_gate(monkeypatch):
    monkeypatch.setenv("DEMO_PASSWORD", PASSWORD)
    auth._fails.clear()


def login(password):
    return client.post("/api/login", json={"password": password})


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def test_api_rejects_requests_without_a_pass():
    assert client.get("/api/doctors").status_code == 401


def test_every_route_except_the_open_ones_is_locked():
    from fastapi.routing import APIRoute
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path not in auth.OPEN_PATHS:
            for method in route.methods:
                res = client.request(method, route.path)
                assert res.status_code == 401, f"{method} {route.path} -> {res.status_code}"


def test_browser_can_read_the_401_cross_origin():
    # The frontend is on a different Vercel domain. If the 401 lacks CORS headers
    # the browser reports a network error and the app can't fall back to the
    # password screen -- this breaks if the check moves into an outer middleware.
    origin = {"Origin": "https://frontend.example"}
    preflight = client.options("/api/chat", headers={
        **origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,content-type",
    })
    assert preflight.status_code == 200
    assert "authorization" in preflight.headers["access-control-allow-headers"].lower()
    denied = client.post("/api/chat", headers=origin, json={})
    assert denied.status_code == 401
    assert denied.headers.get("access-control-allow-origin")


def test_health_stays_open():
    assert client.get("/health").status_code == 200


def test_right_password_returns_a_pass_that_unlocks_the_api():
    res = login(PASSWORD)
    assert res.status_code == 200
    assert client.get("/api/doctors", headers=bearer(res.json()["token"])).status_code == 200


def test_tampered_pass_is_rejected():
    token = login(PASSWORD).json()["token"]
    exp, sig = token.split(".")
    forged = f"{int(exp) + 999999}.{sig}"  # push the expiry out, keep the old signature
    assert client.get("/api/doctors", headers=bearer(forged)).status_code == 401


def test_expired_pass_is_rejected():
    stale = auth.issue_pass(now=time.time() - auth.PASS_TTL - 1)
    assert client.get("/api/doctors", headers=bearer(stale)).status_code == 401


def test_changing_the_password_invalidates_existing_passes(monkeypatch):
    token = login(PASSWORD).json()["token"]
    monkeypatch.setenv("DEMO_PASSWORD", "a brand new phrase")
    assert client.get("/api/doctors", headers=bearer(token)).status_code == 401


def test_third_wrong_try_locks_out_even_the_right_password():
    assert [login("nope").status_code for _ in range(3)] == [401, 401, 401]
    locked = login(PASSWORD)
    assert locked.status_code == 429
    assert 0 < locked.json()["detail"]["retry_after"] <= auth.LOCKOUT


def test_success_before_the_third_try_resets_the_count():
    login("nope")
    login("nope")
    assert login(PASSWORD).status_code == 200
    assert [login("nope").status_code for _ in range(2)] == [401, 401]


def test_lockout_expires(monkeypatch):
    for _ in range(3):
        login("nope")
    real_time = time.time
    monkeypatch.setattr(auth.time, "time", lambda: real_time() + auth.LOCKOUT + 1)
    assert login(PASSWORD).status_code == 200


def test_unset_password_fails_closed(monkeypatch):
    monkeypatch.delenv("DEMO_PASSWORD")
    assert login("").status_code == 401
    assert client.get("/api/doctors", headers=bearer(auth.issue_pass())).status_code == 401
