import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request

from content_filter import (
    find_bad_words,
    find_gibberish_words,
    find_possible_names,
    has_low_word_diversity,
)
from openai_client import DraftGenerationError, generate_draft
from prompts import build_system_prompt, build_user_prompt
from tone_guide import find_tempered_words
from word_count import count_words, get_range, is_in_range

MIN_WORDS_PER_ANSWER = 5

app = Flask(__name__)

ALLOWED_ORIGIN = "https://wesdlpteam.github.io"


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/api/generate", methods=["POST", "OPTIONS"])
def generate():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(silent=True) or {}

    report_type = data.get("report_type")
    answers = data.get("answers")
    pronouns = data.get("pronouns", "they/them")
    tutor_group = data.get("tutor_group")
    house = data.get("house")
    adjust = data.get("adjust")

    if report_type not in ["tutor", "pyp"]:
        return jsonify({"error": "report_type must be 'tutor' or 'pyp'"}), 400

    if not isinstance(answers, dict):
        return jsonify({"error": "answers must be an object"}), 400

    has_answer = any(str(v).strip() for v in answers.values())
    if not has_answer:
        return jsonify({"error": "at least one answer required"}), 400

    for value in answers.values():
        text = str(value).strip()
        if text and len(text.split()) < MIN_WORDS_PER_ANSWER:
            return jsonify(
                {"error": f"each answer needs at least {MIN_WORDS_PER_ANSWER} words"}
            ), 400
        if find_bad_words(text):
            return jsonify({"error": "please rewrite an answer without inappropriate language"}), 400
        if find_gibberish_words(text):
            return jsonify({"error": "one of your answers doesn't look like real text, please rewrite it"}), 400
        if has_low_word_diversity(text):
            return jsonify({"error": "one of your answers looks like repeated filler text, please write a genuine response"}), 400
        if find_possible_names(text):
            return jsonify(
                {"error": "please describe the student without using their name"}
            ), 400

    system_prompt = build_system_prompt(report_type, pronouns)
    user_prompt = build_user_prompt(report_type, answers, pronouns, tutor_group, house, adjust)

    try:
        draft = generate_draft(system_prompt, user_prompt)
    except DraftGenerationError as exc:
        return jsonify({"error": str(exc)}), 502

    word_count = count_words(draft)
    low, high = get_range(report_type)

    return jsonify(
        {
            "draft": draft,
            "word_count": word_count,
            "in_range": is_in_range(word_count, report_type),
            "target_range": [low, high],
            "tempered_words": find_tempered_words(answers),
        }
    )
