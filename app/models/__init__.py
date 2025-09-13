from datetime import datetime
from typing import Optional

from sqlmodel import JSON, Column, Field, SQLModel

from app.core.deps import engine

schema_name = 'gpt_teacher'


class StudentSession(SQLModel, table=True):
    """Student session model"""

    __tablename__ = 'student_session'
    __table_args__ = {'extend_existing': True, 'schema': schema_name}

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: Optional[int] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.now)


class StudentMessage(SQLModel, table=True):
    """Student message model"""

    __tablename__ = 'student_messages'
    __table_args__ = {'extend_existing': True, 'schema': schema_name}

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(
        foreign_key=f'{schema_name}.student_session.id', index=True
    )
    code: str
    message: str
    created_at: datetime = Field(default_factory=datetime.now)


class CodeAnalysis(SQLModel, table=True):
    """Code analysis model"""

    __tablename__ = 'code_analysis'
    __table_args__ = {'extend_existing': True, 'schema': schema_name}

    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: int = Field(
        foreign_key=f'{schema_name}.student_messages.id', index=True
    )
    analysis: dict = Field(sa_column=Column(JSON), default={})
    created_at: datetime = Field(default_factory=datetime.now)


class TeacherResponse(SQLModel, table=True):
    """Teacher response model"""

    __tablename__ = 'teacher_responses'
    __table_args__ = {'extend_existing': True, 'schema': schema_name}

    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: int = Field(
        foreign_key=f'{schema_name}.student_messages.id', index=True
    )
    response: str
    created_at: datetime = Field(default_factory=datetime.now)


if __name__ == '__main__':
    StudentSession.metadata.create_all(engine)
    StudentMessage.metadata.create_all(engine)
    CodeAnalysis.metadata.create_all(engine)
    TeacherResponse.metadata.create_all(engine)
