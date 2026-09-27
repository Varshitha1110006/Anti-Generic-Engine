"""Backend tests for roles, quotas, judge access, and read-only judge."""
import os
import uuid
import requests
import pytest

BASE_URL = "http://localhost:8001"  # internal fast path; avoids Cloudflare UA gate
UA = {"User-Agent": "Mozilla/5.0 pytest-roles"}
CHEF_ID = "d24ff992-a447-4bf1-b833-11f3f4a27e0d"


def api(path):
    return f"{BASE_URL}{path}"


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json", **UA})
    return s


def _login(session, email, password):
    r = session.post(api("/api/auth/login"), json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()


@pytest.fixture(scope="module")
def owner(session):
    return _login(session, "demo@antigeneric.app", "Demo1234!")


@pytest.fixture(scope="module")
def judge(session):
    return _login(session, "judge@antigeneric.app", "Inkloom-Judge-2026")


@pytest.fixture(scope="module")
def registered(session):
    email = f"TEST_ru_{uuid.uuid4().hex[:8]}@example.com"
    r = session.post(api("/api/auth/register"), json={"name": "TEST Reg", "email": email, "password": "Passw0rd!"})
    assert r.status_code == 200, r.text
    return {"email": email, **r.json()}


def _h(token):
    return {"Authorization": f"Bearer {token}", **UA}


class TestOwnerRole:
    def test_owner_login_role_and_name(self, owner):
        assert owner["user"]["role"] == "owner"
        assert owner["user"]["name"] == "Studio Owner"

    def test_owner_usage_unlimited(self, session, owner):
        r = session.get(api("/api/usage"), headers=_h(owner["token"]))
        assert r.status_code == 200
        d = r.json()
        assert d["role"] == "owner"
        assert d["unlimited"] is True
        assert d["builds_limit"] is None and d["chats_limit"] is None
        assert d["can_edit"] is True


class TestJudgeRole:
    def test_judge_login_role_and_name(self, judge):
        assert judge["user"]["role"] == "judge"
        assert judge["user"]["name"] == "Inkloom Judge"

    def test_judge_usage_quota(self, session, judge):
        r = session.get(api("/api/usage"), headers=_h(judge["token"]))
        assert r.status_code == 200
        d = r.json()
        assert d["role"] == "judge"
        assert d["unlimited"] is False
        assert d["builds_limit"] == 3
        assert d["chats_limit"] == 15
        assert d["can_edit"] is False

    def test_judge_sees_owner_showcase(self, session, judge):
        r = session.get(api("/api/workflows"), headers=_h(judge["token"]))
        assert r.status_code == 200
        projects = r.json()
        chef = [p for p in projects if p["id"] == CHEF_ID]
        assert chef, f"Chef Notebook not in judge history: {[p['title'] for p in projects]}"
        assert chef[0]["shared"] is True
        assert chef[0]["title"]  # not empty

    def test_judge_can_view_owner_project(self, session, judge):
        r = session.get(api(f"/api/workflows/{CHEF_ID}"), headers=_h(judge["token"]))
        assert r.status_code == 200
        d = r.json()
        assert len(d["stages"]) == 6

    def test_judge_rename_forbidden(self, session, judge):
        r = session.patch(api(f"/api/workflows/{CHEF_ID}"), json={"title": "hacked"}, headers=_h(judge["token"]))
        assert r.status_code == 403
        assert "view-only" in r.json()["detail"].lower() or "judge" in r.json()["detail"].lower()

    def test_judge_delete_forbidden(self, session, judge):
        r = session.delete(api(f"/api/workflows/{CHEF_ID}"), headers=_h(judge["token"]))
        assert r.status_code == 403


class TestRegisteredUserQuota:
    def test_new_user_usage_limits(self, session, registered):
        r = session.get(api("/api/usage"), headers=_h(registered["token"]))
        assert r.status_code == 200
        d = r.json()
        assert d["role"] == "user"
        assert d["unlimited"] is False
        assert d["builds_limit"] == 1
        assert d["chats_limit"] == 5
        assert d["builds_used"] == 0 and d["chats_used"] == 0

    def test_isolation_registered_cannot_see_owner_project(self, session, registered):
        r = session.get(api("/api/workflows"), headers=_h(registered["token"]))
        assert r.status_code == 200
        ids = [p["id"] for p in r.json()]
        assert CHEF_ID not in ids

    def test_isolation_registered_get_owner_project_404(self, session, registered):
        r = session.get(api(f"/api/workflows/{CHEF_ID}"), headers=_h(registered["token"]))
        assert r.status_code == 404

    def test_build_then_second_build_429(self, session, registered):
        """Runs ONE real build (~60-150s) then verifies a second build is 429."""
        h = _h(registered["token"])
        payload = {"idea": "A pocket weather diary that only tracks how the sky felt.", "audience": "curious journalers", "constraints": "no location tracking"}
        r = session.post(api("/api/workflow"), json=payload, headers=h, timeout=240)
        assert r.status_code == 200, r.text
        doc = r.json()
        assert len(doc["stages"]) == 6
        pid = doc["id"]

        u = session.get(api("/api/usage"), headers=h).json()
        assert u["builds_used"] == 1

        # second build must 429
        r2 = session.post(api("/api/workflow"), json=payload, headers=h, timeout=30)
        assert r2.status_code == 429
        assert "daily allowance" in r2.json()["detail"].lower()

        # 5 chats ok, 6th 429
        for i in range(5):
            rc = session.post(api(f"/api/workflows/{pid}/chat"), json={"message": f"TEST_probe {i}: keep it short."}, headers=h, timeout=120)
            assert rc.status_code == 200, f"chat {i} failed: {rc.text}"
        u2 = session.get(api("/api/usage"), headers=h).json()
        assert u2["chats_used"] == 5

        r6 = session.post(api(f"/api/workflows/{pid}/chat"), json={"message": "TEST 6th chat should fail"}, headers=h, timeout=30)
        assert r6.status_code == 429
        assert "daily allowance" in r6.json()["detail"].lower()


class TestJudgeChat:
    def test_judge_can_chat_on_owner_project(self, session, judge):
        h = _h(judge["token"])
        before = session.get(api("/api/usage"), headers=h).json()
        r = session.post(api(f"/api/workflows/{CHEF_ID}/chat"), json={"message": "TEST_JUDGE_PROBE: name one brand trait in one sentence."}, headers=h, timeout=120)
        assert r.status_code == 200, r.text
        after = session.get(api("/api/usage"), headers=h).json()
        assert after["chats_used"] == before["chats_used"] + 1
