from enum import Enum


class Features(Enum):
    CHATBOT = "chat"
    IMAGE_CAPTIONING = "caption"
    STT = "stt"


class LogLevel(Enum):
    CAPTION = "CAPTION"
    CHATBOT = "CH@"
    ERROR = "ERROR"
    INFO = "INFO"
    VOICE_ASSISTANT = ("VAST",)
    STT = "STT"


# Huggingface model documentation can be found by appending the model name to https://huggingface.co/
# Ex. https://huggingface.co/openai/whisper-large-v3-turbo
class Models(Enum):
    GPT2 = "gpt2"
    SUNO_BARK = "suno/bark"
    WHISPER_TINY_EN = "openai/whisper-tiny.en"
    WHISPER_LARGE_V3_TURBO = "openai/whisper-large-v3-turbo"


class PipelineFrameworks(Enum):
    PYTORCH = "pt"
    TENSORFLOW = "tf"


class Tasks(Enum):
    ASR = "automatic-speech-recognition"
    STT = "speech-to-text"
    TEXT_GENERATION = "text-generation"
    TTS = "text-to-speech"
