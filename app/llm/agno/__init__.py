from agno.models.google import Gemini

from app.core.config import settings


def get_default_agno_model():
    return Gemini(id='gemini-2.5-flash', api_key=settings.GEMINI_API_KEY)


def generate_stream(*, agent, input):
    for event in agent.run(input, stream=True):
        # Extract the content from the RunContentEvent
        if hasattr(event, 'content') and event.content:
            yield event.content
        elif hasattr(event, 'delta') and event.delta:
            yield event.delta
