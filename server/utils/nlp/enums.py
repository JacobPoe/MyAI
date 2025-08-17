from enum import Enum


class AudioRequestMode(Enum):
    QUESTION = "question"
    TRANSCRIBE = "transcribe"


class ConfigType(Enum):
    AGENT = "agent"
    MODEL = "model"


class DeviceMap(Enum):
    AUTO = "auto"
    CPU = "cpu"
    CUDA = "cuda"


# Huggingface model documentation can be found by appending the model name to https://huggingface.co/
# Ex. https://huggingface.co/openai/whisper-large-v3-turbo
class Models(Enum):
    GPT2 = "gpt2"
    QWEN3 = "Qwen/Qwen3-235B-A22B-Thinking-2507-FP8"
    SUNO_BARK = "suno/bark"
    WHISPER_LARGE_V3_TURBO = "openai/whisper-large-v3-turbo"


class PipelineFrameworks(Enum):
    PYTORCH = "pt"


class Roles(Enum):
    AGENT = "agent"
    USER = "user"


class Tasks(Enum):
    ASR = "automatic-speech-recognition"
    TEXT_GENERATION = "text-generation"
    TTS = "text-to-speech"
