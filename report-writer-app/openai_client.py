import json
import os

from openai import OpenAI


class DraftGenerationError(Exception):
    pass


class FollowupGenerationError(Exception):
    pass


class StyleCheckGenerationError(Exception):
    pass


def generate_draft(system_prompt: str, user_prompt: str) -> str:
    if not os.environ.get("OPENAI_API_KEY"):
        raise DraftGenerationError("OPENAI_API_KEY is not set")

    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception as exc:
        raise DraftGenerationError(f"OpenAI request failed: {exc}") from exc

    return response.choices[0].message.content.strip()


def generate_followup(system_prompt: str, user_prompt: str) -> dict:
    if not os.environ.get("OPENAI_API_KEY"):
        raise FollowupGenerationError("OPENAI_API_KEY is not set")

    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
    except Exception as exc:
        raise FollowupGenerationError(f"OpenAI request failed: {exc}") from exc

    question = str(data.get("question", "")).strip()
    suggestions = [str(s).strip() for s in data.get("suggestions", []) if str(s).strip()]
    if not question:
        raise FollowupGenerationError("OpenAI response missing a follow-up question")

    return {"question": question, "suggestions": suggestions}


def generate_style_check(system_prompt: str, user_prompt: str) -> dict:
    if not os.environ.get("OPENAI_API_KEY"):
        raise StyleCheckGenerationError("OPENAI_API_KEY is not set")

    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
    except Exception as exc:
        raise StyleCheckGenerationError(f"OpenAI request failed: {exc}") from exc

    corrected_text = str(data.get("corrected_text", "")).strip()
    if not corrected_text:
        raise StyleCheckGenerationError("OpenAI response missing corrected text")

    raw_changes = data.get("changes", [])
    changes = []
    if isinstance(raw_changes, list):
        for item in raw_changes:
            if not isinstance(item, dict):
                continue
            changes.append(
                {
                    "original": str(item.get("original", "")).strip(),
                    "corrected": str(item.get("corrected", "")).strip(),
                    "reason": str(item.get("reason", "")).strip(),
                }
            )

    raw_suggestions = data.get("suggestions", [])
    suggestions = []
    if isinstance(raw_suggestions, list):
        suggestions = [str(s).strip() for s in raw_suggestions if str(s).strip()]

    return {"corrected_text": corrected_text, "changes": changes, "suggestions": suggestions}
