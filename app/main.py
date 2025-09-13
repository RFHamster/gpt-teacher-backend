import asyncio
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.agents.code_analyser_agent import call_code_analyser_agent
from app.agents.teacher_agent import call_teacher_agent_agent
from app.core.config import settings
from app.core.deps import SessionDep
from app.llm.agno import generate_stream, get_default_agno_model
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


@app.post('/stream')
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
def call_agno(request_body: RequestBodyQuestion, session: SessionDep):
    if not request_body.session_id:
        request_body.session_id = str(uuid.uuid4())
    print("teste")
    senior_analysis = call_code_analyser_agent(
        session_id=request_body.session_id,
        code=request_body.code,
        question=request_body.question,
    )
    print("teste")
    teacher_message = call_teacher_agent_agent(
        session_id=request_body.session_id,
        code=request_body.code,
        question=request_body.question,
        code_analysis=senior_analysis,
    )
    print("teste")
    def stream_response(teacher_message):
        for chunk in teacher_message:
            yield chunk

    return StreamingResponse(
        stream_response(teacher_message),
        media_type="text/plain",
        headers={"X-Session-ID": request_body.session_id}
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
