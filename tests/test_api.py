import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.database import create_tables, get_engine
from app.main import app
from app.models import StoredPayload, TransformedWord

LIST_1 = ["first string", "second string", "third string"]
LIST_2 = ["other string", "another string", "last string"]
OUTPUT = (
    "FIRST STRING, OTHER STRING, SECOND STRING, ANOTHER STRING, "
    "THIRD STRING, LAST STRING"
)


@pytest.fixture
def client():
    create_tables()
    with Session(get_engine()) as db:
        db.exec(delete(StoredPayload))
        db.exec(delete(TransformedWord))
        db.commit()
    with TestClient(app) as test_client:
        yield test_client


# The sample request is stored and can be read back by its id.
def test_post_then_get_returns_the_sample_output(client):
    created = client.post("/payload", json={"list_1": LIST_1, "list_2": LIST_2})
    assert created.status_code == 200
    body = created.json()
    assert body["message"] == "payload created"

    read = client.get(f"/payload/{body['id']}")
    assert read.status_code == 200
    assert read.json() == {"output": OUTPUT}


# The same lists return the id that was already stored.
def test_a_repeated_post_returns_the_same_id(client):
    first = client.post("/payload", json={"list_1": LIST_1, "list_2": LIST_2})
    second = client.post("/payload", json={"list_1": LIST_1, "list_2": LIST_2})

    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]
    assert second.json()["message"] == "payload already stored"


# Lists of different length are refused and nothing is created.
def test_lists_of_different_length_are_refused(client):
    response = client.post(
        "/payload",
        json={"list_1": ["one"], "list_2": ["two", "three"]},
    )
    assert response.status_code == 422


# An unknown id has nothing to read.
def test_an_unknown_id_is_not_found(client):
    response = client.get("/payload/missing-id")
    assert response.status_code == 404
