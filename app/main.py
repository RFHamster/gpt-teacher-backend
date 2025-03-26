import asyncio

from app.core.deps import SessionDep
from app.llm.langchain import (
    langchain_make_question,
    langchain_make_question_stream,
)
from app.models.dto import RequestBodyQuestion
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
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


@app.get('/stream')
async def main():
    return StreamingResponse(fake_text_streamer(), media_type='text/plain')


@app.post('/call/')
def call(request_body: RequestBodyQuestion, session: SessionDep):
    return langchain_make_question(
        question=request_body.question, code=request_body.code
    )


@app.post('/call/stream/')
def call(request_body: RequestBodyQuestion, session: SessionDep):
    return StreamingResponse(
        langchain_make_question_stream(
            question=request_body.question, code=request_body.code
        ),
        media_type='text/plain',
    )
