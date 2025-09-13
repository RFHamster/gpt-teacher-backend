import re

from agno.agent import Agent
from agno.db.postgres import PostgresDb

from app.agents.code_analyser_agent import AnaliseCodigoCompleta
from app.agents.teacher_agent.prompt import PROMPT_TEACHER_AGENT
from app.core.config import settings
from app.llm.agno import get_default_agno_model


def get_teacher_agent_prompt(
    *,
    student_message: str,
    student_code: str,
    code_analysis: AnaliseCodigoCompleta,
    template: str = PROMPT_TEACHER_AGENT,
) -> str:
    replacements = {
        r'\{\{student_message\}\}': student_message,
        r'\{\{student_code\}\}': student_code,
        r'\{\{code_analysis\}\}': str(code_analysis.model_dump()),
    }

    resultado = template
    for pattern, replacement in replacements.items():
        resultado = re.sub(pattern, replacement, resultado)

    return resultado


def get_teacher_agent_agno_agent(session_id: str):
    return Agent(
        markdown=True,
        model=get_default_agno_model(),
        db=PostgresDb(
            db_url=settings.sqlalchemy_db_uri, session_table='sessions'
        ),
        session_id=session_id,
    )


def call_teacher_agent_agent(
    *,
    session_id: str,
    code: str,
    question: str,
    code_analysis: AnaliseCodigoCompleta,
):
    agent = get_teacher_agent_agno_agent(session_id)

    return agent.run(
        get_teacher_agent_prompt(
            student_message=question,
            student_code=code,
            code_analysis=code_analysis,
        ),
        stream=False,
    ).content
