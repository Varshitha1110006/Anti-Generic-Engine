"""Regression coverage for analysis, six-stage workflow, and persistence APIs."""
import os
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL") or open("/app/frontend/.env").read().split("=", 1)[1].splitlines()[0]


def test_health_and_analysis():
    health = requests.get(f"{BASE_URL}/api/", timeout=30)
    assert health.status_code == 200
    analysis = requests.post(f"{BASE_URL}/api/analyze", json={"idea": "A focused tool for independent makers"}, timeout=30)
    assert analysis.status_code == 200
    body = analysis.json()
    assert isinstance(body["score"], int)
    assert body["signals"] and body["unlocks"]


def test_workflow_has_six_structured_stages_and_persists():
    payload = {
        "idea": "TEST_An opinionated tool map for makers",
        "audience": "TEST_Independent makers",
        "constraints": "TEST_One clear sentence",
    }
    created = requests.post(f"{BASE_URL}/api/workflow", json=payload, timeout=180)
    assert created.status_code == 200, created.text
    body = created.json()
    assert body["idea"] == payload["idea"]
    assert len(body["stages"]) == 6
    assert [stage["key"] for stage in body["stages"]] == ["understand", "personality", "challenge", "visualize", "test", "launch"]
    for stage in body["stages"]:
        assert stage["summary"]
        assert isinstance(stage["decisions"], list)
        assert isinstance(stage["tensions"], list)
        assert stage["next_question"]
    records = requests.get(f"{BASE_URL}/api/workflows", timeout=30)
    assert records.status_code == 200
    assert any(item["id"] == body["id"] for item in records.json())