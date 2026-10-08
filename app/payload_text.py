import hashlib
import json


def transform(text: str) -> str:
    # Stands in for the outside service. The sample shows each word in uppercase.
    return text.upper()


def interleave(list_1: list[str], list_2: list[str]) -> str:
    # One word from the first list, then one from the second, repeated until both end.
    if len(list_1) != len(list_2):
        raise ValueError("The two lists must have the same number of words")

    mixed: list[str] = []
    for left, right in zip(list_1, list_2):
        mixed.append(left)
        mixed.append(right)
    return ", ".join(mixed)


def request_label(list_1: list[str], list_2: list[str]) -> str:
    # Same lists in the same order always get the same label, so a repeated request can be recognized.
    raw = json.dumps(
        {"list_1": list_1, "list_2": list_2},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
