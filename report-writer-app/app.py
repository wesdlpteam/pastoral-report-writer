from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, request, send_from_directory

from content_filter import find_bad_words, find_gibberish_words, has_low_word_diversity
from openai_client import (
    DraftGenerationError,
    FollowupGenerationError,
    generate_draft,
    generate_followup,
)
from prompts import (
    ANSWER_LABELS,
    FOLLOWUP_SYSTEM_PROMPT,
    build_followup_user_prompt,
    build_system_prompt,
    build_user_prompt,
)
from tone_guide import find_tempered_words
from word_count import count_words, get_range, is_in_range

MIN_WORDS_PER_ANSWER = 5

app = Flask(__name__, static_folder="static", static_url_path="")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}

    report_type = data.get("report_type")
    pronouns = data.get("pronouns", "they/them")
    tutor_group = data.get("tutor_group")
    house = data.get("house")
    answers = data.get("answers")
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

    system_prompt = build_system_prompt(report_type, pronouns)
    user_prompt = build_user_prompt(
        report_type, answers, pronouns, tutor_group, house, adjust
    )

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


@app.route("/api/followup", methods=["POST"])
def followup():
    data = request.get_json(silent=True) or {}

    report_type = data.get("report_type")
    question_id = data.get("question_id")
    answer = str(data.get("answer", "")).strip()
    pronouns = data.get("pronouns", "they/them")

    if report_type not in ANSWER_LABELS:
        return jsonify({"error": "report_type must be 'tutor' or 'pyp'"}), 400
    if question_id not in ANSWER_LABELS[report_type]:
        return jsonify({"error": "unknown question_id for this report_type"}), 400
    if not answer:
        return jsonify({"error": "answer is required"}), 400

    question_label = ANSWER_LABELS[report_type][question_id]
    user_prompt = build_followup_user_prompt(question_label, answer, pronouns)

    try:
        result = generate_followup(FOLLOWUP_SYSTEM_PROMPT, user_prompt)
    except FollowupGenerationError as exc:
        return jsonify({"error": str(exc)}), 502

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
