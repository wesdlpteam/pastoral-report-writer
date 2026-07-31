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
