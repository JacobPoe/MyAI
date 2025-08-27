import base64
import io
import nemo.collections.asr as nemo_asr
import numpy as np
import scipy

from transformers import (
    AutoTokenizer,
    pipeline,
)

from services.env import EnvService, EnvVars

from utils.nlp.enums import DeviceMap, Models, Tasks
from utils.logger import Logger, LogLevel

DEVICE_MAP = EnvService.get(EnvVars.DEVICE_MAP.value, DeviceMap.AUTO.value)


class Synthesizer:
    def __init__(self):
        self.asr_model = None

        self.tts_pipeline = None
        self.tts_tokenizer = None

    def transcribe_audio(self, data):
        """
        Wrapper for the asr_model.transcribe() method.
        Allows for other classes to use the same pipeline across all instances
        (param) data: The audio data to be transcribed
        """

        if self.asr_model is None:
            self.init_asr_pipeline()

        if isinstance(data, tuple):
            # Extract the audio data from the tuple or process accordingly
            audio_data = np.array(data[1] if data and len(data) > 1 else [], dtype=np.float32).flatten()
        else:
            audio_data = np.array(data, dtype=np.float32).flatten()

        return self.asr_model.transcribe(audio_data)

    def generate_audio(self, transcript):
        Logger.log(LogLevel.SYNTHESIZER, f"Generating audio response...")

        if self.tts_pipeline is None:
            self.init_tts_pipeline()

        # Generate audio using the pipeline
        audio_raw = self.tts_pipeline(transcript, forward_params={"do_sample": True})

        # Convert the generated audio to a numpy array
        audio_data = np.array(audio_raw["audio"], dtype=np.float32).flatten()

        # Normalize audio data to the range of int16
        wav = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)

        # Store audio data to a buffer
        audio_buffer = io.BytesIO()
        scipy.io.wavfile.write(audio_buffer, rate=audio_raw["sampling_rate"], data=wav)

        # Encode the audio buffer to base64
        audio_buffer.seek(0)
        Logger.log(LogLevel.SYNTHESIZER, f"Audio response generated.")
        return base64.b64encode(audio_buffer.read()).decode("utf-8")

    def init_asr_pipeline(self, device_map=DEVICE_MAP):
        try:
            Logger.log(LogLevel.SYNTHESIZER, "Initializing ASR model...")
            self.asr_model = nemo_asr.models.ASRModel.from_pretrained(
                model_name=Models.PARAKEET.value,
            )
            Logger.log(LogLevel.SYNTHESIZER, "ASR model initialized successfully.")
        except Exception as e:
            Logger.log(LogLevel.ERROR, f"ASR model failed to initialize, {e}")
            raise ValueError("ASR model failed to initialize.")

    def init_tts_pipeline(self, device_map=DEVICE_MAP):
        try:
            Logger.log(LogLevel.SYNTHESIZER, "Loading TTS pipeline...")
            self.tts_pipeline = pipeline(
                Tasks.TTS.value,
                Models.SUNO_BARK.value,
                device_map=device_map,
            )
            Logger.log(LogLevel.SYNTHESIZER, "TTS pipeline loaded successfully.")

            Logger.log(LogLevel.SYNTHESIZER, "Loading tokenizer...")
            self.tts_tokenizer = AutoTokenizer.from_pretrained(
                Models.SUNO_BARK.value,
                use_fast=True,
                device_map=device_map,
            )
            Logger.log(LogLevel.SYNTHESIZER, "TTS tokenizer loaded successfully.")
        except Exception as e:
            Logger.log(LogLevel.ERROR, "TTS pipeline failed to initialize.")
            raise ValueError("TTS pipeline failed to initialize.")
