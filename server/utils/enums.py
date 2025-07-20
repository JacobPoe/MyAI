from enum import Enum

class AudioRequestMode(Enum):
    QUESTION = "question"
    TRANSCRIBE = "transcribe"

class LogLevel(Enum):
    CAPTION = "CAPTION"
    CHATBOT = "CH@"
    ERROR = "ERROR"
    INFO = "INFO"
    SYNTHESIZER = "SYNTHESIZER"


# Huggingface model documentation can be found by appending the model name to https://huggingface.co/
# Ex. https://huggingface.co/openai/whisper-large-v3-turbo
class Models(Enum):
    GPT2 = "gpt2"
    SUNO_BARK = "suno/bark"
    WHISPER_LARGE_V3_TURBO = "openai/whisper-large-v3-turbo"


class PipelineFrameworks(Enum):
    PYTORCH = "pt"


class Tasks(Enum):
    ASR = "automatic-speech-recognition"
    TEXT_GENERATION = "text-generation"
    TTS = "text-to-speech"
