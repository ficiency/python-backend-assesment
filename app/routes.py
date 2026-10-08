from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.database import get_session
from app.service import create_payload
from app.store import find_payload_by_id

router = APIRouter()


class PayloadRequest(BaseModel):
    list_1: list[str]
    list_2: list[str]


class PayloadCreated(BaseModel):
    id: str
    message: str


class PayloadOutput(BaseModel):
    output: str


@router.post("/payload", response_model=PayloadCreated)
def post_payload(body: PayloadRequest, session: Session = Depends(get_session)):
    try:
        result = create_payload(session, body.list_1, body.list_2)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    if result.created:
        return PayloadCreated(id=result.id, message="payload created")
    return PayloadCreated(id=result.id, message="payload already stored")


@router.get("/payload/{payload_id}", response_model=PayloadOutput)
def get_payload(payload_id: str, session: Session = Depends(get_session)):
    row = find_payload_by_id(session, payload_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Payload not found")
    return PayloadOutput(output=row.output)
