from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.models import (
    CodeAnalysis,
    StudentMessage,
    StudentSession,
    TeacherResponse,
)


# Request models for creation
class StudentSessionCreate(BaseModel):
    student_id: Optional[int] = None


class StudentMessageCreate(BaseModel):
    session_id: int
    code: str
    message: str


class CodeAnalysisCreate(BaseModel):
    message_id: int
    analysis: Dict[str, Any]


class TeacherResponseCreate(BaseModel):
    message_id: int
    response: str


async def create_student_session(db: Session):
    """Create a new student session"""
    db_session = StudentSession(created_at=datetime.now())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


async def create_student_message(
    message_data: StudentMessageCreate, db: Session
):
    """Create a new student message"""
    # Verify session exists
    session_exists = db.get(StudentSession, message_data.session_id)
    if not session_exists:
        raise HTTPException(status_code=404, detail='Session not found')

    db_message = StudentMessage(
        session_id=message_data.session_id,
        code=message_data.code,
        message=message_data.message,
        created_at=datetime.now(),
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


async def create_code_analysis(analysis_data: CodeAnalysisCreate, db: Session):

    message_exists = db.get(StudentMessage, analysis_data.message_id)
    if not message_exists:
        raise HTTPException(status_code=404, detail='Message not found')

    db_analysis = CodeAnalysis(
        message_id=analysis_data.message_id,
        analysis=analysis_data.analysis,
        created_at=datetime.now(),
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)

    return db_analysis


async def create_teacher_response(
    response_data: TeacherResponseCreate, db: Session
):
    """Create a new teacher response"""
    # Verify message exists
    message_exists = db.get(StudentMessage, response_data.message_id)
    if not message_exists:
        raise HTTPException(status_code=404, detail='Message not found')

    db_response = TeacherResponse(
        message_id=response_data.message_id,
        response=response_data.response,
        created_at=datetime.now(),
    )
    db.add(db_response)
    db.commit()
    db.refresh(db_response)

    return db_response
