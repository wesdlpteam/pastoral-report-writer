from prompts import (
    FOLLOWUP_SYSTEM_PROMPT,
    STYLE_CHECK_SYSTEM_PROMPT,
    build_followup_user_prompt,
    build_style_check_user_prompt,
    build_system_prompt,
    build_user_prompt,
)


def test_build_system_prompt_includes_wesley_grammar_style_rules():
    prompt = build_system_prompt("tutor")
    assert "First VI Volleyball" in prompt
    assert '"practise" is the verb' in prompt
    assert "James's work" in prompt
    assert "however" in prompt.lower() and "semicolon" in prompt
    assert "Spell out a term in full" in prompt
    assert "broadening" in prompt


def test_build_system_prompt_tutor_has_word_range():
    prompt = build_system_prompt("tutor")
    assert "100-150 words" in prompt


def test_build_system_prompt_includes_myp_subject_names():
    prompt = build_system_prompt("tutor")
    assert "Language and Literature" in prompt
    assert "Individuals and Societies" in prompt


def test_build_system_prompt_myp_note_shown_for_years_7_to_10():
    for year in ("7", "8", "9", "10"):
        prompt = build_system_prompt("tutor", year_level=year)
        assert "Learner Profile" in prompt
        assert "ATL" in prompt


def test_build_system_prompt_myp_note_hidden_for_years_11_12():
    for year in ("11", "12"):
        prompt = build_system_prompt("tutor", year_level=year)
        assert "Learner Profile" not in prompt


def test_build_system_prompt_myp_note_hidden_when_no_year_level():
    prompt = build_system_prompt("tutor")
    assert "Learner Profile" not in prompt


def test_build_system_prompt_theme_four_is_broad_summarising_comment():
    prompt = build_system_prompt("tutor")
    assert "summarising comment" in prompt
    assert "Student Reflection Rubric" in prompt
    assert "Education Outdoors" in prompt
    assert "goals or next steps for development" not in prompt


def test_build_system_prompt_includes_digital_tool_formatting():
    prompt = build_system_prompt("tutor")
    assert "PowerPoint" in prompt
    assert "Microsoft Word" in prompt
    assert "Paint Shop Pro" in prompt
    assert "generalise it away" in prompt


def test_build_system_prompt_includes_title_italics_convention():
    prompt = build_system_prompt("tutor")
    assert "*To Kill a Mockingbird*" in prompt


def test_build_system_prompt_theme_three_is_tutor_group_participation():
    prompt = build_system_prompt("tutor")
    assert "participant in the Tutor Group" in prompt
    assert "achievements, participation, leadership" not in prompt


def test_build_system_prompt_includes_title_formatting_rules():
    prompt = build_system_prompt("tutor")
    assert "Units 3 & 4" in prompt
    assert "Years 7 & 8" in prompt
    assert "Senior School" in prompt and "not \"SS\"" in prompt
    assert "class members" in prompt
    assert "Principal's Honour Roll" in prompt


def test_build_system_prompt_tutor_includes_examples():
    prompt = build_system_prompt("tutor")
    assert "Example 1:" in prompt


def test_build_system_prompt_includes_name_formatting_guide():
    prompt = build_system_prompt("tutor")
    assert "NAME FORMATTING" in prompt
    assert "Orson (Sonny)" in prompt
    assert "Do not swap back and forth" in prompt


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


def test_build_user_prompt_includes_formal_and_preferred_name():
    prompt = build_user_prompt(
        "tutor", {"person": "kind"}, formal_name="Jane Test", preferred_name="Janie"
    )
    assert "Formal name: Jane Test" in prompt
    assert "Preferred name: Janie" in prompt


def test_build_user_prompt_shows_no_preferred_name_when_none_given():
    prompt = build_user_prompt("tutor", {"person": "kind"}, formal_name="Jane Test")
    assert "Formal name: Jane Test" in prompt
    assert "Preferred name: (none given)" in prompt


def test_system_prompt_forbids_inventing_content_even_for_word_count():
    prompt = build_system_prompt("tutor")
    assert "never" in prompt.lower() or "must" in prompt.lower()
    assert "invent" in prompt.lower()


def test_followup_system_prompt_requires_json_response():
    assert "json" in FOLLOWUP_SYSTEM_PROMPT.lower()
    assert "question" in FOLLOWUP_SYSTEM_PROMPT.lower()


def test_followup_system_prompt_targets_student_not_teacher():
    lower = FOLLOWUP_SYSTEM_PROMPT.lower()
    assert "about the student" in lower
    assert "never" in lower and "teacher" in lower


def test_build_followup_user_prompt_includes_label_and_answer():
    prompt = build_followup_user_prompt("The student as a person", "resilient and kind")
    assert "The student as a person" in prompt
    assert "resilient and kind" in prompt


def test_build_followup_user_prompt_includes_pronouns():
    prompt = build_followup_user_prompt("The student as a person", "resilient", pronouns="she/her")
    assert "she/her" in prompt


def test_style_check_system_prompt_requires_json_response():
    lower = STYLE_CHECK_SYSTEM_PROMPT.lower()
    assert "json" in lower
    assert "corrected_text" in lower
    assert "changes" in lower


def test_style_check_system_prompt_forbids_changing_meaning():
    lower = STYLE_CHECK_SYSTEM_PROMPT.lower()
    assert "never" in lower
    assert "change the meaning" in lower or "meaning" in lower


def test_style_check_system_prompt_includes_wesley_style_rules():
    assert "First VI Volleyball" in STYLE_CHECK_SYSTEM_PROMPT
    assert '"practise" is the verb' in STYLE_CHECK_SYSTEM_PROMPT


def test_style_check_system_prompt_leaves_names_alone():
    assert "leave any" in STYLE_CHECK_SYSTEM_PROMPT.lower()
    assert "names exactly as given" in STYLE_CHECK_SYSTEM_PROMPT.lower()


def test_style_check_system_prompt_requests_theme_coverage_suggestions():
    lower = STYLE_CHECK_SYSTEM_PROMPT.lower()
    assert "suggestions" in lower
    assert "four themes" in lower
    assert "tutor group" in lower
    assert "never invent a" in lower


def test_build_style_check_user_prompt_includes_text():
    prompt = build_style_check_user_prompt("This is the report text.")
    assert "This is the report text." in prompt
