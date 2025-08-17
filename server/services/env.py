import os

from dotenv import load_dotenv
from enum import Enum


class EnvVars(Enum):
    DEBUG = "DEBUG"
    DEFAULT_MODEL = "DEFAULT_MODEL"
    DEFAULT_TOKENIZER = "DEFAULT_TOKENIZER"
    MAX_LENGTH = "MAX_LENGTH"
    SELECTED_PRETRAINED_MODEL = "SELECTED_PRETRAINED_MODEL"
    PRETRAINED_MODEL_DIR = "PRETRAINED_MODEL_DIR"
    ROUTE_ASR = "ROUTE_ASR"
    ROUTE_IS_ALIVE = "ROUTE_IS_ALIVE"
    ROUTE_TTS = "ROUTE_TTS"
    ROUTE_TRAINING_INIT = "ROUTE_TRAINING_INIT"
    SERVER_PORT = "SERVER_PORT"
    SERVER_HOST = "SERVER_HOST"
    TRAINING_ARGS_NUM_EPOCHS = "TRAINING_ARGS_NUM_EPOCHS"


_DEBUG = os.getenv(EnvVars.DEBUG.value, "false").strip()
DEBUG = _DEBUG.lower() == "true" if _DEBUG else False


load_dotenv()


class EnvService:
    @staticmethod
    def get(key: str, default=None) -> str:
        assert (
            EnvVars(key) is not None
        ), f"Invalid environment variable key: {key}"

        value = os.getenv(key)
        if value is None:
            if default is not None:
                return default
            raise ValueError(f"Environment variable '{key}' not set.")
        return value.strip()

    @staticmethod
    def get_int(key: str) -> int | None:
        assert (
            EnvVars(key) is not None
        ), f"Invalid environment variable key: {key}"

        return int(os.getenv(key))

    @staticmethod
    def is_debug() -> bool:
        return DEBUG
