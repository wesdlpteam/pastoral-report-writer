from unittest.mock import patch

from openai_client import StyleCheckStructureError
from style_checker import check_report_text

TWO_PARAGRAPHS = "Jane is kind and reliable.\n\nJane contributes to discussions."


@patch("style_checker.generate_style_check")
def test_paragraphs_are_passed_through(mock_generate):
    mock_generate.return_value = {
        "corrected_text": "Jane is kind and reliable.\n\nJane contributes to discussions.",
        "changes": [],
        "suggestions": [],
    }

    result = check_report_text(TWO_PARAGRAPHS)

    assert result["corrected_text"].count("\n\n") == 1
    _, kwargs = mock_generate.call_args
    assert kwargs["expected_paragraphs"] == 2


@patch("style_checker.generate_style_check")
def test_house_style_is_enforced_on_the_corrected_text(mock_generate):
    mock_generate.return_value = {
        "corrected_text": "Supporting Jane as her tutor in the Semester was a pleasure.",
        "changes": [],
        "suggestions": [],
    }

    result = check_report_text("Supporting Jane as her tutor in the Semester was a pleasure.")

    assert "as her Tutor" in result["corrected_text"]
    assert "in the semester" in result["corrected_text"]
    assert len(result["changes"]) == 2


@patch("style_checker.generate_style_check")
def test_lost_paragraphs_trigger_a_per_paragraph_recheck(mock_generate):
    def responses(system_prompt, user_prompt, expected_paragraphs=1):
        if expected_paragraphs == 2:
            raise StyleCheckStructureError("merged", suggestions=["Add theme 3."])
        paragraph = user_prompt.rsplit("\n\n", 1)[-1]
        return {"corrected_text": paragraph, "changes": [], "suggestions": []}

    mock_generate.side_effect = responses

    result = check_report_text(TWO_PARAGRAPHS)

    assert result["corrected_text"] == TWO_PARAGRAPHS
    assert result["suggestions"] == ["Add theme 3."]
    assert mock_generate.call_count == 3


@patch("style_checker.generate_style_check")
def test_fallback_collapses_a_stray_break_inside_one_paragraph(mock_generate):
    def responses(system_prompt, user_prompt, expected_paragraphs=1):
        if expected_paragraphs == 2:
            raise StyleCheckStructureError("merged")
        return {"corrected_text": "One line.\nSecond line.", "changes": []}

    mock_generate.side_effect = responses

    result = check_report_text(TWO_PARAGRAPHS)

    assert result["corrected_text"] == "One line. Second line.\n\nOne line. Second line."
