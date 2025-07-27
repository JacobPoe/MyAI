import os

from dotenv import load_dotenv
from enum import Enum

# Load and configure environment variables
load_dotenv()
_DEBUG = os.getenv("DEBUG")
DEBUG = _DEBUG.lower() == "true" if _DEBUG else False


class EnvService:
    @staticmethod
    def get(key: str) -> str:
        return os.getenv(key)

    @staticmethod
    def is_debug() -> bool:
        return DEBUG

class EnvVars(Enum):
    DEBUG = "DEBUG"
    ROUTE_ASR = "ROUTE_ASR"
    ROUTE_TTS = "ROUTE_TTS"
    ROUTE_TRAINING = "ROUTE_TRAINING"
    SERVER_PORT = "SERVER_PORT"
    SERVER_HOST = "SERVER_HOST"
