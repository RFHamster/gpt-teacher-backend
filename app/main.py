import asyncio
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

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

class QuestionRequest(BaseModel):
    """Modelo para requisições de perguntas sobre código"""
    session_id: Optional[str] = Field(
        default=None,
        description="ID da sessão (será criado automaticamente se não fornecido)",
    )
    question: str = Field(
        ...,
        description="Pergunta sobre o código",
    )
    code: str = Field(
        ...,
        description="Código a ser analisado",
    )


class StandardResponse(BaseModel):
    """Resposta padrão da API"""
    response: str = Field(..., description="Resposta gerada pela IA")
    session_id: Optional[str] = Field(None, description="ID da sessão")


class ErrorResponse(BaseModel):
    """Modelo de resposta de erro"""
    detail: str = Field(..., description="Descrição do erro")


app = FastAPI(
    title="Sistema de Ensino com IA",
    description="""
    ## API de Ensino Assistido por Inteligência Artificial

    Esta API fornece um sistema educacional que combina análise de código e feedback pedagógico 
    utilizando agentes especializados de IA.

    ### Características principais:
    - 🤖 **Agentes Especializados**: Code Analyser + Teacher Agent
    - 📊 **Análise de Código**: Feedback detalhado sobre qualidade e melhorias
    - 🎓 **Resposta Pedagógica**: Explicações educativas adaptadas ao nível do estudante
    - 🔄 **Streaming**: Respostas em tempo real
    - 💾 **Persistência**: Histórico de sessões e análises

    ### Fluxo de trabalho:
    1. Envie código + pergunta
    2. Sistema analisa o código
    3. Gera resposta pedagógica personalizada
    4. Retorna feedback em streaming
    """,
    version="1.0.0",
    contact={
        "name": "Equipe de Desenvolvimento",
        "email": "dev@exemplo.com",
    },
    license_info={
        "name": "MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=['X-Session-ID'],
)


async def fake_text_streamer():
    """Gerador de texto fake para testes de streaming"""
    messages = [
        'Olá! Como posso te ajudar?',
        'Estou aqui para responder suas perguntas.',
        'Você pode perguntar sobre qualquer coisa!',
        'Isso é um teste de streaming de texto...',
    ]
    for message in messages:
        yield message + '\n'
        await asyncio.sleep(1)


@app.post(
    '/fake_stream',
    summary="Teste de Streaming",
    description="Endpoint de teste que simula streaming de texto com mensagens pré-definidas em português",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "Stream de texto de teste",
            "content": {"text/plain": {"example": "Olá! Como posso te ajudar?\n"}},
            "headers": {
                "X-Session-ID": {
                    "description": "ID da sessão gerado automaticamente",
                    "schema": {"type": "string", "format": "uuid"}
                }
            }
        }
    },
    tags=["Teste"]
)
async def fake_stream_endpoint(request_body: QuestionRequest):
    """
    Endpoint para testar funcionalidade de streaming.

    Retorna uma sequência de mensagens pré-definidas com delay simulado,
    útil para testar a integração com clientes que consomem streaming.
    """
    print(f"Session ID recebido: {request_body.session_id}")
    response = StreamingResponse(fake_text_streamer(), media_type='text/plain')
    response.headers['X-Session-ID'] = str(uuid.uuid4())
    return response


@app.post(
    '/call/agno/',
    summary="Sistema Completo com Agentes",
    description="""
    Sistema completo que utiliza agentes especializados para análise de código e resposta pedagógica.

    **Fluxo de processamento:**
    1. Cria/recupera sessão do estudante
    2. Analisa o código com Code Analyser Agent
    3. Gera resposta pedagógica com Teacher Agent
    4. Persiste dados no banco
    5. Retorna resposta em streaming
    """,
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "Resposta pedagógica em streaming",
            "content": {"text/plain": {"example": "Analisando seu código...\nSua função está bem estruturada..."}},
            "headers": {
                "X-Session-ID": {
                    "description": "ID da sessão (criado automaticamente se não fornecido)",
                    "schema": {"type": "string", "format": "uuid"}
                }
            }
        },
        422: {"model": ErrorResponse, "description": "Erro de validação"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    },
    tags=["Agentes IA"]
)
async def call_agno_system(request_body: QuestionRequest, session: SessionDep):
    """
    Endpoint principal que utiliza o sistema completo de ensino com IA.

    **Características:**
    - 🔍 **Análise Especializada**: Code Analyser Agent avalia qualidade, bugs e melhorias
    - 🎓 **Feedback Pedagógico**: Teacher Agent fornece explicações educativas
    - 💾 **Persistência**: Mantém histórico de sessões e análises
    - 🔄 **Streaming**: Resposta em tempo real

    **Parâmetros:**
    - **question**: Sua pergunta específica sobre o código
    - **code**: Código para análise (Python, JavaScript, etc.)
    - **session_id**: Opcional - permite continuidade da conversa

    **Exemplo de uso:**
    ```python
    {
        "question": "Como posso otimizar esta função?",
        "code": "def fibonacci(n):\\n    if n <= 1:\\n        return n\\n    return fibonacci(n-1) + fibonacci(n-2)"
    }
    ```
    """
    try:
        # Cria nova sessão se não fornecida
        if not request_body.session_id:
            student_session = await create_student_session(db=session)
            request_body.session_id = student_session.id

        # Salva mensagem do estudante
        student_message = await create_student_message(
            StudentMessageCreate(
                session_id=int(request_body.session_id),
                code=request_body.code,
                message=request_body.question,
            ),
            session,
        )

        # Executa análise de código
        senior_analysis = call_code_analyser_agent(
            session_id=str(request_body.session_id),
            code=request_body.code,
            question=request_body.question,
        )

        # Salva análise no banco
        await create_code_analysis(
            CodeAnalysisCreate(
                message_id=student_message.id,
                analysis=senior_analysis.model_dump(),
            ),
            session,
        )

        # Gera resposta pedagógica
        teacher_message = call_teacher_agent_agent(
            session_id=str(request_body.session_id),
            code=request_body.code,
            question=request_body.question,
            code_analysis=senior_analysis,
        )

        # Salva resposta do professor
        await create_teacher_response(
            TeacherResponseCreate(
                message_id=student_message.id,
                response=teacher_message
            ),
            session,
        )

        def stream_response(teacher_message):
            """Gerador para streaming da resposta"""
            for chunk in teacher_message:
                yield chunk

        return StreamingResponse(
            stream_response(teacher_message),
            media_type='text/plain',
            headers={'X-Session-ID': str(request_body.session_id)},
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no sistema de agentes: {str(e)}"
        )


@app.post(
    '/call/langchain/',
    summary="LangChain com Streaming",
    description="Utiliza LangChain com capacidade de streaming para respostas em tempo real",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "Resposta LangChain em streaming",
            "content": {"text/plain": {"example": "Analisando código...\nSugestões de melhoria..."}},
            "headers": {
                "X-Session-ID": {
                    "description": "ID da sessão (gerado se não fornecido)",
                    "schema": {"type": "string", "format": "uuid"}
                }
            }
        },
        422: {"model": ErrorResponse, "description": "Erro de validação"},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor"}
    },
    tags=["LangChain"]
)
def call_langchain_stream(request_body: QuestionRequest, session: SessionDep):
    """
    Processa perguntas usando LangChain com streaming.

    **Vantagens do streaming:**
    - ⚡ Resposta mais rápida - receba conteúdo conforme é gerado
    - 💫 Melhor experiência do usuário - feedback visual imediato
    - 🔄 Ideal para respostas longas ou análises complexas

    **Quando usar:**
    - Análises detalhadas de código
    - Explicações passo-a-passo
    - Tutoriais ou documentação
    - Qualquer resposta que possa ser longa

    **Diferenças do sistema completo:**
    - Não utiliza agentes especializados
    - Não persiste dados no banco
    - Processamento mais rápido e direto
    """
    try:
        response = StreamingResponse(
            langchain_make_question_stream(
                question=request_body.question,
                code=request_body.code
            ),
            media_type='text/plain',
        )

        # Gera Session ID se não fornecido
        if not request_body.session_id:
            response.headers['X-Session-ID'] = str(uuid.uuid4())
        else:
            response.headers['X-Session-ID'] = request_body.session_id

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro no LangChain streaming: {str(e)}"
        )


@app.get(
    "/health",
    summary="Health Check",
    description="Verifica se a API está funcionando corretamente",
    response_model=dict,
    tags=["Sistema"]
)
def health_check():
    """
    Endpoint para verificação de saúde da API.

    Retorna informações básicas sobre o status do sistema.
    """
    return {
        "status": "healthy",
        "service": "Sistema de Ensino com IA",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)