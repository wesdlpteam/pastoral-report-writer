from unittest.mock import patch

import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_index_serves_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<html" in response.data.lower()


def test_generate_missing_report_type(client):
    response = client.post("/api/generate", json={"answers": {}})
    assert response.status_code == 400


def test_generate_invalid_report_type(client):
    response = client.post("/api/generate", json={"report_type": "bogus", "answers": {}})
    assert response.status_code == 400


def test_generate_missing_required_answers(client):
    response = client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "answers": {"person": "", "learner": "", "participant": ""},
        },
    )
    assert response.status_code == 400
    body = response.get_json()
    assert "missing required answers" in body["error"]


@patch("app.generate_draft")
def test_generate_success_tutor(mock_generate_draft, client):
    mock_generate_draft.return_value = " ".join(["word"] * 120)

    response = client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "answers": {
                "person": "resilient",
                "learner": "improving",
                "participant": "engaged",
                "summary": "",
            },
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["word_count"] == 120
    assert body["in_range"] is True
    assert body["target_range"] == [100, 150]


@patch("app.generate_draft")
def test_generate_openai_failure_returns_502(mock_generate_draft, client):
    from openai_client import DraftGenerationError

    mock_generate_draft.side_effect = DraftGenerationError("boom")

    response = client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "answers": {"person": "x", "learner": "y", "participant": "z"},
        },
    )

    assert response.status_code == 502


@patch("app.generate_draft")
def test_generate_success_pyp(mock_generate_draft, client):
    mock_generate_draft.return_value = " ".join(["word"] * 200)

    response = client.post(
        "/api/generate",
        json={
            "report_type": "pyp",
            "answers": {
                "learner_social": "curious",
                "atl": "strong thinking skills",
                "achievement": "camp",
                "next_steps": "keep reading widely",
            },
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["target_range"] == [180, 300]
