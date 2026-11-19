"""Runs a style check and guarantees the teacher's paragraphs survive it.

One model call handles the whole comment. If that call merges or drops a
paragraph break, the text is checked again one paragraph at a time, which
cannot change the paragraph structure. Mechanical house-style rules are then
enforced in house_style.py.
"""

import logging

from house_style import apply_house_style, join_paragraphs, split_paragraphs
from openai_client import StyleCheckStructureError, generate_style_check
from prompts import (
    STYLE_CHECK_PARAGRAPH_SYSTEM_PROMPT,
    STYLE_CHECK_SYSTEM_PROMPT,
    build_style_check_paragraph_user_prompt,
    build_style_check_user_prompt,
)

logger = logging.getLogger(__name__)


def check_report_text(text: str) -> dict:
    paragraphs = split_paragraphs(text)

    try:
        result = generate_style_check(
            STYLE_CHECK_SYSTEM_PROMPT,
            build_style_check_user_prompt(text),
            expected_paragraphs=len(paragraphs),
        )
    except StyleCheckStructureError as exc:
        logger.warning("Style check lost paragraph breaks, rechecking per paragraph: %s", exc)
        result = _check_each_paragraph(paragraphs, exc.suggestions)

    corrected, style_changes = apply_house_style(result["corrected_text"], original_text=text)
    result["corrected_text"] = corrected
    result["changes"] = list(result.get("changes", [])) + style_changes
    return result


def _check_each_paragraph(paragraphs: list, suggestions: list) -> dict:
    corrected = []
    changes = []

    for paragraph in paragraphs:
        single = generate_style_check(
            STYLE_CHECK_PARAGRAPH_SYSTEM_PROMPT,
            build_style_check_paragraph_user_prompt(paragraph),
            expected_paragraphs=1,
        )
        # Collapse any stray line break so one paragraph in stays one out.
        corrected.append(" ".join(single["corrected_text"].split()))
        changes.extend(single["changes"])

    return {
        "corrected_text": join_paragraphs(corrected),
        "changes": changes,
        "suggestions": suggestions,
    }
