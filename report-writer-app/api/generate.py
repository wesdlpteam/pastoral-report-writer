import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai_client import DraftGenerationError, generate_draft
from prompts import build_system_prompt, build_user_prompt
from word_count import count_words, get_range, is_in_range


REQUIRED_KEYS = {
    "tutor": ["person", "learner", "participant"],
    "pyp": ["learner_social", "atl", "achievement", "next_steps"],
}


def handler(request):
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        }

    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method not allowed"}),
        }

    try:
        data = json.loads(request.body) if isinstance(request.body, str) else request.body
    except (json.JSONDecodeError, TypeError):
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Invalid JSON"}),
        }

    report_type = data.get("report_type")
    answers = data.get("answers")
    pronouns = data.get("pronouns", "they/them")
    tutor_group = data.get("tutor_group")
    house = data.get("house")

    if report_type not in REQUIRED_KEYS:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "report_type must be 'tutor' or 'pyp'"}),
        }

    if not isinstance(answers, dict):
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "answers must be an object"}),
        }

    missing = [
        key
        for key in REQUIRED_KEYS[report_type]
        if not str(answers.get(key, "")).strip()
    ]
    if missing:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": f"missing required answers: {', '.join(missing)}"}),
        }

    system_prompt = build_system_prompt(report_type, pronouns)
    user_prompt = build_user_prompt(report_type, answers, pronouns, tutor_group, house)

    try:
        draft = generate_draft(system_prompt, user_prompt)
    except DraftGenerationError as exc:
        return {
            "statusCode": 502,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(exc)}),
        }

    word_count = count_words(draft)
    low, high = get_range(report_type)

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },
        "body": json.dumps(
            {
                "draft": draft,
                "word_count": word_count,
                "in_range": is_in_range(word_count, report_type),
                "target_range": [low, high],
            }
        ),
    }
