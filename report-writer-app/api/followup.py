import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request

from openai_client import FollowupGenerationError, generate_followup
from prompts import ANSWER_LABELS, FOLLOWUP_SYSTEM_PROMPT, build_followup_user_prompt

logger = logging.getLogger(__name__)

MAX_PRONOUN_LENGTH = 30

app = Flask(__name__)

ALLOWED_ORIGIN = "https://wesdlpteam.github.io"


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/api/followup", methods=["POST", "OPTIONS"])
def followup():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(silent=True) or {}

    report_type = data.get("report_type")
    question_id = data.get("question_id")
    answer = str(data.get("answer", "")).strip()
    pronouns = str(data.get("pronouns", "they/them"))[:MAX_PRONOUN_LENGTH]

    if report_type not in ANSWER_LABELS:
        return jsonify({"error": "report_type must be 'tutor'"}), 400
    if question_id not in ANSWER_LABELS[report_type]:
        return jsonify({"error": "unknown question_id for this report_type"}), 400
    if not answer:
        return jsonify({"error": "answer is required"}), 400

    question_label = ANSWER_LABELS[report_type][question_id]
    user_prompt = build_followup_user_prompt(question_label, answer, pronouns)

    try:
        result = generate_followup(FOLLOWUP_SYSTEM_PROMPT, user_prompt)
    except FollowupGenerationError as exc:
        logger.error("Follow-up generation failed: %s", exc)
        return jsonify(
            {"error": "Something went wrong getting a follow-up question. Please try again."}
        ), 502

    return jsonify(result)
