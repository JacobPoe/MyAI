from enum import Enum


class AudioRequestMode(Enum):
    QUESTION = "question"
    TRANSCRIBE = "transcribe"


# Huggingface datasets can be found at https://huggingface.co/datasets
# Ex. https://huggingface.co/datasets/MegaScience/MegaScience
class Dataset(Enum):
    GSM8K = "openai/gsm8k"


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


class TrainingRequestOpts(Enum):
    RESUME_FROM_CHECKPOINT = "resume_from_checkpoint"
