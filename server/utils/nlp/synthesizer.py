import base64
import io
import librosa
import numpy as np
import os
import scipy

from transformers import (
    AutoModelForSpeechSeq2Seq,
    AutoProcessor,
    AutoTokenizer,
    pipeline,
)
from transformers.pipelines.automatic_speech_recognition import (
    AutomaticSpeechRecognitionPipeline,
)

from utils.enums import LogLevel, Models, Tasks, PipelineFrameworks
from utils.logger import Logger

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
synthesizer = pipeline(Tasks.TTS.value, Models.SUNO_BARK.value)
Logger.log(LogLevel.INFO, "TTS pipeline loaded successfully.")

Logger.log(LogLevel.INFO, "Loading TTS tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    Models.WHISPER_LARGE_V3_TURBO.value, use_fast=True
)
Logger.log(LogLevel.INFO, "TTS tokenizer loaded successfully.")

Logger.log(LogLevel.INFO, "Creating ASR pipeline...")
asr_pipeline = AutomaticSpeechRecognitionPipeline(
    model=stt_model,
    feature_extractor=stt_processor,
    tokenizer=tokenizer,
    framework=PipelineFrameworks.PYTORCH.value,
    chunk_length_s=50,
    device=os.getenv("STT_COMPUTATION_DEVICE", -1),
)
Logger.log(LogLevel.INFO, "ASR pipeline initialized successfully.")


class Synthesizer:
    @staticmethod
    def generate_audio(transcript):
        Logger.log(LogLevel.INFO, f"Generating audio response...")

        # Generate audio using the pipeline
        audio_raw = synthesizer(transcript, forward_params={"do_sample": True})

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

    @staticmethod
    def transcribe_audio(data):
        # Check if audio_file_path is a path or already loaded audio data
        sample_rate, audio = data

        # If input audio is in stereo, normalize it to mono
        if audio.ndim == 2:
            audio = librosa.to_mono(audio)

        if stt_model is None:
            Logger.log(LogLevel.ERROR, "STT model failed to initialize.")
            raise ValueError(
                "STT model failed to initialize. Ensure the model path is correct and accessible."
            )

        if stt_processor is None:
            Logger.log(LogLevel.ERROR, "Processor failed to load.")
            raise ValueError(
                "Processor failed to load. Ensure the processor path is correct and accessible."
            )
        stt_processor.chunk_length = 1
        stt_processor.nb_max_frames = 3000
        stt_processor.sampling_rate = int(
            os.getenv("STT_SAMPLE_RATE", 16000)
        )  # Default to 16kHz if not set
        stt_processor.raw = audio

        result = asr_pipeline(audio)
        Logger.log(LogLevel.STT, result["text"])
        return result["text"]
