import io
import json
import numpy as np
import scipy

from flask import jsonify, send_file
from pydub import AudioSegment
from transformers import pipeline

from server.enums.logger import LogLevel
from server.enums.models import Models, Tasks

from faster_whisper import WhisperModel
model = WhisperModel(Models.FASTER_WHISPER.value)

from server.utils.logger import Logger
logger = Logger()

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def speech_to_text(request):
  logger.log(LogLevel.INFO, "Processing speech to text")
  logger.log(LogLevel.INFO, f"request {type(request)}, {len(request)}: {request[:25]}...")

  try:
    audio_buffer = io.BytesIO(request)
    audio = AudioSegment.from_file(audio_buffer, format="mp3")
    wav_buffer = io.BytesIO()
    audio.export(wav_buffer, format="wav")
    wav_buffer.seek(0)

    sampling_rate, audio_data = scipy.io.wavfile.read(wav_buffer)
    transcription = model.transcribe(audio_data, str(sampling_rate))

    return jsonify({"transcription": transcription})
  except Exception as e:
    logger.log(LogLevel.ERROR, f"Error processing speech to text, {e}")
    return jsonify({"error": str(e)}), 500

def text_to_speech(request, voice="default"):
  synthesizer = pipeline(Tasks.TTS.value, model="suno/bark")
  try:
    logger.log(LogLevel.INFO, "Processing text to speech")
    input = request.decode('utf-8')
    data = json.loads(input)

    # Convert the audio data to a numpy array
    synthesized_tts = synthesizer(data["userMessage"])

    # Extract and flatten the audio data
    audio_data = np.array(synthesized_tts["audio"], dtype=np.float32).flatten()
    
    # Normalize audio data to the range of int16
    wav = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)

    # Bytes obj to store audio data
    audio_buffer = io.BytesIO()
    scipy.io.wavfile.write(audio_buffer, rate=synthesized_tts["sampling_rate"], data=wav)

    # Move the buffer's pointer back to the beginning
    audio_buffer.seek(0)
    return send_file(audio_buffer, mimetype="audio/wav", as_attachment=False)

  except Exception as e:
    logger.log(LogLevel.ERROR, f"Error processing text to speech, {e}")
    return jsonify({"error": str(e)}), 500
  
# # TODO: Is paying for HuggingFace API worth it?
# HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
# TTS_INFERENCE_API = os.getenv("TTS_INFERENCE_API")
# def query_tts(data):
#   headers = {
#     "Authorization": f"Bearer {HUGGINGFACE_TOKEN}",
#   }
#   payload = {
#     "inputs": data["userMessage"],
#   }
#   response = requests.post(TTS_INFERENCE_API, headers=headers, json=payload)
#   logger.log(LogLevel.INFO, f"query_tts response: {response}")
#   return response.content
