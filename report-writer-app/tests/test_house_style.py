from house_style import apply_house_style, join_paragraphs, split_paragraphs


def style(text, original_text=None):
    corrected, _ = apply_house_style(text, original_text)
    return corrected


def test_tutor_as_a_title_takes_a_capital():
    text = "It has been a pleasure supporting Jane as her tutor this year."
    assert style(text) == "It has been a pleasure supporting Jane as her Tutor this year."


def test_tutor_already_capitalised_is_left_alone():
    text = "It has been a pleasure supporting Sam as her Tutor this year."
    assert style(text) == text


def test_two_reports_end_up_consistent():
    first = style("supporting Jane as her tutor this year")
    second = style("supporting Sam as her Tutor this year")
    assert "as her Tutor" in first
    assert "as her Tutor" in second


def test_tutor_as_a_verb_is_not_capitalised():
    text = "He tutors his peers patiently."
    assert style(text) == text


def test_tutor_group_is_two_capitalised_words():
    assert style("within her tutorial group") == "within her Tutor Group"
    assert style("within her tutor group") == "within her Tutor Group"


def test_semester_on_its_own_takes_a_small_s():
    text = "Over the course of the Semester she grew in confidence."
    assert style(text) == "Over the course of the semester she grew in confidence."


def test_numbered_semester_keeps_its_capital():
    text = "In Semester 1 he led the group, and in Semester 2 he mentored others."
    assert style(text) == text


def test_lowercase_numbered_semester_is_capitalised():
    assert style("during semester 2 she improved") == "during Semester 2 she improved"


def test_semester_starting_a_sentence_keeps_its_capital():
    text = "Semester reports are due soon. Semester marks were pleasing."
    assert style(text) == text


def test_event_names_do_not_get_asterisks():
    text = "She performed in the *Autumn Music Concert* with great poise."
    assert style(text) == "She performed in the Autumn Music Concert with great poise."


def test_unlisted_event_names_are_also_stripped():
    text = "He competed in the *House Swimming Carnival* and the *Year 9 Camp*."
    assert style(text) == "He competed in the House Swimming Carnival and the Year 9 Camp."


def test_book_titles_keep_their_asterisks():
    text = "Her essay on *To Kill a Mockingbird* was thoughtful."
    assert style(text) == text


def test_double_asterisks_collapse_to_one():
    assert style("her essay on **Macbeth** was strong") == "her essay on *Macbeth* was strong"


def test_quotation_marks_are_restored_when_swapped_for_asterisks():
    original = 'She sang in the "Autumn Music Concert" last term.'
    corrected = "She sang in the *Autumn Music Concert* last term."
    assert style(corrected, original) == original


def test_changes_explain_each_fix_in_plain_english():
    _, changes = apply_house_style("as her tutor in the Semester")
    reasons = " ".join(change["reason"] for change in changes)
    assert "capital T" in reasons
    assert "small s" in reasons


def test_no_changes_reported_for_clean_text():
    text = "In Semester 1, Jane supported her peers as her Tutor had encouraged."
    corrected, changes = apply_house_style(text)
    assert corrected == text
    assert changes == []


def test_split_and_join_paragraphs_round_trip():
    text = "First paragraph.\n\nSecond paragraph.\n\n\nThird paragraph."
    paragraphs = split_paragraphs(text)
    assert paragraphs == ["First paragraph.", "Second paragraph.", "Third paragraph."]
    assert join_paragraphs(paragraphs) == (
        "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    )


def test_empty_text_is_safe():
    assert apply_house_style("") == ("", [])
