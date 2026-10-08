import pytest
from sqlmodel import Session, delete

from app.database import create_tables, get_engine
from app.models import StoredPayload, TransformedWord
from app.payload_text import request_label
from app.service import create_payload
from app.store import find_payload, find_word

LIST_1 = ["first string", "second string", "third string"]
LIST_2 = ["other string", "another string", "last string"]
OUTPUT = (
    "FIRST STRING, OTHER STRING, SECOND STRING, ANOTHER STRING, "
    "THIRD STRING, LAST STRING"
)


@pytest.fixture
def session():
    create_tables()
    with Session(get_engine()) as db:
        db.exec(delete(StoredPayload))
        db.exec(delete(TransformedWord))
        db.commit()
        yield db


def counting_transform(calls: list[str]):
    def _transform(word: str) -> str:
        calls.append(word)
        return word.upper()

    return _transform


# The sample lists are stored once, with the mixed text from the task.
def test_a_new_request_stores_the_sample_output(session):
    calls: list[str] = []
    result = create_payload(session, LIST_1, LIST_2, counting_transform(calls))

    assert result.created is True
    assert result.output == OUTPUT
    assert calls == LIST_1 + LIST_2
    stored = find_payload(session, request_label(LIST_1, LIST_2))
    assert stored is not None
    assert stored.id == result.id


# The same lists return the id already stored and do not call the outside service.
def test_a_repeated_request_reuses_the_same_id(session):
    calls: list[str] = []
    transform_word = counting_transform(calls)
    first = create_payload(session, LIST_1, LIST_2, transform_word)
    second = create_payload(session, LIST_1, LIST_2, transform_word)

    assert second.id == first.id
    assert second.created is False
    assert second.output == OUTPUT
    assert len(calls) == 6


# A word seen in an earlier request is not sent to the outside service again.
def test_a_known_word_is_not_transformed_again(session):
    calls: list[str] = []
    transform_word = counting_transform(calls)
    create_payload(session, ["first string"], ["other string"], transform_word)
    calls.clear()

    result = create_payload(session, ["first string"], ["new string"], transform_word)

    assert result.created is True
    assert result.output == "FIRST STRING, NEW STRING"
    assert calls == ["new string"]


# Lists of different length are refused before anything is stored.
def test_lists_of_different_length_are_refused(session):
    calls: list[str] = []
    with pytest.raises(ValueError):
        create_payload(session, ["one"], ["two", "three"], counting_transform(calls))

    assert calls == []
    assert find_word(session, "one") is None
