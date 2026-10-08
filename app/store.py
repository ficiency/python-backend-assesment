from uuid import uuid4

from sqlmodel import Session, select

from app.models import StoredPayload, TransformedWord


def save_word(session: Session, word: str, result: str) -> None:
    session.add(TransformedWord(word=word, result=result))
    session.commit()


def find_word(session: Session, word: str) -> str | None:
    row = session.get(TransformedWord, word)
    if row is None:
        return None
    return row.result


def save_payload(session: Session, label: str, output: str) -> StoredPayload:
    payload = StoredPayload(id=str(uuid4()), label=label, output=output)
    session.add(payload)
    session.commit()
    session.refresh(payload)
    return payload


def find_payload(session: Session, label: str) -> StoredPayload | None:
    statement = select(StoredPayload).where(StoredPayload.label == label)
    return session.exec(statement).first()
