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

    try:
        request_audio = request.files.get("wav").read()
        audio_buffer = io.BytesIO(request_audio)
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

        reply = worker.generate_reply(transcription["text"])
        Logger.log(LogLevel.INFO, f"Chatbot reply: {reply}")

        audio_base64 = None
        if request.form.get("requestAudioResponses"):
            audio_base64 = generate_audio_response(reply)

        return jsonify({"transcription": transcription, "reply": reply, "audio": audio_base64})

    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing audio prompt, {e}")
        return jsonify({"error": str(e)}), 500


def handle_text_prompt(worker: Chatbot, request):
    Logger.log(LogLevel.INFO, "Processing text prompt")
    try:
        # Decode the request
        decoded_request = request.data.decode("utf-8")
        data = json.loads(decoded_request)

        # Generate the reply and save it to the response
        transcript = worker.generate_reply(data["userMessage"])
        # Return no audio data unless requested
        audio_base64 = None

        # If the user requested an STT response
        if data["generateAudioResponses"]:
            audio_base64 = generate_audio_response(transcript)

        return transcript, audio_base64

    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing text prompt, {e}")
        return jsonify({"error": str(e)}), 500


def generate_audio_response(transcript):
    Logger.log(LogLevel.INFO, f"Generating audio response...")

    # Initialize the TTS pipeline
    synthesizer = pipeline(Tasks.TTS.value, model="suno/bark")

    # Generate the audio response
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
    Logger.log(LogLevel.INFO, f"Audio response generated.")
    return base64.b64encode(audio_buffer.read()).decode('utf-8')