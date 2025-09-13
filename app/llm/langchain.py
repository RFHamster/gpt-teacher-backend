from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from app.agents.teacher_agent import PROMPT_TEACHER_AGENT
from app.core.config import (
    GEMINI_2_0_FLASH,
    GOOGLE_CHAT_MODELS,
    LLM_PARAMETERS,
    NVIDIA_CHAT_MODELS,
    settings,
)


def load_nvidia_chat_model(model_name: str) -> ChatNVIDIA:
    return ChatNVIDIA(
        model=model_name,
        api_key=settings.NVIDIA_NIM_API_KEY,
        top_p=0.7,
        **LLM_PARAMETERS[model_name],
    )


def load_google_chat_model(model_name: str) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=settings.GEMINI_API_KEY,
        top_p=0.7,
        **LLM_PARAMETERS[model_name],
    )


def get_model_load_function(model_name: str):
    if model_name in NVIDIA_CHAT_MODELS:
        return load_nvidia_chat_model
    if model_name in GOOGLE_CHAT_MODELS:
        return load_google_chat_model
    else:
        raise ValueError(f'Invalid model name: "{model_name}"')


def init_llm_model(model_name: str):
    load_model = get_model_load_function(model_name)
    return load_model(model_name)


def langchain_make_question(
    *, question: str, code: str, model_name: str = GEMINI_2_0_FLASH
):
    llm = init_llm_model(model_name)
    prompt = PromptTemplate(
        template=PROMPT_TEACHER_AGENT,
        input_variables=['student_message', 'student_code', 'code_analysis'],
    )
    chain = prompt | llm | StrOutputParser()

    answer = chain.invoke(
        {
            'student_message': question,
            'student_code': code,
            'code_analysis': 'Sem analises',
        }
    )

    return answer


async def langchain_make_question_stream(
    *, question: str, code: str, model_name: str = GEMINI_2_0_FLASH
):
    llm = init_llm_model(model_name)
    prompt = PromptTemplate(
        template=PROMPT_TEACHER_AGENT,
        input_variables=['student_message', 'student_code', 'code_analysis'],
    )
    chain = prompt | llm | StrOutputParser()

    async for chunk in chain.astream(
        {
            'student_message': question,
            'student_code': code,
            'code_analysis': 'Sem analises',
        }
    ):
        yield chunk
