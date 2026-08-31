from unittest.mock import MagicMock, patch

import pytest

from openai_client import (
    DraftGenerationError,
    FollowupGenerationError,
    StyleCheckGenerationError,
    generate_draft,
    generate_followup,
    generate_style_check,
)


def test_generate_draft_missing_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(DraftGenerationError, match="OPENAI_API_KEY"):
        generate_draft("system", "user")


@patch("openai_client.OpenAI")
def test_generate_draft_success(mock_openai_class, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unittest")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="  Draft text.  "))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    result = generate_draft("system prompt", "user prompt")

    assert result == "Draft text."
    mock_client.chat.completions.create.assert_called_once()


@patch("openai_client.OpenAI")
def test_generate_draft_api_failure(mock_openai_class, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unittest")
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = RuntimeError("network down")
    mock_openai_class.return_value = mock_client

    with pytest.raises(DraftGenerationError, match="OpenAI request failed"):
        generate_draft("system prompt", "user prompt")


@patch("openai_client.OpenAI")
def test_generate_draft_uses_model_env_var(mock_openai_class, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unittest")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="text"))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    generate_draft("system", "user")

    _, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-4o"


@patch("openai_client.OpenAI")
def test_generate_draft_defaults_to_mini_model(mock_openai_class, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unittest")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="text"))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    generate_draft("system", "user")

    _, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-4o-mini"


def test_generate_followup_missing_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(FollowupGenerationError, match="OPENAI_API_KEY"):
        generate_followup("system", "user")


@patch("openai_client.OpenAI")
def test_generate_followup_success(mock_openai_class, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unittest")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content='{"question": "What did they do well?", "suggestions": ["a", "b"]}'
            )
        )
    ]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    result = generate_followup("system prompt", "user prompt")

    assert result == {"question": "What did they do well?", "suggestions": ["a", "b"]}
    _, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["response_format"] == {"type": "json_object"}


@patch("openai_client.OpenAI")
def test_generate_followup_missing_question_raises(mock_openai_class, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unittest")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content='{"suggestions": []}'))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    with pytest.raises(FollowupGenerationError):
        generate_followup("system prompt", "user prompt")


@patch("openai_client.OpenAI")
def test_generate_followup_api_failure(mock_openai_class, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unittest")
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = RuntimeError("network down")
    mock_openai_class.return_value = mock_client

    with pytest.raises(FollowupGenerationError, match="OpenAI request failed"):
        generate_followup("system prompt", "user prompt")


def test_generate_style_check_missing_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(StyleCheckGenerationError, match="OPENAI_API_KEY"):
        generate_style_check("system", "user")


@patch("openai_client.OpenAI")
def test_generate_style_check_success(mock_openai_class, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unittest")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=(
                    '{"corrected_text": "Corrected report.", '
                    '"changes": [{"original": "Y10", "corrected": "Year 10", '
                    '"reason": "house style"}]}'
                )
            )
        )
    ]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    result = generate_style_check("system prompt", "user prompt")

    assert result["corrected_text"] == "Corrected report."
    assert result["changes"] == [
        {"original": "Y10", "corrected": "Year 10", "reason": "house style"}
    ]
    _, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["response_format"] == {"type": "json_object"}


@patch("openai_client.OpenAI")
def test_generate_style_check_no_issues_found(mock_openai_class, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unittest")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(content='{"corrected_text": "Already fine.", "changes": []}')
        )
    ]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    result = generate_style_check("system prompt", "user prompt")

    assert result == {"corrected_text": "Already fine.", "changes": [], "suggestions": []}


@patch("openai_client.OpenAI")
def test_generate_style_check_missing_corrected_text_raises(mock_openai_class, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unittest")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content='{"changes": []}'))]
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    with pytest.raises(StyleCheckGenerationError):
        generate_style_check("system prompt", "user prompt")


@patch("openai_client.OpenAI")
def test_generate_style_check_api_failure(mock_openai_class, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "unittest")
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = RuntimeError("network down")
    mock_openai_class.return_value = mock_client

    with pytest.raises(StyleCheckGenerationError, match="OpenAI request failed"):
        generate_style_check("system prompt", "user prompt")
