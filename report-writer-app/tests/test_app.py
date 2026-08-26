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
                "person": "shows resilience and works well with peers",
                "learner": "steadily improving across all subjects this term",
                "participant": "engaged and enthusiastic in class activities",
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
def test_generate_passes_year_level_to_myp_note(mock_generate_draft, client):
    mock_generate_draft.return_value = " ".join(["word"] * 120)

    client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "year_level": "8",
            "answers": {"person": "shows resilience and works well with peers"},
        },
    )

    system_prompt, _ = mock_generate_draft.call_args[0]
    assert "Learner Profile" in system_prompt


@patch("app.generate_draft")
def test_generate_openai_failure_returns_502(mock_generate_draft, client):
    from openai_client import DraftGenerationError

    mock_generate_draft.side_effect = DraftGenerationError("boom")

    response = client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "answers": {
                "person": "shows resilience and works well with peers",
                "learner": "steadily improving across all subjects this term",
                "participant": "engaged and enthusiastic in class activities",
            },
        },
    )

    assert response.status_code == 502


def test_generate_answer_too_short(client):
    response = client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "answers": {"person": "too short", "learner": "", "participant": ""},
        },
    )
    assert response.status_code == 400
    assert "at least" in response.get_json()["error"]


def test_generate_answer_with_gibberish(client):
    response = client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "answers": {
                "person": "asdfgh asdfgh asdfgh asdfgh asdfgh",
                "learner": "",
                "participant": "",
            },
        },
    )
    assert response.status_code == 400
    assert "doesn't look like real text" in response.get_json()["error"]


def test_generate_answer_with_repeated_word_spam(client):
    response = client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "answers": {"person": "poo poo poo poo poo", "learner": "", "participant": ""},
        },
    )
    assert response.status_code == 400
    assert "repeated filler text" in response.get_json()["error"]


def test_generate_answer_with_bad_word(client):
    response = client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "answers": {
                "person": "this student is a total shit in class",
                "learner": "",
                "participant": "",
            },
        },
    )
    assert response.status_code == 400
    assert "inappropriate language" in response.get_json()["error"]


@patch("app.generate_draft")
def test_generate_redacts_possible_name_before_sending(mock_generate_draft, client):
    mock_generate_draft.return_value = " ".join(["word"] * 120)

    response = client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "answers": {
                "person": "Jordan is kind and resilient with peers",
                "learner": "",
                "participant": "",
            },
        },
    )

    assert response.status_code == 200
    _, user_prompt = mock_generate_draft.call_args[0]
    assert "Jordan" not in user_prompt
    assert "[student name]" in user_prompt


@patch("app.generate_followup")
def test_followup_redacts_possible_name_before_sending(mock_generate_followup, client):
    mock_generate_followup.return_value = {"question": "q", "suggestions": []}

    response = client.post(
        "/api/followup",
        json={
            "report_type": "tutor",
            "question_id": "person",
            "answer": "Jordan is kind and resilient",
        },
    )

    assert response.status_code == 200
    _, user_prompt = mock_generate_followup.call_args[0]
    assert "Jordan" not in user_prompt
    assert "[student name]" in user_prompt


def test_followup_missing_report_type(client):
    response = client.post("/api/followup", json={"question_id": "person", "answer": "kind"})
    assert response.status_code == 400


def test_followup_unknown_question_id(client):
    response = client.post(
        "/api/followup",
        json={"report_type": "tutor", "question_id": "bogus", "answer": "kind"},
    )
    assert response.status_code == 400


def test_followup_missing_answer(client):
    response = client.post(
        "/api/followup",
        json={"report_type": "tutor", "question_id": "person", "answer": ""},
    )
    assert response.status_code == 400


@patch("app.generate_followup")
def test_followup_success(mock_generate_followup, client):
    mock_generate_followup.return_value = {
        "question": "What did they do well?",
        "suggestions": ["a specific example", "how they reacted"],
    }

    response = client.post(
        "/api/followup",
        json={"report_type": "tutor", "question_id": "person", "answer": "kind and quiet"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["question"] == "What did they do well?"
    assert body["suggestions"] == ["a specific example", "how they reacted"]


@patch("app.generate_followup")
def test_followup_passes_pronouns_to_prompt(mock_generate_followup, client):
    mock_generate_followup.return_value = {"question": "q", "suggestions": []}

    client.post(
        "/api/followup",
        json={
            "report_type": "tutor",
            "question_id": "person",
            "answer": "kind and quiet",
            "pronouns": "she/her",
        },
    )

    _, user_prompt = mock_generate_followup.call_args[0]
    assert "she/her" in user_prompt


@patch("app.generate_followup")
def test_followup_openai_failure_returns_502(mock_generate_followup, client):
    from openai_client import FollowupGenerationError

    mock_generate_followup.side_effect = FollowupGenerationError("boom")

    response = client.post(
        "/api/followup",
        json={"report_type": "tutor", "question_id": "person", "answer": "kind and quiet"},
    )

    assert response.status_code == 502
