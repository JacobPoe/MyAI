from enum import Enum

class Features(Enum):
  CHATBOT = 'chat'
  IMAGE_CAPTIONING = 'caption'
  STT = 'stt'

class LogLevel(Enum):
  CAPTION = 'CAPTION'
  CHATBOT = 'CH@'
  ERROR = 'ERROR'
  INFO = 'INFO'
  VOICE_ASSISTANT = 'VAST',
  STT = 'STT'

class Models(Enum):
  SUNO_BARK = 'suno/bark'
  FASTER_WHISPER = 'large-v3'
  WHISPER_TINY_EN = 'openai/whisper-tiny.en'

class PipelineFrameworks(Enum):
  PYTORCH = 'pt'
  TENSORFLOW = 'tf'

class Tasks(Enum):
  STT = 'speech-to-text'
  TTS = 'text-to-speech'