import base64
import io
import json
import librosa
import numpy as np
import os
import scipy
import torch

from flask import jsonify
from pydub import AudioSegment
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, AutoTokenizer, pipeline
from transformers.pipelines.automatic_speech_recognition import (
    AutomaticSpeechRecognitionPipeline,
)

from enums.enums import LogLevel, Models, Tasks, PipelineFrameworks
from logger.logger import Logger
from nlp.chatbot import Chatbot

Logger.log(LogLevel.INFO, "Initializing STT model...")
stt_model = AutoModelForSpeechSeq2Seq.from_pretrained(
    Models.WHISPER_TINY_EN.value
)
Logger.log(LogLevel.INFO, "STT model initialized successfully.")

Logger.log(LogLevel.INFO, "Loading STT pipeline...")
stt_pipeline = pipeline(
    Tasks.ASR.value,
    Models.WHISPER_LARGE_V3_TURBO.value,
    torch_dtype=torch.float32
)
Logger.log(LogLevel.INFO, "STT pipeline loaded successfully.")

Logger.log(LogLevel.INFO, "Loading STT processor...")
stt_processor = AutoProcessor.from_pretrained(
    Models.WHISPER_TINY_EN.value
)
Logger.log(LogLevel.INFO, "STT processor loaded successfully.")

Logger.log(LogLevel.INFO, "Loading TTS pipeline...")
synthesizer = pipeline(
    Tasks.TTS.value,
    Models.SUNO_BARK.value
)
Logger.log(LogLevel.INFO, "TTS pipeline loaded successfully.")

Logger.log(LogLevel.INFO, "Loading TTS tokenizer...")
tokenizer =  AutoTokenizer.from_pretrained(
    Models.WHISPER_TINY_EN.value, use_fast=True
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

class Translator:
    @staticmethod
    def generate_audio(transcript):
        Logger.log(LogLevel.INFO, f"Generating audio response...")

        # Generate audio using the pipeline
        audio_raw = synthesizer(transcript, forward_params={"do_sample": True})

        # Convert the generated audio to a numpy array
        audio_data = np.array(
            audio_raw["audio"], dtype=np.float32
        ).flatten()

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
        return base64.b64encode(audio_buffer.read()).decode('utf-8')


    @staticmethod
    def handle_audio_prompt(worker: Chatbot, request):
        Logger.log(LogLevel.INFO, "Processing audio prompt")

        request_audio = request.files.get("wav").read()
        audio_buffer = io.BytesIO(request_audio)
        wav_buffer = io.BytesIO()

        audio = AudioSegment.from_file(audio_buffer)
        audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0)

        # Read the audio data from the wav_buffer
        sampling_rate, audio_data = scipy.io.wavfile.read(wav_buffer)

        # Pass the audio data to the whisper pipeline
        transcription = stt_pipeline(audio_data)
        Logger.log(LogLevel.INFO, f"STT transcription: {transcription}")

        reply = worker.generate_reply(transcription["text"])
        Logger.log(LogLevel.INFO, f"Chatbot reply: {reply}")

        audio_base64 = None
        if request.form.get("requestAudioResponses"):
            audio_base64 = Translator.generate_audio(reply)

        return jsonify({"transcription": transcription, "reply": reply, "audio": audio_base64})


    @staticmethod
    def handle_text_prompt(worker: Chatbot, request):
        Logger.log(LogLevel.INFO, "Processing text prompt")

        # Decode the request
        decoded_request = request.data.decode("utf-8")
        data = json.loads(decoded_request)

        # Generate the reply and save it to the response
        transcript = worker.generate_reply(data["userMessage"])
        # Return no audio data unless requested
        audio_base64 = None

        # If the user requested an STT response
        if data["generateAudioResponses"]:
            audio_base64 = Translator.generate_audio(transcript)

        return transcript, audio_base64


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
