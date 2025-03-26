from app.core.config import settings
from langchain_community.chat_models import ChatOpenAI


class NvidiaChatModel(ChatOpenAI):
    def __init__(self, **kwargs):
        super().__init__(
            openai_api_key=settings.NVIDIA_LLAMA_NEMOTROM_3_3_API_KEY,
            openai_api_base='https://integrate.api.nvidia.com/v1',
            model_name=settings.NVIDIA_LLAMA_NEMOTROM_3_3_NAME,
            temperature=0.2,
            model_kwargs={
                'top_p': 0.7,
            },
            max_tokens=4096,
            streaming=True,
            **kwargs
        )
