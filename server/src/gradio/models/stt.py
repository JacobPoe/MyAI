import librosa
import numpy as np
import os

from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, AutoTokenizer
from transformers.pipelines.automatic_speech_recognition import (
    AutomaticSpeechRecognitionPipeline,
)

from enums import Models, LogLevel, PipelineFrameworks
from logger import Logger


class STT:
    def callback(self, audio):
        return STT.transcribe_audio(audio)

    # TODO: Investigate methods to more efficiently normalize audio data
    @staticmethod
    def transcribe_audio(data):
        try:
            # Check if audio_file_path is a path or already loaded audio data
            sample_rate, audio = data

            # # Normalize audio_data to float32 for Whisper compatibility
            # if audio.dtype != np.float32:
            #     audio = (
            #         audio.astype(np.float32) / np.iinfo(audio.dtype).max
            #     )

            # If input audio is in stereo, normalize it to mono
            if audio.ndim == 2:
                audio = librosa.to_mono(audio)

            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                Models.WHISPER_TINY_EN.value
            )
            if model is None:
                Logger.log(LogLevel.ERROR, "Model failed to load.")
                raise ValueError(
                    "Model failed to load. Ensure the model path is correct and accessible."
                )

            processor = AutoProcessor.from_pretrained(
                Models.WHISPER_TINY_EN.value
            )
            if processor is None:
                Logger.log(LogLevel.ERROR, "Processor failed to load.")
                raise ValueError(
                    "Processor failed to load. Ensure the processor path is correct and accessible."
                )
            processor.chunk_length = 1
            processor.nb_max_frames = 3000
            processor.sampling_rate = int(os.getenv("STT_SAMPLE_RATE", 16000))  # Default to 16kHz if not set
            processor.raw = audio

            tokenizer = AutoTokenizer.from_pretrained(Models.WHISPER_TINY_EN.value, use_fast=True)
            pipe = AutomaticSpeechRecognitionPipeline(
                model=model,
                feature_extractor=processor,
                tokenizer=tokenizer,
                framework=PipelineFrameworks.PYTORCH.value,
                chunk_length_s=50,
                device=os.getenv('STT_COMPUTATION_DEVICE', -1)
            )

            result = pipe(audio)
            Logger.log(LogLevel.STT, result["text"])
            return result["text"]
        except Exception as e:
            Logger.log(LogLevel.ERROR, f"Error processing speech to text. {e}")
            return f"Error processing speech to text. {e}"
