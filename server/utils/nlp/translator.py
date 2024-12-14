import base64
import io
import json
import numpy as np
import scipy
import torch

from flask import jsonify, send_file
from pydub import AudioSegment
from transformers import pipeline

from enums import LogLevel, Tasks
from logger import Logger

from nlp.chatbot import Chatbot

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


def handle_audio_prompt(worker: Chatbot, request):
    Logger.log(LogLevel.INFO, "Processing audio prompt")
    Logger.log(
        LogLevel.INFO,
        f"request {type(request)}, {len(request)}: {request[:25]}...",
    )

    try:
        audio_buffer = io.BytesIO(request)
        wav_buffer = io.BytesIO()

        audio = AudioSegment.from_file(audio_buffer)
        audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0)

        # Read the audio data from the wav_buffer
        sampling_rate, audio_data = scipy.io.wavfile.read(wav_buffer)

        whisper = pipeline(
            "automatic-speech-recognition",
            "openai/whisper-large-v3",
            torch_dtype=torch.float32
        )

        # Pass the audio data to the whisper pipeline
        transcription = whisper(audio_data)
        Logger.log(LogLevel.INFO, f"STT transcription: {transcription}")
        return jsonify(transcription)
    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing audio prompt, {e}")
        return jsonify({"error": str(e)}), 500


def handle_text_prompt(worker: Chatbot, request):
    Logger.log(LogLevel.INFO, "Processing text prompt")
    try:
        # Initialize the TTS pipeline
        synthesizer = pipeline(Tasks.TTS.value, model="suno/bark")

        # Decode the request and extract the user message
        decoded_request = request.decode("utf-8")
        data = json.loads(decoded_request)

        # Generate the audio response
        transcript = worker.generate_reply(data["userMessage"])
        audio_raw = synthesizer(transcript)
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
        audio_base64 = base64.b64encode(audio_buffer.read()).decode('utf-8')

        return transcript, audio_base64

    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing text prompt, {e}")
        return jsonify({"error": str(e)}), 500
