import re

from agno.agent import Agent
from agno.db.postgres import PostgresDb

from app.agents.code_analyser_agent.models import AnaliseCodigoCompleta
from app.agents.code_analyser_agent.prompt import PROMPT_CODE_ANALYZER_AGENT
from app.core.config import settings
from app.llm.agno import get_default_agno_model


def get_code_analyser_prompt(
    *,
    student_message: str,
    student_code: str,
    detalhamento_level: str = 'medio',
    educational_focus: str = 'ambos',
    include_code_suggestions: bool = True,
    feedback_tone: str = 'encorajador',
    template: str = PROMPT_CODE_ANALYZER_AGENT,
) -> str:
    """
    Preenche o template do prompt usando regex - versão hardcoded

    Args:
            template: Template com variáveis {{}}
            student_message: Mensagem do aluno
            student_code: Código do aluno
            detalhamento_level: minimo, medio, maximo
            educational_focus: erros, melhorias, ambos
            feedback_language: pt-br, en, es
            include_code_suggestions: True/False
            feedback_tone: encorajador, neutro, direto

    Returns:
            Prompt com todas as variáveis preenchidas
    """

    # Converter boolean para string
    include_code_str = 'true' if include_code_suggestions else 'false'

    # Mapeamento das variáveis
    replacements = {
        r'\{\{detalhamento_level\}\}': detalhamento_level,
        r'\{\{educational_focus\}\}': educational_focus,
        r'\{\{include_code_suggestions\}\}': include_code_str,
        r'\{\{feedback_tone\}\}': feedback_tone,
        r'\{\{student_message\}\}': student_message,
        r'\{\{student_code\}\}': student_code,
    }

    # Aplicar substituições usando regex
    resultado = template
    for pattern, replacement in replacements.items():
        resultado = re.sub(pattern, replacement, resultado)

    return resultado


def get_code_analyser_agno_agent(session_id: str):
    return Agent(
        output_schema=AnaliseCodigoCompleta,
        model=get_default_agno_model(),
        markdown=True,
        db=PostgresDb(
            db_url=settings.sqlalchemy_db_uri, session_table='sessions'
        ),
        session_id=session_id,
    )


def call_code_analyser_agent(*, session_id: str, code: str, question: str):
    agent = get_code_analyser_agno_agent(session_id)

    return agent.run(
        get_code_analyser_prompt(student_message=question, student_code=code),
        stream=False,
    ).content
