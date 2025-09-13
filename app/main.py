import asyncio
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.agents.code_analyser_agent import call_code_analyser_agent
from app.agents.teacher_agent import call_teacher_agent_agent
from app.core.deps import SessionDep
from app.crud import (
    CodeAnalysisCreate,
    StudentMessageCreate,
    TeacherResponseCreate,
    create_code_analysis,
    create_student_message,
    create_student_session,
    create_teacher_response,
)
from app.llm.langchain import (
    langchain_make_question,
    langchain_make_question_stream,
)
from app.models.dto import RequestBodyQuestion

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=['X-Session-ID'],
)


async def fake_text_streamer():
    messages = [
        'Olá! Como posso te ajudar?',
        'Estou aqui para responder suas perguntas.',
        'Você pode perguntar sobre qualquer coisa!',
        'Isso é um teste de streaming de texto...',
    ]
    for message in messages:
        yield message + '\n'
        await asyncio.sleep(1)  # Simula um delay para o streaming


@app.post('/fake_stream')
async def main(request_body: RequestBodyQuestion):
    print(request_body.session_id)
    response = StreamingResponse(fake_text_streamer(), media_type='text/plain')
    response.headers['X-Session-ID'] = str(uuid.uuid4())
    return response


@app.post('/call/')
def call(request_body: RequestBodyQuestion, session: SessionDep):
    return langchain_make_question(
        question=request_body.question, code=request_body.code
    )


@app.post('/call/agno/')
async def call_agno(request_body: RequestBodyQuestion, session: SessionDep):
    if not request_body.session_id:
        student_session = await create_student_session(db=session)
        request_body.session_id = student_session.id

    student_message = await create_student_message(
        StudentMessageCreate(
            session_id=request_body.session_id,
            code=request_body.code,
            message=request_body.question,
        ),
        session,
    )

    senior_analysis = call_code_analyser_agent(
        session_id=str(request_body.session_id),
        code=request_body.code,
        question=request_body.question,
    )

    await create_code_analysis(
        CodeAnalysisCreate(
            message_id=student_message.id,
            analysis=senior_analysis.model_dump(),
        ),
        session,
    )

    teacher_message = call_teacher_agent_agent(
        session_id=str(request_body.session_id),
        code=request_body.code,
        question=request_body.question,
        code_analysis=senior_analysis,
    )

    await create_teacher_response(
        TeacherResponseCreate(
            message_id=student_message.id, response=teacher_message
        ),
        session,
    )

    def stream_response(teacher_message):
        for chunk in teacher_message:
            yield chunk

    return StreamingResponse(
        stream_response(teacher_message),
        media_type='text/plain',
        headers={'X-Session-ID': str(request_body.session_id)},
    )


@app.post('/call/langchain/')
def call(request_body: RequestBodyQuestion, session: SessionDep):
    response = StreamingResponse(
        langchain_make_question_stream(
            question=request_body.question, code=request_body.code
        ),
        media_type='text/plain',
    )
    if not request_body.session_id:
        response.headers['X-Session-ID'] = str(uuid.uuid4())
    return response
