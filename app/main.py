# from app.core.deps import SessionDep
# from app.core.config import settings as s
import asyncio

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os headers
)

class RequestBody(BaseModel):
    text: str

@app.post('/', response_model=str)
async def ingest_process(
    request_body: RequestBody,
    # session: SessionDep,
) -> str:
    print(request_body.text)
    return request_body.text

async def fake_text_streamer():
    messages = [
        "Olá! Como posso te ajudar?",
        "Estou aqui para responder suas perguntas.",
        "Você pode perguntar sobre qualquer coisa!",
        "Isso é um teste de streaming de texto..."
    ]
    for message in messages:
        yield message + "\n"
        await asyncio.sleep(1)  # Simula um delay para o streaming

@app.get("/stream")
async def main():
    return StreamingResponse(fake_text_streamer(), media_type="text/plain")
