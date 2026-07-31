from unittest.mock import MagicMock, patch

import pytest

from openai_client import DraftGenerationError, generate_draft


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
