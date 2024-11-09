from enum import Enum

class Features(Enum):
  CHATBOT = 'chat'
  IMAGE_CAPTIONING = 'caption'

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

class Tasks(Enum):
  STT = 'speech-to-text'
  TTS = 'text-to-speech'