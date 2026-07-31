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
