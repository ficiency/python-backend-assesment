import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, delete

from app.database import create_tables, get_engine
from app.models import StoredPayload, TransformedWord
from app.payload_text import request_label
from app.store import find_payload, find_word, save_payload, save_word

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
        # Each test starts from an empty memory.
        db.exec(delete(StoredPayload))
        db.exec(delete(TransformedWord))
        db.commit()
        yield db


# A word saved once must be found again, so the outside service is not called twice.
def test_a_saved_word_can_be_found_again(session):
    save_word(session, "first string", "FIRST STRING")
    assert find_word(session, "first string") == "FIRST STRING"


# The same two lists must find the payload that was already stored.
def test_a_saved_payload_can_be_found_by_its_label(session):
    label = request_label(LIST_1, LIST_2)
    saved = save_payload(session, label, OUTPUT)
    found = find_payload(session, label)
    assert found is not None
    assert found.id == saved.id
    assert found.output == OUTPUT


# The same request must not create a second payload.
def test_the_same_label_cannot_be_stored_twice(session):
    label = request_label(LIST_1, LIST_2)
    save_payload(session, label, OUTPUT)
    with pytest.raises(IntegrityError):
        save_payload(session, label, OUTPUT)
    session.rollback()
