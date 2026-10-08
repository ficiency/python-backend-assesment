from collections.abc import Callable

from sqlmodel import Session

from app.payload_text import interleave, request_label, transform
from app.store import find_payload, find_word, save_payload, save_word


class PayloadResult:
    def __init__(self, payload_id: str, output: str, created: bool) -> None:
        self.id = payload_id
        self.output = output
        self.created = created


def create_payload(
    session: Session,
    list_1: list[str],
    list_2: list[str],
    transform_word: Callable[[str], str] = transform,
) -> PayloadResult:
    # Stop a bad request before any word is transformed or stored.
    if len(list_1) != len(list_2):
        raise ValueError("The two lists must have the same number of words")

    label = request_label(list_1, list_2)
    existing = find_payload(session, label)
    if existing is not None:
        return PayloadResult(existing.id, existing.output, created=False)

    first = [_stored_or_transformed(session, word, transform_word) for word in list_1]
    second = [_stored_or_transformed(session, word, transform_word) for word in list_2]
    output = interleave(first, second)
    saved = save_payload(session, label, output)
    return PayloadResult(saved.id, saved.output, created=True)


def _stored_or_transformed(
    session: Session,
    word: str,
    transform_word: Callable[[str], str],
) -> str:
    # A word already stored is reused, so the outside service is not called again.
    cached = find_word(session, word)
    if cached is not None:
        return cached

    result = transform_word(word)
    save_word(session, word, result)
    return result
