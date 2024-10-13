from enum import Enum

class Models(Enum):
  SUNO_BARK = 'suno/bark'
  FASTER_WHISPER = 'large-v3'

class Tasks(Enum):
  STT = 'speech-to-text'
  TTS = 'text-to-speech'
