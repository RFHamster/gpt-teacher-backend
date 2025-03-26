from pydantic import BaseModel


class RequestBodyQuestion(BaseModel):
    question: str
    code: str
