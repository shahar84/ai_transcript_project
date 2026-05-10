# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from pathlib import Path

# Load variables from .env into environment
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    REPLICATE_API_TOKEN: str
    TRANSCRIBE_MODEL: str = "vaibhavs10/incredibly-fast-whisper:3ab86df6c8f54c11309d4d1f930ac292bad43ace52d10c80d87eb258b3c9f79c"
    TTS_MODEL: str = "google/gemini-3.1-flash-tts"
    TTS_VOICE: str = "Kore"
    TTS_PROMPT: str = "Speak in an engaging, conversational podcast tone."
    TTS_LANGUAGE: str = "en-US"
    OPENAI_API_KEY: str | None = None
    # Tell Pydantic where to read from
    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding='utf-8')


# Create a single instance to import anywhere
settings = Settings()
