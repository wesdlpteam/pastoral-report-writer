# Pastoral Report Writing Companion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Flask + vanilla JS web app that interviews a Wesley College teacher about a student (Q&A with chips + free text, no student name ever entered) and drafts a pastoral report comment via the OpenAI API, matching Wesley's Tutor Report and PYP Semester Report structures and word counts.

**Architecture:** Flask backend (`report-writer-app/app.py`) exposes `POST /api/generate` and serves a static single-page frontend. Backend logic split into small, independently testable modules (word counting, prompt building, OpenAI call) so each has its own unit tests without needing a real API key. Frontend is plain HTML/CSS/JS, no build step.

**Tech Stack:** Python 3.13, Flask, `openai` Python SDK, `python-dotenv`, `pytest` for backend tests. No frontend framework.

## Global Constraints

- Tutor Report word count: 100–150 words (from `Years 7 to12 Tutor Report Guidelines - 2026.pdf`).
- PYP Report word count: 180–300 words (from `PYP Semester Report Guidelines.pdf`).
- Student's real name is never entered into the tool, never sent to the AI, never logged. Draft output always uses the literal placeholder `[student name]`.
- No persistence: no database, no server-side logging of answers or drafts beyond serving the single request/response.
- OpenAI API key lives only in `report-writer-app/.env` (git-ignored), read via environment variable, never hardcoded, never sent to the frontend.
- Default AI model: `gpt-4o-mini`, overridable via `OPENAI_MODEL` env var.
- Visual style: Wesley brand tokens only — purple `#4F2759` (primary/interactive), gold `#C59F40` (accent), neutrals `#EFEDED` / `#E6E2DD` / `#DAD7D1`, black/white. No Inter/Roboto, no gradients, no generic AI-default look.
- New code lives in `report-writer-app/`, sitting next to (not inside) the existing `Pastoral Report Writer/` training-material folder, which stays git-ignored and untouched.
- The six sample docx files contain a pre-existing `[student name]` placeholder convention from the school's own de-identification (with occasional text-concatenation artifacts from that process) plus two stray real first names ("Alistair", "Chloe") that must never appear in this codebase.

---

### Task 1: Project scaffolding

**Files:**
- Create: `report-writer-app/requirements.txt`
- Create: `report-writer-app/.env.example`
- Create: `report-writer-app/tests/conftest.py`
- Create: `report-writer-app/tests/__init__.py` (empty)

**Interfaces:**
- Produces: a `report-writer-app/` directory that all later tasks write into, and a `tests/conftest.py` that makes `from app import ...`, `from word_count import ...`, etc. resolve correctly when `pytest` is run from inside `report-writer-app/`.

- [ ] **Step 1: Create the folder and requirements file**

```
report-writer-app/requirements.txt
```

```
flask>=3.0
openai>=1.40
python-dotenv>=1.0
pytest>=8.0
```

- [ ] **Step 2: Create the env example file**

Create `report-writer-app/.env.example` (this is a template file, safe to commit, holds no real credential) with two lines:
- The `OPENAI_API_KEY` variable, left blank as a placeholder for each developer to fill in locally.
- The `OPENAI_MODEL` variable, set to the default model name `gpt-4o-mini`.

The real `report-writer-app/.env` (git-ignored, created later in Task 9) is where an actual key value goes — never in `.env.example`, never committed.

- [ ] **Step 3: Create the test path fixup**

```
report-writer-app/tests/conftest.py
```

```python
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

```
report-writer-app/tests/__init__.py
```

(empty file)

- [ ] **Step 4: Set up a virtual environment and install dependencies**

Run: `cd report-writer-app && python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt`
Expected: pip installs flask, openai, python-dotenv, pytest with no errors.

- [ ] **Step 5: Commit**

```bash
cd "/c/Users/delmastroa/OneDrive - Wesley College/Documents/App Dev/Pastoral Engine"
git add report-writer-app/requirements.txt report-writer-app/.env.example report-writer-app/tests/conftest.py report-writer-app/tests/__init__.py
git commit -m "chore: scaffold report-writer-app project"
```

---

### Task 2: Word counting

**Files:**
- Create: `report-writer-app/word_count.py`
- Test: `report-writer-app/tests/test_word_count.py`

**Interfaces:**
- Produces: `count_words(text: str) -> int`, `get_range(report_type: str) -> tuple[int, int]`, `is_in_range(word_count: int, report_type: str) -> bool`, `REPORT_RANGES: dict`. Used by `app.py` (Task 6) and `prompts.py` (Task 4).

- [ ] **Step 1: Write the failing tests**

```
report-writer-app/tests/test_word_count.py
```

```python
from word_count import count_words, get_range, is_in_range


def test_count_words_basic():
    assert count_words("This is five words total") == 5


def test_count_words_empty_string():
    assert count_words("") == 0


def test_count_words_extra_whitespace():
    assert count_words("  word   another   ") == 2


def test_get_range_tutor():
    assert get_range("tutor") == (100, 150)


def test_get_range_pyp():
    assert get_range("pyp") == (180, 300)


def test_is_in_range_true():
    assert is_in_range(120, "tutor") is True


def test_is_in_range_false_below():
    assert is_in_range(50, "tutor") is False


def test_is_in_range_false_above():
    assert is_in_range(200, "tutor") is False


def test_is_in_range_boundary_inclusive():
    assert is_in_range(100, "tutor") is True
    assert is_in_range(150, "tutor") is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd report-writer-app && .venv/Scripts/python -m pytest tests/test_word_count.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'word_count'`

- [ ] **Step 3: Write the implementation**

```
report-writer-app/word_count.py
```

```python
REPORT_RANGES = {
    "tutor": (100, 150),
    "pyp": (180, 300),
}


def count_words(text: str) -> int:
    return len(text.split())


def get_range(report_type: str) -> tuple[int, int]:
    return REPORT_RANGES[report_type]


def is_in_range(word_count: int, report_type: str) -> bool:
    low, high = get_range(report_type)
    return low <= word_count <= high
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd report-writer-app && .venv/Scripts/python -m pytest tests/test_word_count.py -v`
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
cd "/c/Users/delmastroa/OneDrive - Wesley College/Documents/App Dev/Pastoral Engine"
git add report-writer-app/word_count.py report-writer-app/tests/test_word_count.py
git commit -m "feat: add word counting and range checks"
```

---

### Task 3: Style example corpus

**Files:**
- Create: `report-writer-app/style_examples.py`
- Test: `report-writer-app/tests/test_style_examples.py`

**Interfaces:**
- Produces: `TUTOR_EXAMPLES: list[str]`. Used by `prompts.py` (Task 4) to calibrate Tutor Report drafting style.

- [ ] **Step 1: Write the failing tests**

```
report-writer-app/tests/test_style_examples.py
```

```python
from style_examples import TUTOR_EXAMPLES


def test_tutor_examples_not_empty():
    assert len(TUTOR_EXAMPLES) >= 4


def test_tutor_examples_are_strings():
    assert all(isinstance(example, str) for example in TUTOR_EXAMPLES)


def test_tutor_examples_use_placeholder():
    for example in TUTOR_EXAMPLES:
        assert "[student name]" in example


def test_tutor_examples_no_real_names_leak():
    banned_names = ["Alistair", "Chloe"]
    for example in TUTOR_EXAMPLES:
        for name in banned_names:
            assert name not in example
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd report-writer-app && .venv/Scripts/python -m pytest tests/test_style_examples.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'style_examples'`

- [ ] **Step 3: Write the implementation**

These five excerpts are hand-selected and lightly cleaned from the six sample docx files reviewed earlier in this project (`Saville examples.docx`, `grace samples.docx`, `russell sample.docx`, `sparrow examples.docx`). The two stray real first names found in the source files ("Alistair" in `grace samples.docx`, "Chloe" in `sparrow examples.docx`) are replaced with the placeholder here, and one glued-word artifact ("SAMPLE[student name]") from the source file's own de-identification pass is fixed to read naturally.

```
report-writer-app/style_examples.py
```

```python
TUTOR_EXAMPLES = [
    "[student name] is a gentle and reserved student who contributes "
    "positively to our Homeroom community. He enjoys interacting with his "
    "peers in the classroom and playground and is happy within his social "
    "environment in the Middle School. It has been pleasing to observe "
    "[student name] taking greater responsibility for his approaches to "
    "learning. He is being encouraged to adopt a more consistent "
    "application to classroom tasks, so that his work always reflects his "
    "best effort.",

    "[student name] is a bright and social member of the Tutor Group who "
    "consistently displays the ROAR tenets of Respect, Opportunity, "
    "Achievement, and Resilience in all facets of her learning. She has "
    "adapted well to the demands of Year 7. In the classroom, she is "
    "engaged and hardworking, and in music and sport, she participates "
    "with enthusiasm. As Year 7 Kerrie House leader, she serves as a "
    "role-model during House events, motivating her peers to do their "
    "best and, in turn, fostering a strong sense of team spirit and "
    "inclusivity during these activities. In Tutor Group, [student name] "
    "is collaborative and open-minded. She both expresses her opinion "
    "and allows others to contribute. Although she loves to socialise, "
    "she channels her energy productively when she needs to. [student "
    "name] should be proud of such a positive start to the year and "
    "should continue to seek out opportunities in Semester 2.",

    "[student name] continues to be a very outgoing, friendly, and "
    "polite member of our Tutorial Group as he moves through Year 12, "
    "though he could be more attentive to the expectations for personal "
    "presentation at school. I am pleased that he is feeling increasingly "
    "motivated in his studies as the year progresses and that he has "
    "found a workable balance between school and social life. The "
    "feedback from his teachers on WiSE suggests that he is making good "
    "progress, and I hope he is following up on their suggestions and "
    "comments. I have enjoyed having [student name] in our Tutorial for "
    "the last three years and seeing him grow as a person over that "
    "time. I wish him the best of luck as he moves towards the Year 12 "
    "exams.",

    "[student name] reflected that she has had a positive start to her "
    "final year at Wesley, with the school formal being a clear "
    "highlight. [student name] has been actively involved in House "
    "activities, including spoons, volleyball, and trivia, making a "
    "valuable contribution to our House spirit. She identified managing "
    "the demanding workload and closely scheduled SACs as a key "
    "challenge this semester. It was encouraging to hear that she has "
    "addressed this by developing a study timetable and making "
    "productive use of her study periods. Looking ahead, [student name] "
    "is keen to continue her involvement in House events and continue "
    "building on her study habits. It has been a delight to have "
    "[student name] in our Tutor Group over the past three years, and I "
    "hope she thoroughly enjoys all the special events leading up to "
    "graduation.",

    "[student name] is a social and enthusiastic member of the Tutor "
    "Group. Throughout Semester 1, [student name] has consistently "
    "displayed the tenets of Opportunity and Resilience as evidenced by "
    "the growth in maturity he has shown transiting from the PYP to the "
    "MYP. Although the academic demands of Year 7 are at times "
    "challenging, he is developing organisational skills to help him "
    "build consistent work habits. [student name]'s true passion is "
    "sports; whether in Physical and Health Education or on the tennis "
    "court, he thrives when able to move freely. For subjects that he "
    "finds more challenging, he is encouraged to seek feedback on his "
    "work and develop a routine for Home Learning tasks. In Tutor "
    "Group, [student name] contributes openly to discussions and "
    "enjoys working collaboratively with his peers. He should be proud "
    "of the way he has embraced new challenges and should keep building "
    "good organisation habits.",
]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd report-writer-app && .venv/Scripts/python -m pytest tests/test_style_examples.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
cd "/c/Users/delmastroa/OneDrive - Wesley College/Documents/App Dev/Pastoral Engine"
git add report-writer-app/style_examples.py report-writer-app/tests/test_style_examples.py
git commit -m "feat: add cleaned Tutor Report style examples"
```

---

### Task 4: Prompt building

**Files:**
- Create: `report-writer-app/prompts.py`
- Test: `report-writer-app/tests/test_prompts.py`

**Interfaces:**
- Consumes: `get_range` from `word_count.py` (Task 2), `TUTOR_EXAMPLES` from `style_examples.py` (Task 3).
- Produces: `build_system_prompt(report_type: str) -> str`, `build_user_prompt(report_type: str, answers: dict) -> str`, `ANSWER_LABELS: dict`. Used by `app.py` (Task 6).

- [ ] **Step 1: Write the failing tests**

```
report-writer-app/tests/test_prompts.py
```

```python
from prompts import build_system_prompt, build_user_prompt


def test_build_system_prompt_tutor_has_word_range():
    prompt = build_system_prompt("tutor")
    assert "100-150 words" in prompt


def test_build_system_prompt_pyp_has_word_range():
    prompt = build_system_prompt("pyp")
    assert "180-300 words" in prompt


def test_build_system_prompt_tutor_includes_examples():
    prompt = build_system_prompt("tutor")
    assert "Example 1:" in prompt


def test_build_system_prompt_pyp_has_no_examples_section():
    prompt = build_system_prompt("pyp")
    assert "Example 1:" not in prompt


def test_build_system_prompt_always_uses_placeholder_instruction():
    for report_type in ("tutor", "pyp"):
        prompt = build_system_prompt(report_type)
        assert "[student name]" in prompt


def test_build_user_prompt_includes_answers():
    answers = {
        "person": "resilient and kind",
        "learner": "improving steadily",
        "participant": "engaged",
        "summary": "",
    }
    prompt = build_user_prompt("tutor", answers)
    assert "resilient and kind" in prompt
    assert "improving steadily" in prompt


def test_build_user_prompt_skips_empty_answers():
    answers = {"person": "", "learner": "improving", "participant": "", "summary": ""}
    prompt = build_user_prompt("tutor", answers)
    assert "The student as a person" not in prompt
    assert "improving" in prompt


def test_build_user_prompt_pyp_uses_pyp_labels():
    answers = {"learner_social": "curious", "atl": "", "achievement": "", "next_steps": ""}
    prompt = build_user_prompt("pyp", answers)
    assert "Who they are as a learner and socially" in prompt
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd report-writer-app && .venv/Scripts/python -m pytest tests/test_prompts.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'prompts'`

- [ ] **Step 3: Write the implementation**

```
report-writer-app/prompts.py
```

```python
from word_count import get_range
from style_examples import TUTOR_EXAMPLES

STYLE_GUIDE_NOTES = (
    "Follow Wesley College's editorial style: no contractions (write "
    '"do not" not "don\'t"); write "Year 9" not "Y9"; write "Semester 1" '
    'and "Tutor Group" (two words); use Australian English spelling '
    "(organisation, colour); avoid jargon and keep sentences clear."
)

REPORT_RULES = {
    "tutor": (
        "You are drafting a Wesley College Years 7-12 Tutor Report "
        "comment. The comment must be {low}-{high} words. It must cover "
        "exactly four themes in this order: (1) the student as a person "
        "- character, resilience, personal qualities; (2) the student as "
        "a learner - academic wellbeing and progress; (3) the student as "
        "a participant in the Tutor Group - engagement with the group; "
        "(4) a summarising, strengths-based, future-focused closing "
        "sentence. Write in third person, past tense where natural, and "
        'always refer to the student as "[student name]" - never invent '
        "a real name."
    ),
    "pyp": (
        "You are drafting a Wesley College PYP (Prep-Year 6) Semester "
        "Report personal profile comment. The comment must be "
        "{low}-{high} words. It must cover: personal knowledge of the "
        "student (who they are as a learner and socially), an "
        "Approaches to Learning skill with a specific example, an "
        "achievement or participation example, and clear, manageable "
        "next steps for the student as a learner. Write in third "
        "person, past tense where natural, and always refer to the "
        'student as "[student name]" - never invent a real name.'
    ),
}

ANSWER_LABELS = {
    "tutor": {
        "person": "The student as a person",
        "learner": "The student as a learner",
        "participant": "The student as a Tutor Group participant",
        "summary": "Additional closing notes",
    },
    "pyp": {
        "learner_social": "Who they are as a learner and socially",
        "atl": "Approaches to Learning strength and example",
        "achievement": "Achievement or participation example",
        "next_steps": "Next steps for the student as a learner",
    },
}


def build_system_prompt(report_type: str) -> str:
    low, high = get_range(report_type)
    rules = REPORT_RULES[report_type].format(low=low, high=high)
    parts = [rules, STYLE_GUIDE_NOTES]

    if report_type == "tutor":
        examples_block = "\n\n".join(
            f"Example {i}:\n{example}"
            for i, example in enumerate(TUTOR_EXAMPLES, start=1)
        )
        parts.append(
            "Here are real examples of Wesley's Tutor Report voice and "
            "structure to match in tone (do not copy content, only "
            "style):\n\n" + examples_block
        )

    return "\n\n".join(parts)


def build_user_prompt(report_type: str, answers: dict) -> str:
    labels = ANSWER_LABELS[report_type]
    lines = ["Teacher's notes about the student:"]
    for key, label in labels.items():
        value = str(answers.get(key, "")).strip()
        if value:
            lines.append(f"- {label}: {value}")
    lines.append("\nWrite the report comment now, following the rules above exactly.")
    return "\n".join(lines)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd report-writer-app && .venv/Scripts/python -m pytest tests/test_prompts.py -v`
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
cd "/c/Users/delmastroa/OneDrive - Wesley College/Documents/App Dev/Pastoral Engine"
git add report-writer-app/prompts.py report-writer-app/tests/test_prompts.py
git commit -m "feat: add system/user prompt builders for both report types"
```

---

### Task 5: OpenAI client wrapper

**Files:**
- Create: `report-writer-app/openai_client.py`
- Test: `report-writer-app/tests/test_openai_client.py`

**Interfaces:**
- Produces: `generate_draft(system_prompt: str, user_prompt: str) -> str`, `DraftGenerationError(Exception)`. Used by `app.py` (Task 6). Reads `OPENAI_API_KEY` and `OPENAI_MODEL` from the environment; raises `DraftGenerationError` if the key is missing or the API call fails.

- [ ] **Step 1: Write the failing tests**

```
report-writer-app/tests/test_openai_client.py
```

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd report-writer-app && .venv/Scripts/python -m pytest tests/test_openai_client.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'openai_client'`

- [ ] **Step 3: Write the implementation**

```
report-writer-app/openai_client.py
```

```python
import os

from openai import OpenAI


class DraftGenerationError(Exception):
    pass


def generate_draft(system_prompt: str, user_prompt: str) -> str:
    if not os.environ.get("OPENAI_API_KEY"):
        raise DraftGenerationError("OPENAI_API_KEY is not set")

    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    # OpenAI() with no arguments reads the key from the OPENAI_API_KEY
    # environment variable automatically - the key is never handled as a
    # local variable or literal in this codebase.
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd report-writer-app && .venv/Scripts/python -m pytest tests/test_openai_client.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd "/c/Users/delmastroa/OneDrive - Wesley College/Documents/App Dev/Pastoral Engine"
git add report-writer-app/openai_client.py report-writer-app/tests/test_openai_client.py
git commit -m "feat: add OpenAI client wrapper with error handling"
```

---

### Task 6: Flask app and API endpoint

**Files:**
- Create: `report-writer-app/app.py`
- Test: `report-writer-app/tests/test_app.py`

**Interfaces:**
- Consumes: `count_words`, `get_range`, `is_in_range` from `word_count.py` (Task 2); `build_system_prompt`, `build_user_prompt` from `prompts.py` (Task 4); `generate_draft`, `DraftGenerationError` from `openai_client.py` (Task 5).
- Produces: Flask app instance `app`, route `GET /` (serves `static/index.html`), route `POST /api/generate` accepting `{"report_type": str, "answers": dict}` and returning `{"draft": str, "word_count": int, "in_range": bool, "target_range": [int, int]}` on success or `{"error": str}` with 400/502 on failure. Used by `static/script.js` (Task 7) and by manual verification (Task 8/9).

- [ ] **Step 1: Write the failing tests**

```
report-writer-app/tests/test_app.py
```

```python
from unittest.mock import patch

import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_index_serves_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<html" in response.data.lower()


def test_generate_missing_report_type(client):
    response = client.post("/api/generate", json={"answers": {}})
    assert response.status_code == 400


def test_generate_invalid_report_type(client):
    response = client.post("/api/generate", json={"report_type": "bogus", "answers": {}})
    assert response.status_code == 400


def test_generate_missing_required_answers(client):
    response = client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "answers": {"person": "", "learner": "", "participant": ""},
        },
    )
    assert response.status_code == 400
    body = response.get_json()
    assert "missing required answers" in body["error"]


@patch("app.generate_draft")
def test_generate_success_tutor(mock_generate_draft, client):
    mock_generate_draft.return_value = " ".join(["word"] * 120)

    response = client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "answers": {
                "person": "resilient",
                "learner": "improving",
                "participant": "engaged",
                "summary": "",
            },
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["word_count"] == 120
    assert body["in_range"] is True
    assert body["target_range"] == [100, 150]


@patch("app.generate_draft")
def test_generate_openai_failure_returns_502(mock_generate_draft, client):
    from openai_client import DraftGenerationError

    mock_generate_draft.side_effect = DraftGenerationError("boom")

    response = client.post(
        "/api/generate",
        json={
            "report_type": "tutor",
            "answers": {"person": "x", "learner": "y", "participant": "z"},
        },
    )

    assert response.status_code == 502


@patch("app.generate_draft")
def test_generate_success_pyp(mock_generate_draft, client):
    mock_generate_draft.return_value = " ".join(["word"] * 200)

    response = client.post(
        "/api/generate",
        json={
            "report_type": "pyp",
            "answers": {
                "learner_social": "curious",
                "atl": "strong thinking skills",
                "achievement": "camp",
                "next_steps": "keep reading widely",
            },
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["target_range"] == [180, 300]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd report-writer-app && .venv/Scripts/python -m pytest tests/test_app.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app'`

- [ ] **Step 3: Write the implementation**

```
report-writer-app/app.py
```

```python
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, request, send_from_directory

from openai_client import DraftGenerationError, generate_draft
from prompts import build_system_prompt, build_user_prompt
from word_count import count_words, get_range, is_in_range

app = Flask(__name__, static_folder="static", static_url_path="")

REQUIRED_KEYS = {
    "tutor": ["person", "learner", "participant"],
    "pyp": ["learner_social", "atl", "achievement", "next_steps"],
}


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    report_type = data.get("report_type")
    answers = data.get("answers")

    if report_type not in REQUIRED_KEYS:
        return jsonify({"error": "report_type must be 'tutor' or 'pyp'"}), 400
    if not isinstance(answers, dict):
        return jsonify({"error": "answers must be an object"}), 400

    missing = [
        key
        for key in REQUIRED_KEYS[report_type]
        if not str(answers.get(key, "")).strip()
    ]
    if missing:
        return (
            jsonify({"error": f"missing required answers: {', '.join(missing)}"}),
            400,
        )

    system_prompt = build_system_prompt(report_type)
    user_prompt = build_user_prompt(report_type, answers)

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
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
```

Note: `static/index.html` doesn't exist yet (created in Task 7), so `test_index_serves_html` will fail at Step 4 until Task 7 is done. Create a minimal placeholder now so this task's tests pass in isolation:

```
report-writer-app/static/index.html
```

```html
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Pastoral Report Writing Companion</title></head>
<body><p>Loading...</p></body>
</html>
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd report-writer-app && .venv/Scripts/python -m pytest tests/test_app.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
cd "/c/Users/delmastroa/OneDrive - Wesley College/Documents/App Dev/Pastoral Engine"
git add report-writer-app/app.py report-writer-app/tests/test_app.py report-writer-app/static/index.html
git commit -m "feat: add Flask app with /api/generate endpoint"
```

---

### Task 7: Frontend Q&A interface

**Files:**
- Modify: `report-writer-app/static/index.html` (replace placeholder from Task 6)
- Create: `report-writer-app/static/style.css`
- Create: `report-writer-app/static/script.js`

**Interfaces:**
- Consumes: `POST /api/generate` from `app.py` (Task 6), request/response shape as defined there.
- Produces: the full teacher-facing UI. No later tasks depend on its internals.

- [ ] **Step 1: Replace the placeholder HTML**

```
report-writer-app/static/index.html
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Pastoral Report Writing Companion</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <header class="header">
    <h1>Pastoral Report Writing Companion</h1>
    <p class="tagline">Answer a few quick questions, get a Wesley-style draft.</p>
  </header>

  <main class="app">
    <section id="screen-select" class="screen">
      <h2>Which report are you writing?</h2>
      <div class="type-choices">
        <button class="type-btn" data-type="tutor">
          <span class="type-title">Tutor Report</span>
          <span class="type-sub">Years 7&ndash;12 &middot; 100&ndash;150 words</span>
        </button>
        <button class="type-btn" data-type="pyp">
          <span class="type-title">PYP Semester Report</span>
          <span class="type-sub">Prep&ndash;6 &middot; 180&ndash;300 words</span>
        </button>
      </div>
    </section>

    <section id="screen-question" class="screen hidden">
      <p class="progress" id="progress-text"></p>
      <h2 id="question-text"></h2>
      <div class="chips" id="chip-container"></div>
      <label class="freetext-label" for="freetext-input">Add specifics (optional)</label>
      <textarea id="freetext-input" rows="3" placeholder="Type anything specific here..."></textarea>
      <div class="nav-buttons">
        <button id="back-btn" class="btn btn-secondary">Back</button>
        <button id="next-btn" class="btn btn-primary">Next</button>
        <button id="generate-btn" class="btn btn-primary hidden">Generate draft</button>
      </div>
    </section>

    <section id="screen-result" class="screen hidden">
      <h2>Draft comment</h2>
      <p id="error-banner" class="error-banner hidden"></p>
      <p id="loading-text" class="loading-text hidden">Writing your draft...</p>
      <textarea id="draft-text" rows="10" class="hidden"></textarea>
      <p class="word-count hidden" id="word-count-text"></p>
      <div class="result-buttons">
        <button id="regenerate-btn" class="btn btn-secondary hidden">Regenerate</button>
        <button id="copy-btn" class="btn btn-primary hidden">Copy</button>
        <button id="start-over-btn" class="btn btn-secondary">Start a new student</button>
      </div>
    </section>
  </main>

  <script src="script.js"></script>
</body>
</html>
```

- [ ] **Step 2: Write the stylesheet**

```
report-writer-app/static/style.css
```

```css
:root {
  --wes-purple: #4F2759;
  --wes-gold: #C59F40;
  --wes-black: #000000;
  --wes-white: #FFFFFF;
  --wes-neutral-100: #EFEDED;
  --wes-neutral-200: #E6E2DD;
  --wes-neutral-300: #DAD7D1;
  --wes-neutral-900: #2B281F;
  --wes-error: #E83534;
  --wes-ink-gold: #7A5012;
  --wes-font-ui: "Graphik", "Segoe UI", system-ui, sans-serif;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: var(--wes-font-ui);
  background: var(--wes-neutral-100);
  color: var(--wes-neutral-900);
}

.header {
  background: var(--wes-purple);
  color: var(--wes-white);
  padding: 2.5rem 1.5rem;
  text-align: left;
}

.header h1 {
  margin: 0 0 0.25rem 0;
  font-size: clamp(1.5rem, 4vw, 2.25rem);
  color: var(--wes-gold);
}

.header .tagline {
  margin: 0;
  color: var(--wes-white);
}

.app {
  max-width: 640px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
}

.screen.hidden {
  display: none;
}

.type-choices {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1.5rem;
}

.type-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.35rem;
  padding: 1.5rem;
  border: none;
  border-radius: 4px;
  background: var(--wes-purple);
  color: var(--wes-white);
  cursor: pointer;
  text-align: left;
}

.type-btn:hover {
  background: var(--wes-neutral-900);
}

.type-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--wes-gold);
}

.type-sub {
  color: var(--wes-white);
}

.progress {
  color: var(--wes-purple);
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 1rem 0;
}

.chip {
  padding: 0.5rem 1rem;
  border-radius: 999px;
  border: 2px solid var(--wes-purple);
  background: var(--wes-white);
  color: var(--wes-purple);
  cursor: pointer;
  font-family: var(--wes-font-ui);
  font-size: 0.95rem;
}

.chip.selected {
  background: var(--wes-purple);
  color: var(--wes-white);
}

.freetext-label {
  display: block;
  margin-top: 1rem;
  font-weight: 600;
}

textarea {
  width: 100%;
  padding: 0.75rem;
  font-family: var(--wes-font-ui);
  font-size: 1rem;
  border: 2px solid var(--wes-neutral-300);
  border-radius: 4px;
  margin-top: 0.5rem;
}

.nav-buttons,
.result-buttons {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  border: none;
  font-family: var(--wes-font-ui);
  font-size: 1rem;
  cursor: pointer;
}

.btn-primary {
  background: var(--wes-purple);
  color: var(--wes-white);
}

.btn-primary:hover {
  background: var(--wes-neutral-900);
}

.btn-secondary {
  background: var(--wes-white);
  color: var(--wes-purple);
  border: 2px solid var(--wes-purple);
}

.btn-secondary:hover {
  background: var(--wes-neutral-200);
}

.hidden {
  display: none !important;
}

.error-banner {
  background: var(--wes-error);
  color: var(--wes-white);
  padding: 0.75rem 1rem;
  border-radius: 4px;
}

.loading-text {
  color: var(--wes-purple);
  font-weight: 600;
}

.word-count {
  font-weight: 600;
  margin-top: 0.5rem;
}

.word-count.out-of-range {
  color: var(--wes-ink-gold);
}

.word-count.in-range {
  color: var(--wes-purple);
}
```

- [ ] **Step 3: Write the frontend logic**

```
report-writer-app/static/script.js
```

```javascript
const QUESTIONS = {
  tutor: [
    {
      id: "person",
      question: "What's this student like as a person?",
      chips: [
        "Resilient",
        "Quiet / reserved",
        "Friendly and outgoing",
        "Organised",
        "Still building confidence",
        "Kind to peers",
      ],
    },
    {
      id: "learner",
      question: "How are they doing as a learner?",
      chips: [
        "Strong academic progress",
        "Developing steadily",
        "Needs more consistency",
        "Asks great questions",
        "Working hard to catch up",
      ],
    },
    {
      id: "participant",
      question: "How do they take part in Tutor Group?",
      chips: [
        "Actively engaged",
        "Quiet but present",
        "Supportive of peers",
        "Still settling in",
        "Takes on a leadership role",
      ],
    },
    {
      id: "summary",
      question: "Anything else to add? (optional)",
      chips: [],
    },
  ],
  pyp: [
    {
      id: "learner_social",
      question: "Who are they as a learner and socially?",
      chips: [
        "Curious and inquisitive",
        "Confident in social settings",
        "Quiet but kind",
        "Works well in groups",
        "Prefers working independently",
      ],
    },
    {
      id: "atl",
      question: "What's an Approaches to Learning strength, with an example?",
      chips: [
        "Strong thinking skills",
        "Strong research skills",
        "Strong communication skills",
        "Strong social skills",
        "Strong self-management skills",
      ],
    },
    {
      id: "achievement",
      question: "Any achievement or participation to highlight?",
      chips: [
        "Co-curricular activity",
        "Camp / Education Outdoors",
        "Passion project",
        "Leadership role",
        "Group task success",
      ],
    },
    {
      id: "next_steps",
      question: "What's the next step for them as a learner?",
      chips: [],
    },
  ],
};

const state = {
  reportType: null,
  index: 0,
  answers: {},
  selectedChips: {},
};

const screenSelect = document.getElementById("screen-select");
const screenQuestion = document.getElementById("screen-question");
const screenResult = document.getElementById("screen-result");

const progressText = document.getElementById("progress-text");
const questionText = document.getElementById("question-text");
const chipContainer = document.getElementById("chip-container");
const freetextInput = document.getElementById("freetext-input");
const backBtn = document.getElementById("back-btn");
const nextBtn = document.getElementById("next-btn");
const generateBtn = document.getElementById("generate-btn");

const errorBanner = document.getElementById("error-banner");
const loadingText = document.getElementById("loading-text");
const draftText = document.getElementById("draft-text");
const wordCountText = document.getElementById("word-count-text");
const regenerateBtn = document.getElementById("regenerate-btn");
const copyBtn = document.getElementById("copy-btn");
const startOverBtn = document.getElementById("start-over-btn");

document.querySelectorAll(".type-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    state.reportType = btn.dataset.type;
    state.index = 0;
    state.answers = {};
    state.selectedChips = {};
    showScreen(screenQuestion);
    renderQuestion();
  });
});

function showScreen(screen) {
  [screenSelect, screenQuestion, screenResult].forEach((s) => s.classList.add("hidden"));
  screen.classList.remove("hidden");
}

function currentQuestions() {
  return QUESTIONS[state.reportType];
}

function renderQuestion() {
  const questions = currentQuestions();
  const q = questions[state.index];

  progressText.textContent = `Question ${state.index + 1} of ${questions.length}`;
  questionText.textContent = q.question;

  chipContainer.innerHTML = "";
  const selected = state.selectedChips[q.id] || [];
  q.chips.forEach((chipLabel) => {
    const chipEl = document.createElement("button");
    chipEl.type = "button";
    chipEl.className = "chip";
    chipEl.textContent = chipLabel;
    if (selected.includes(chipLabel)) {
      chipEl.classList.add("selected");
    }
    chipEl.addEventListener("click", () => toggleChip(q.id, chipLabel, chipEl));
    chipContainer.appendChild(chipEl);
  });

  freetextInput.value = state.answers[`${q.id}__freetext`] || "";

  backBtn.classList.toggle("hidden", state.index === 0);
  const isLast = state.index === questions.length - 1;
  nextBtn.classList.toggle("hidden", isLast);
  generateBtn.classList.toggle("hidden", !isLast);
}

function toggleChip(questionId, chipLabel, chipEl) {
  const selected = state.selectedChips[questionId] || [];
  const idx = selected.indexOf(chipLabel);
  if (idx === -1) {
    selected.push(chipLabel);
    chipEl.classList.add("selected");
  } else {
    selected.splice(idx, 1);
    chipEl.classList.remove("selected");
  }
  state.selectedChips[questionId] = selected;
}

function saveCurrentAnswer() {
  const q = currentQuestions()[state.index];
  state.answers[`${q.id}__freetext`] = freetextInput.value;
  const chips = state.selectedChips[q.id] || [];
  const freetext = freetextInput.value.trim();

  let combined = "";
  if (chips.length && freetext) {
    combined = `${chips.join(", ")}. ${freetext}`;
  } else if (chips.length) {
    combined = chips.join(", ");
  } else {
    combined = freetext;
  }
  state.answers[q.id] = combined;
}

backBtn.addEventListener("click", () => {
  saveCurrentAnswer();
  state.index -= 1;
  renderQuestion();
});

nextBtn.addEventListener("click", () => {
  saveCurrentAnswer();
  state.index += 1;
  renderQuestion();
});

generateBtn.addEventListener("click", () => {
  saveCurrentAnswer();
  showScreen(screenResult);
  generateDraft();
});

regenerateBtn.addEventListener("click", () => {
  generateDraft();
});

copyBtn.addEventListener("click", () => {
  draftText.select();
  navigator.clipboard.writeText(draftText.value);
});

startOverBtn.addEventListener("click", () => {
  state.reportType = null;
  state.index = 0;
  state.answers = {};
  state.selectedChips = {};
  showScreen(screenSelect);
});

async function generateDraft() {
  errorBanner.classList.add("hidden");
  draftText.classList.add("hidden");
  wordCountText.classList.add("hidden");
  regenerateBtn.classList.add("hidden");
  copyBtn.classList.add("hidden");
  loadingText.classList.remove("hidden");

  const payloadAnswers = {};
  currentQuestions().forEach((q) => {
    payloadAnswers[q.id] = state.answers[q.id] || "";
  });

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ report_type: state.reportType, answers: payloadAnswers }),
    });
    const body = await response.json();

    if (!response.ok) {
      throw new Error(body.error || "Something went wrong generating the draft.");
    }

    draftText.value = body.draft;
    wordCountText.textContent = `${body.word_count} words (target: ${body.target_range[0]}-${body.target_range[1]})`;
    wordCountText.classList.toggle("in-range", body.in_range);
    wordCountText.classList.toggle("out-of-range", !body.in_range);

    draftText.classList.remove("hidden");
    wordCountText.classList.remove("hidden");
    regenerateBtn.classList.remove("hidden");
    copyBtn.classList.remove("hidden");
  } catch (err) {
    errorBanner.textContent = err.message;
    errorBanner.classList.remove("hidden");
  } finally {
    loadingText.classList.add("hidden");
  }
}
```

- [ ] **Step 4: Run the backend test suite to confirm nothing broke**

Run: `cd report-writer-app && .venv/Scripts/python -m pytest -v`
Expected: all previously-passing tests still pass (the `test_index_serves_html` test now checks the real page).

- [ ] **Step 5: Commit**

```bash
cd "/c/Users/delmastroa/OneDrive - Wesley College/Documents/App Dev/Pastoral Engine"
git add report-writer-app/static/index.html report-writer-app/static/style.css report-writer-app/static/script.js
git commit -m "feat: add Q&A frontend with chips, draft view, and Wesley styling"
```

---

### Task 8: Local smoke test without a real API key

**Files:**
- None created — this is a manual verification task using the app built in Tasks 1–7.

**Interfaces:**
- Consumes: `app.py` from Task 6.

- [ ] **Step 1: Run the full backend test suite one more time**

Run: `cd report-writer-app && .venv/Scripts/python -m pytest -v`
Expected: all tests pass (word_count, style_examples, prompts, openai_client, app — roughly 31 tests total).

- [ ] **Step 2: Start the server**

Run: `cd report-writer-app && .venv/Scripts/python app.py`
Expected: console shows `Running on http://127.0.0.1:5000`

- [ ] **Step 3: Confirm the page loads (in a second terminal)**

Run: `curl -s http://127.0.0.1:5000/ | head -c 200`
Expected: HTML starting with `<!DOCTYPE html>` and containing `Pastoral Report Writing Companion`

- [ ] **Step 4: Confirm validation errors work without needing an API key**

Run: `curl -s -X POST http://127.0.0.1:5000/api/generate -H "Content-Type: application/json" -d "{\"report_type\":\"tutor\",\"answers\":{}}"`
Expected: `{"error":"missing required answers: person, learner, participant"}` with HTTP 400

- [ ] **Step 5: Stop the server**

Stop the `python app.py` process (Ctrl+C in its terminal, or close the background task).

- [ ] **Step 6: Report status to the user**

No commit needed — this task is verification-only, nothing changes in the repo. Tell the user the backend and static frontend serve correctly, and that Task 9 needs their real OpenAI key before end-to-end generation can be tested.

---

### Task 9: End-to-end verification with a real OpenAI key

**Files:**
- None created — depends on the user creating `report-writer-app/.env` themselves (git-ignored, never pasted into chat).

**Interfaces:**
- Consumes: the full app from Tasks 1–7.

- [ ] **Step 1: Ask the user to create their local `.env`**

Tell the user: copy `report-writer-app/.env.example` to `report-writer-app/.env` and paste their real OpenAI API key into it. This file is git-ignored and never leaves their machine. Do not ask them to paste the key into the chat.

- [ ] **Step 2: Confirm the file exists (without reading its contents into the conversation)**

Run: `test -f report-writer-app/.env && echo "found"`
Expected: `found`

- [ ] **Step 3: Start the server**

Run: `cd report-writer-app && .venv/Scripts/python app.py`
Expected: console shows `Running on http://127.0.0.1:5000`

- [ ] **Step 4: Run one real generation for each report type**

Run:
```bash
curl -s -X POST http://127.0.0.1:5000/api/generate \
  -H "Content-Type: application/json" \
  -d "{\"report_type\":\"tutor\",\"answers\":{\"person\":\"resilient, quiet but warming up\",\"learner\":\"steady academic progress, asks good questions\",\"participant\":\"still settling in but contributing more each week\",\"summary\":\"enjoyed the recent House athletics carnival\"}}"
```
Expected: HTTP 200, JSON body with a `draft` field containing `[student name]`, a `word_count` roughly in the 100–150 range, and `target_range: [100, 150]`.

Run the same for `"report_type":"pyp"` with PYP-shaped answers and confirm `target_range: [180, 300]`.

- [ ] **Step 5: Confirm no identifying data appears in what was sent**

Review the `answers` payloads used in Step 4 by eye: confirm no real student name, DOB, or other identifier was included (they weren't — the test payloads only ever contained behaviour/learning descriptions).

- [ ] **Step 6: Open the app in a real browser and walk through it once, end to end**

Open `http://127.0.0.1:5000` in a browser. Pick Tutor Report, click through all four questions using chips and free text, click Generate, confirm the draft appears with a word count, try Regenerate, try Copy, try Start a new student, then repeat once for PYP Report.

- [ ] **Step 7: Stop the server**

Stop the `python app.py` process.

- [ ] **Step 8: Report status to the user**

No commit needed (nothing new to add — `.env` stays local and git-ignored). Summarise to the user: both report types generate drafts in range, the UI works end to end, and the tool is ready to use.
