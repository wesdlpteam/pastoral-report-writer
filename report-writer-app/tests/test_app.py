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


def test_generate_missing_formal_name(client):
    response = client.post(
        "/api/generate",
        json={"report_type": "tutor", "answers": {"person": "shows resilience and works well with peers"}},
    )
    assert response.status_code == 400
    assert "formal name is required" in response.get_json()["error"]


def test_generate_formal_name_with_bad_word(client):
    response = client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "formal_name": "shit Test",
            "answers": {"person": "shows resilience and works well with peers"},
        },
    )
    assert response.status_code == 400
    assert "formal name" in response.get_json()["error"]


def test_generate_missing_required_answers(client):
    response = client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "formal_name": "Jane Test",
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
            "formal_name": "Jane Test",
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
def test_generate_uses_real_name_in_prompt(mock_generate_draft, client):
    mock_generate_draft.return_value = " ".join(["word"] * 120)

    client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "formal_name": "Jane Test",
            "preferred_name": "Janie",
            "answers": {"person": "shows resilience and works well with peers"},
        },
    )

    _, user_prompt = mock_generate_draft.call_args[0]
    assert "Formal name: Jane Test" in user_prompt
    assert "Preferred name: Janie" in user_prompt


@patch("app.generate_draft")
def test_generate_passes_year_level_to_myp_note(mock_generate_draft, client):
    mock_generate_draft.return_value = " ".join(["word"] * 120)

    client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "formal_name": "Jane Test",
            "year_level": "8",
            "answers": {"person": "shows resilience and works well with peers"},
        },
    )

    system_prompt, _ = mock_generate_draft.call_args[0]
    assert "Learner Profile" in system_prompt


@patch("app.generate_draft")
def test_generate_caps_pronoun_length(mock_generate_draft, client):
    mock_generate_draft.return_value = " ".join(["word"] * 120)
    long_pronoun = "x" * 200

    client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "formal_name": "Jane Test",
            "pronouns": long_pronoun,
            "answers": {"person": "shows resilience and works well with peers"},
        },
    )

    system_prompt, user_prompt = mock_generate_draft.call_args[0]
    assert long_pronoun not in system_prompt
    assert long_pronoun not in user_prompt
    assert "x" * 30 in user_prompt


@patch("app.generate_draft")
def test_generate_openai_failure_returns_502(mock_generate_draft, client):
    from openai_client import DraftGenerationError

    mock_generate_draft.side_effect = DraftGenerationError("boom")

    response = client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "formal_name": "Jane Test",
            "answers": {
                "person": "shows resilience and works well with peers",
                "learner": "steadily improving across all subjects this term",
                "participant": "engaged and enthusiastic in class activities",
            },
        },
    )

    assert response.status_code == 502
    error = response.get_json()["error"]
    assert "boom" not in error
    assert "went wrong" in error


def test_generate_answer_too_short(client):
    response = client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "formal_name": "Jane Test",
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
            "formal_name": "Jane Test",
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
            "formal_name": "Jane Test",
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
            "formal_name": "Jane Test",
            "answers": {
                "person": "this student is a total shit in class",
                "learner": "",
                "participant": "",
            },
        },
    )
    assert response.status_code == 400
    assert "inappropriate language" in response.get_json()["error"]


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
    error = response.get_json()["error"]
    assert "boom" not in error
    assert "went wrong" in error


def test_style_check_missing_text(client):
    response = client.post("/api/style_check", json={})
    assert response.status_code == 400
    assert "paste the report text" in response.get_json()["error"]


def test_style_check_too_short(client):
    response = client.post("/api/style_check", json={"text": "Too short."})
    assert response.status_code == 400
    assert "at least" in response.get_json()["error"]


def test_style_check_too_long(client):
    response = client.post("/api/style_check", json={"text": "word " * 401})
    assert response.status_code == 400
    assert "no more than" in response.get_json()["error"]


def test_style_check_bad_word(client):
    text = "This is a shit report about the student's term and their overall progress this year."
    response = client.post("/api/style_check", json={"text": text})
    assert response.status_code == 400
    assert "inappropriate language" in response.get_json()["error"]


@patch("app.generate_style_check")
def test_style_check_success(mock_generate_style_check, client):
    mock_generate_style_check.return_value = {
        "corrected_text": "The corrected report text goes here for the student.",
        "changes": [{"original": "Y10", "corrected": "Year 10", "reason": "house style"}],
    }
    text = "The report text goes here about the student in Y10 for this term, overall, and beyond."

    response = client.post("/api/style_check", json={"text": text})

    assert response.status_code == 200
    body = response.get_json()
    assert body["corrected_text"] == "The corrected report text goes here for the student."
    assert body["changes"] == [{"original": "Y10", "corrected": "Year 10", "reason": "house style"}]
    assert body["original_text"] == text


@patch("app.generate_style_check")
def test_style_check_openai_failure_returns_502(mock_generate_style_check, client):
    from openai_client import StyleCheckGenerationError

    mock_generate_style_check.side_effect = StyleCheckGenerationError("boom")
    text = "The report text goes here about the student in Y10 for this term, overall, and beyond."

    response = client.post("/api/style_check", json={"text": text})

    assert response.status_code == 502
    error = response.get_json()["error"]
    assert "boom" not in error
    assert "went wrong" in error
