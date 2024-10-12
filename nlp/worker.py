import io
import json
import numpy as np
import scipy

from flask import jsonify, send_file
from transformers import pipeline

from enums.logger import LogLevel
from enums.model_types import ModelTypes

from utils.logger import Logger
logger = Logger()

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


def speech_to_text(audio_binary):
  return None

def text_to_speech(request, voice="default"):
  synthesizer = pipeline(ModelTypes.TTS.value, model="suno/bark")
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
