import os

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from server.nlp.worker import speech_to_text, text_to_speech

from server.enums.logger import LogLevel
from server.utils.logger import Logger

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
DEBUG = os.getenv("DEBUG")
SERVER_PORT = os.getenv("SERVER_PORT")
SERVER_HOST = os.getenv("SERVER_HOST")

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
logger = Logger()

### GETs
####################################################################################################
@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')

### POSTs
####################################################################################################
@app.route('/speech-to-text', methods=['POST'])
def speech_to_text_route():
  try:
    response = speech_to_text(request.data)
    return response
  except Exception as e:
    logger.log(LogLevel.ERROR, f"Error processing speech to text, {e}")
    return jsonify({"error": str(e)}), 500

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech_route():
  try:
    response = text_to_speech(request.data)
    return response
  except Exception as e:
    logger.log(LogLevel.ERROR, f"Error processing text to speech, {e}")
    return jsonify({"error": str(e)}), 500

### Main
####################################################################################################
if __name__ == "__main__":
  app.run(port=SERVER_PORT, host=SERVER_HOST)
