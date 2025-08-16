import base64
import io
import numpy as np
import scipy
import torch

from transformers import (
    AutoModelForSpeechSeq2Seq,
    AutoTokenizer,
    pipeline,
)

from utils.nlp.enums import Models, Tasks
from utils.logger import Logger, LogLevel


class Synthesizer:
    def __init__(self):
        self.stt_model = None
        self.stt_pipeline = None

        self.tts_pipeline = None
        self.tts_tokenizer = None

    def stt_pipeline(self, data):
        """
        Wrapper for the stt_pipeline
        Allows for other classes to use the same pipeline across all instances
        (param) data: The audio data to be transcribed
        """
        if self.stt_pipeline is None:
            self.init_stt_pipeline()
        return self.stt_pipeline(data)

    def generate_audio(self, transcript):
        Logger.log(LogLevel.SYNTHESIZER, f"Generating audio response...")

        if self.tts_pipeline is None:
            self.init_tts_pipeline()

        # Generate audio using the pipeline
        audio_raw = self.tts_pipeline(
            transcript, forward_params={"do_sample": True}
        )

        # Convert the generated audio to a numpy array
        audio_data = np.array(audio_raw["audio"], dtype=np.float32).flatten()

        # Normalize audio data to the range of int16
        wav = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)

        # Store audio data to a buffer
        audio_buffer = io.BytesIO()
        scipy.io.wavfile.write(
            audio_buffer, rate=audio_raw["sampling_rate"], data=wav
        )

        # Encode the audio buffer to base64
        audio_buffer.seek(0)
        Logger.log(LogLevel.SYNTHESIZER, f"Audio response generated.")
        return base64.b64encode(audio_buffer.read()).decode("utf-8")

    def init_stt_pipeline(self):
        try:
            Logger.log(LogLevel.SYNTHESIZER, "Initializing STT model...")
            self.stt_model = AutoModelForSpeechSeq2Seq.from_pretrained(
                Models.WHISPER_LARGE_V3_TURBO.value
            )
            Logger.log(
                LogLevel.SYNTHESIZER, "STT model initialized successfully."
            )

            Logger.log(LogLevel.SYNTHESIZER, "Loading STT pipeline...")
            self.stt_pipeline = pipeline(
                Tasks.ASR.value,
                Models.WHISPER_LARGE_V3_TURBO.value,
                torch_dtype=torch.float32,
            )
            Logger.log(
                LogLevel.SYNTHESIZER, "STT pipeline loaded successfully."
            )
        except Exception as e:
            Logger.log(LogLevel.ERROR, "STT pipeline failed to initialize.")
            raise ValueError("STT pipeline failed to initialize.")

    def init_tts_pipeline(self):
        try:
            Logger.log(LogLevel.SYNTHESIZER, "Loading TTS pipeline...")
            self.tts_pipeline = pipeline(
                Tasks.TTS.value, Models.SUNO_BARK.value
            )
            Logger.log(
                LogLevel.SYNTHESIZER, "TTS pipeline loaded successfully."
            )

            Logger.log(LogLevel.SYNTHESIZER, "Loading tokenizer...")
            self.tts_tokenizer = AutoTokenizer.from_pretrained(
                Models.WHISPER_LARGE_V3_TURBO.value, use_fast=True
            )
            Logger.log(
                LogLevel.SYNTHESIZER, "TTS tokenizer loaded successfully."
            )
        except Exception as e:
            Logger.log(LogLevel.ERROR, "TTS pipeline failed to initialize.")
            raise ValueError("TTS pipeline failed to initialize.")
