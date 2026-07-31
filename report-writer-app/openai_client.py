import os

from openai import OpenAI


class DraftGenerationError(Exception):
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
