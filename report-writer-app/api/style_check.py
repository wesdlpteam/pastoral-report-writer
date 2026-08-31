import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request

from content_filter import find_bad_words
from openai_client import StyleCheckGenerationError, generate_style_check
from prompts import STYLE_CHECK_SYSTEM_PROMPT, build_style_check_user_prompt
from word_count import get_range

logger = logging.getLogger(__name__)

MIN_CHECK_WORDS = 15
MAX_CHECK_WORDS = 600

app = Flask(__name__)

ALLOWED_ORIGIN = "https://wesdlpteam.github.io"


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/api/style_check", methods=["POST", "OPTIONS"])
def style_check():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()

    if not text:
        return jsonify({"error": "please paste the report text to check"}), 400

    word_count = len(text.split())
    if word_count < MIN_CHECK_WORDS:
        return jsonify({"error": f"please paste at least {MIN_CHECK_WORDS} words"}), 400
    if word_count > MAX_CHECK_WORDS:
        return jsonify(
            {"error": f"please paste no more than {MAX_CHECK_WORDS} words at a time"}
        ), 400
    if find_bad_words(text):
        return jsonify({"error": "please remove inappropriate language before checking"}), 400

    user_prompt = build_style_check_user_prompt(text)

    try:
        result = generate_style_check(STYLE_CHECK_SYSTEM_PROMPT, user_prompt)
    except StyleCheckGenerationError as exc:
        logger.error("Style check failed: %s", exc)
        return jsonify(
            {"error": "Something went wrong checking your report. Please try again in a moment."}
        ), 502

    low, high = get_range("tutor")
    result["original_text"] = text
    result["word_count"] = word_count
    result["target_range"] = [low, high]
    result["meets_minimum_length"] = word_count >= low
    return jsonify(result)
