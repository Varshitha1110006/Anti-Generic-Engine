"""Backend tests for JWT auth, project isolation, chat memory, and analyze."""
import os
import uuid
import time
import requests
import pytest

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # fallback to internal for reliability
    BASE_URL = "http://localhost:8001"

UA = {"User-Agent": "Mozilla/5.0 pytest-backend"}


def api(path):
    return f"{BASE_URL}{path}"


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json", **UA})
    return s


@pytest.fixture(scope="module")
def demo_token(session):
    r = session.post(api("/api/auth/login"), json={"email": "demo@antigeneric.app", "password": "Demo1234!"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert "token" in data and data["user"]["email"] == "demo@antigeneric.app"
    assert data["user"]["name"] == "Studio Owner"
    return data["token"]


@pytest.fixture(scope="module")
def user_a(session):
    email = f"test_a_{uuid.uuid4().hex[:8]}@example.com"
    r = session.post(api("/api/auth/register"), json={"name": "TEST User A", "email": email, "password": "Passw0rd!"})
    assert r.status_code == 200, r.text
    d = r.json()
    return {"email": email, "token": d["token"], "user": d["user"]}


@pytest.fixture(scope="module")
def user_b(session):
    email = f"test_b_{uuid.uuid4().hex[:8]}@example.com"
    r = session.post(api("/api/auth/register"), json={"name": "TEST User B", "email": email, "password": "Passw0rd!"})
    assert r.status_code == 200, r.text
    d = r.json()
    return {"email": email, "token": d["token"], "user": d["user"]}


# ---------- Auth ----------
class TestAuth:
    def test_register_duplicate_returns_409(self, session, user_a):
        r = session.post(api("/api/auth/register"), json={"name": "dup", "email": user_a["email"], "password": "Passw0rd!"})
        assert r.status_code == 409
        assert "already exists" in r.json().get("detail", "").lower()

    def test_register_short_password_422_array_detail(self, session):
        r = session.post(api("/api/auth/register"), json={"name": "x", "email": f"short_{uuid.uuid4().hex[:6]}@e.com", "password": "12"})
        assert r.status_code == 422
        detail = r.json().get("detail")
        assert isinstance(detail, list) and len(detail) > 0

    def test_login_wrong_password_401(self, session, user_a):
        r = session.post(api("/api/auth/login"), json={"email": user_a["email"], "password": "WrongPass!"})
        assert r.status_code == 401
        assert isinstance(r.json().get("detail"), str)

    def test_me_requires_token(self, session):
        r = requests.get(api("/api/auth/me"), headers=UA)
        assert r.status_code == 401

    def test_me_with_token(self, session, demo_token):
        r = requests.get(api("/api/auth/me"), headers={"Authorization": f"Bearer {demo_token}", **UA})
        assert r.status_code == 200
        assert r.json()["email"] == "demo@antigeneric.app"

    def test_lockout_after_5_failures(self, session):
        # register fresh user
        email = f"lock_{uuid.uuid4().hex[:8]}@example.com"
        session.post(api("/api/auth/register"), json={"name": "Lock", "email": email, "password": "Passw0rd!"})
        codes = []
        for _ in range(6):
            r = session.post(api("/api/auth/login"), json={"email": email, "password": "wrong!!"})
            codes.append(r.status_code)
        assert 429 in codes, f"expected 429 lockout in {codes}"


# ---------- Analyze (public) ----------
class TestAnalyze:
    def test_analyze_no_token(self, session):
        r = session.post(api("/api/analyze"), json={"idea": "an ai platform for community empowerment"})
        assert r.status_code == 200
        d = r.json()
        assert "score" in d and "signals" in d and len(d["signals"]) == 3
        assert isinstance(d["score"], int)


# ---------- Projects isolation ----------
class TestProjectsIsolation:
    def test_protected_without_token(self, session):
        assert session.get(api("/api/workflows")).status_code == 401

    def test_list_isolated_per_user(self, session, user_a, user_b):
        ra = session.get(api("/api/workflows"), headers={"Authorization": f"Bearer {user_a['token']}"})
        rb = session.get(api("/api/workflows"), headers={"Authorization": f"Bearer {user_b['token']}"})
        assert ra.status_code == 200 and rb.status_code == 200
        assert ra.json() == [] and rb.json() == []

    def test_cross_user_project_returns_404(self, session, demo_token, user_a):
        # find one of demo user's projects
        r = session.get(api("/api/workflows"), headers={"Authorization": f"Bearer {demo_token}"})
        assert r.status_code == 200
        projects = r.json()
        if not projects:
            pytest.skip("No demo projects to test isolation")
        pid = projects[0]["id"]
        # user A should not see it
        r2 = session.get(api(f"/api/workflows/{pid}"), headers={"Authorization": f"Bearer {user_a['token']}"})
        assert r2.status_code == 404

    def test_rename_and_delete_project_flow(self, session, user_a):
        # Since real workflow build is slow, we test rename/delete on an inserted-through-chat only if there is one.
        # Instead, test that patch/delete on unknown id returns 404.
        h = {"Authorization": f"Bearer {user_a['token']}"}
        assert session.patch(api(f"/api/workflows/{uuid.uuid4()}"), json={"title": "x"}, headers=h).status_code == 404
        assert session.delete(api(f"/api/workflows/{uuid.uuid4()}"), headers=h).status_code == 404


# ---------- Chat (only if demo has a project) ----------
class TestChatMemory:
    def test_chat_on_demo_project(self, session, demo_token):
        h = {"Authorization": f"Bearer {demo_token}"}
        r = session.get(api("/api/workflows"), headers=h)
        assert r.status_code == 200
        projects = r.json()
        if not projects:
            pytest.skip("No demo project for chat test")
        pid = projects[0]["id"]
        before = session.get(api(f"/api/workflows/{pid}"), headers=h).json()
        before_count = len(before.get("messages", []))
        r2 = session.post(api(f"/api/workflows/{pid}/chat"), json={"message": "TEST_MEMORY_PROBE: name three brand traits you chose."}, headers=h, timeout=90)
        assert r2.status_code == 200, r2.text
        doc = r2.json()
        assert len(doc["messages"]) == before_count + 2
        assert doc["messages"][-2]["role"] == "user"
        assert doc["messages"][-1]["role"] == "assistant"
        assert len(doc["messages"][-1]["content"]) > 0
