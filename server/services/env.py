import os

from dotenv import load_dotenv
from enum import Enum

# Load and configure environment variables
load_dotenv()
_DEBUG = os.getenv("DEBUG")
DEBUG = _DEBUG.lower() == "true" if _DEBUG else False


class EnvService:
    @staticmethod
    def get(key: str) -> str | None:
        assert (
            EnvVars(key) is not None
        ), f"Invalid environment variable key: {key}"

        return os.getenv(key)

    @staticmethod
    def get_int(key: str) -> int | None:
        assert (
            EnvVars(key) is not None
        ), f"Invalid environment variable key: {key}"

        return int(os.getenv(key))

    @staticmethod
    def is_debug() -> bool:
        return DEBUG


class EnvVars(Enum):
    DEBUG = "DEBUG"
    MAX_LENGTH = "MAX_LENGTH"
    SELECTED_PRETRAINED_MODEL = "SELECTED_PRETRAINED_MODEL"
    PRETRAINED_MODEL_DIR = "PRETRAINED_MODEL_DIR"
    ROUTE_ASR = "ROUTE_ASR"
    ROUTE_TTS = "ROUTE_TTS"
    ROUTE_TRAINING_INIT = "ROUTE_TRAINING_INIT"
    SERVER_PORT = "SERVER_PORT"
    SERVER_HOST = "SERVER_HOST"
    TRAINING_ARGS_NUM_EPOCHS = "TRAINING_ARGS_NUM_EPOCHS"
