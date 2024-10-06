import json
import numpy as np
import os
import scipy
from flask import jsonify, send_file
import soundfile as sf

from requests import request
from transformers import pipeline

from enums.logger import LogLevel
from enums.model_types import ModelTypes

from utils.logger import Logger
logger = Logger()

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
MODEL_TTS = os.getenv("MODEL_TTS")

def speech_to_text(audio_binary):
  return None

def text_to_speech(request, voice="default"):
  synthesizer = pipeline(ModelTypes.TTS.value, model="suno/bark")
  try:
    logger.log(LogLevel.INFO, "Processing text to speech")
    input = request.decode('utf-8')
    data = json.loads(input)

    tts_output = synthesizer(data["userMessage"])

    # Convert the audio data to a numpy array
    audio_data = np.array(tts_output["audio"], dtype=np.int16)

    # # Normalize audio data to the range of int16
    # audio_data = np.int16(audio_data / np.max(np.abs(audio_data)) * 32767)
    
    scipy.io.wavfile.write("bark_out.wav", rate=32000, data=audio_data)
    return send_file("bark_out.wav", mimetype="audio/wav")

  except Exception as e:
    logger.log(LogLevel.ERROR, f"Error processing text to speech, {e}")
    return jsonify({"error": str(e)}), 500
