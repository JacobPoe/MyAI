import io
import scipy.io.wavfile as wav

from enum import Enum
from pydub import AudioSegment

from services.env import EnvService, EnvVars
from utils.logger import Logger, LogLevel

AUDIO_SAMPLE_RATE = EnvService.get_int(EnvVars.AUDIO_SAMPLE_RATE.value, 16000)
DEBUG = EnvService.is_debug()


class AudioFormat(Enum):
    WAV = "wav"
    WEBM = "webm"


class AudioService:
    @staticmethod
    def load_audio(raw_bytes):
        Logger.log(LogLevel.INFO, "Loading audio data from request...")

        if not raw_bytes or len(raw_bytes) == 0:
            Logger.log(LogLevel.ERROR, "Received empty audio data.")
            return None

        audio_buffer = io.BytesIO(raw_bytes)
        wav_buffer = io.BytesIO()

        audio_segment = AudioSegment.from_file(
            audio_buffer, format=AudioFormat.WEBM.value
        )
        audio_segment = audio_segment.set_frame_rate(AUDIO_SAMPLE_RATE).set_channels(1)
        audio_segment.export(wav_buffer, format=AudioFormat.WAV.value)
        wav_buffer.seek(0)

        if DEBUG:
            Logger.log(LogLevel.DEBUG, "Saving audio prompt to debug.wav")
            with open("debug.wav", "wb") as f:
                f.write(wav_buffer.getvalue())

        audio_data = wav.read(wav_buffer)
        Logger.log(LogLevel.INFO, "Audio data loaded successfully.")

        wav_buffer.close()
        return audio_data
