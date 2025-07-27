import os

from dotenv import load_dotenv

# Load and configure environment variables
load_dotenv()
_DEBUG = os.getenv("DEBUG")
DEBUG = _DEBUG.lower() == "true" if _DEBUG else False
ROUTE_ASR = os.getenv("ROUTE_ASR", "/api/v1/asr")
ROUTE_TTS = os.getenv("ROUTE_TTS", "/api/v1/tts")
ROUTE_TRAINING = os.getenv("ROUTE_TRAINING", "/api/v1/training")
SERVER_PORT = os.getenv("SERVER_PORT", 5000)
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")


class EnvService:
    @staticmethod
    def get_debug():
        return DEBUG

    @staticmethod
    def get_route_asr():
        return ROUTE_ASR

    @staticmethod
    def get_route_tts():
        return ROUTE_TTS

    @staticmethod
    def get_route_training():
        return ROUTE_TRAINING

    @staticmethod
    def get_server_port():
        return SERVER_PORT

    @staticmethod
    def get_server_host():
        return SERVER_HOST
