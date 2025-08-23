import os

from dotenv import load_dotenv
from enum import Enum

load_dotenv()


class EnvVars(Enum):
    DEBUG = "DEBUG"
    DEFAULT_MODEL = "DEFAULT_MODEL"
    DEVICE_MAP = "DEVICE_MAP"
    MAX_NEW_TOKENS = "MAX_NEW_TOKENS"
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


class EnvService:
    @staticmethod
    def get(key: str, default: str = None) -> str:
        assert (
            EnvVars(key) is not None
        ), f"Invalid environment variable key: {key}"

        value = os.getenv(key).strip()
        if value is None or value == "":
            if default is not None:
                return default
            raise ValueError(f"Environment variable '{key}' not set.")
        return value

    @staticmethod
    def get_int(key: str, default: int = None) -> int:
        assert (
            EnvVars(key) is not None
        ), f"Invalid environment variable key: {key}"

        value = os.getenv(key).strip()
        if value is None or value == "":
            if default is not None:
                return default
            raise ValueError(f"Environment variable '{key}' not set.")
        return int(os.getenv(key))

    @staticmethod
    def is_debug() -> bool:
        return DEBUG
