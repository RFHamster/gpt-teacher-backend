from dotenv import load_dotenv
from pydantic import PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

LLM_LLAMA_33_70B_INSTRUCT: str = 'meta/llama-3.3-70b-instruct'
GEMINI_2_0_FLASH: str = 'gemini-2.0-flash'

LLM_PARAMETERS = {
    LLM_LLAMA_33_70B_INSTRUCT: {
        'max_tokens': 5000,
        'temperature': 0.3,
        'context_length': 120000,
    },
    GEMINI_2_0_FLASH: {
        'max_tokens': 12000,
        'temperature': 0.3,
        'context_length': 500000,
    },
}

NVIDIA_CHAT_MODELS = [LLM_LLAMA_33_70B_INSTRUCT]
GOOGLE_CHAT_MODELS = [GEMINI_2_0_FLASH]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_ignore_empty=True,
        extra='ignore',
    )

    POSTGRES_SERVER: str = ''
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = 'postgres'
    POSTGRES_USER: str = ''
    POSTGRES_PASSWORD: str = ''

    @computed_field
    @property
    def sqlalchemy_db_uri(self) -> str:
        return f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

    NVIDIA_NIM_API_KEY: str = ''
    GEMINI_API_KEY: str = ''


settings = Settings()
