import base64
import io
import numpy as np
import scipy
import torch

from transformers import (
    AutoModelForSpeechSeq2Seq,
    AutoProcessor,
    AutoTokenizer,
    pipeline,
)

from utils.nlp.enums import Models, Tasks
from utils.logger import Logger, LogLevel

Logger.log(LogLevel.INFO, "Initializing STT model...")
stt_model = AutoModelForSpeechSeq2Seq.from_pretrained(
    Models.WHISPER_LARGE_V3_TURBO.value
)
Logger.log(LogLevel.INFO, "STT model initialized successfully.")

Logger.log(LogLevel.INFO, "Loading STT processor...")
stt_processor = AutoProcessor.from_pretrained(
    Models.WHISPER_LARGE_V3_TURBO.value
)
Logger.log(LogLevel.INFO, "STT processor loaded successfully.")

Logger.log(LogLevel.INFO, "Loading TTS pipeline...")
tts_pipeline = pipeline(Tasks.TTS.value, Models.SUNO_BARK.value)
Logger.log(LogLevel.INFO, "TTS pipeline loaded successfully.")

Logger.log(LogLevel.INFO, "Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    Models.WHISPER_LARGE_V3_TURBO.value, use_fast=True
)
Logger.log(LogLevel.INFO, "TTS tokenizer loaded successfully.")

Logger.log(LogLevel.INFO, "Loading STT pipeline...")
stt_pipeline = pipeline(
    Tasks.ASR.value,
    Models.WHISPER_LARGE_V3_TURBO.value,
    torch_dtype=torch.float32,
)
Logger.log(LogLevel.INFO, "STT pipeline loaded successfully.")


class Synthesizer:
    # Wrapper for the stt_pipeline
    # Allows for other classes to use the same pipeline across all instances
    # (param) data: The audio data to be transcribed
    @staticmethod
    def stt_pipeline(data):
        if stt_pipeline is None:
            Logger.log(LogLevel.ERROR, "STT pipeline failed to initialize.")
            raise ValueError(
                "STT pipeline failed to initialize. Ensure the model path is correct and accessible."
            )
        return stt_pipeline(data)

    @staticmethod
    def generate_audio(transcript):
        Logger.log(LogLevel.INFO, f"Generating audio response...")

        # Generate audio using the pipeline
        audio_raw = tts_pipeline(transcript, forward_params={"do_sample": True})

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
        Logger.log(LogLevel.INFO, f"Audio response generated.")
        return base64.b64encode(audio_buffer.read()).decode("utf-8")
