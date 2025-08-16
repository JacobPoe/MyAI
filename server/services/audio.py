import io
import scipy.io.wavfile as wav

from pydub import AudioSegment

from utils.logger import Logger, LogLevel


class AudioService:
    @staticmethod
    def load_audio(data, debug=False):
        Logger.log(LogLevel.INFO, "Loading audio data from request...")
        audio_buffer = io.BytesIO(data)
        wav_buffer = io.BytesIO()

        audio = AudioSegment.from_file(audio_buffer)
        audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0)

        if debug:
            Logger.log(LogLevel.DEBUG, "Saving audio data to debug.raw")
            with open("debug.raw", "wb") as f:
                f.write(audio_buffer.read())

        # Read the audio data from the wav_buffer
        sampling_rate, audio_data = wav.read(wav_buffer)
        Logger.log(LogLevel.INFO, "Audio data loaded successfully.")

        wav_buffer.close()
        return audio_data
