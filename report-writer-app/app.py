from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, request, send_from_directory

from openai_client import DraftGenerationError, generate_draft
from prompts import build_system_prompt, build_user_prompt
from tone_guide import find_tempered_words
from word_count import count_words, get_range, is_in_range

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


if __name__ == "__main__":
    app.run(debug=True)
