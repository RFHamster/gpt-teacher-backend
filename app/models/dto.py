from uuid import UUID

from pydantic import BaseModel


class RequestBodyQuestion(BaseModel):
    question: str
    code: str
    session_id: int | None = None
