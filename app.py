import os

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from nlp.worker import speech_to_text, text_to_speech

from enums.logger import LogLevel
from utils.logger import Logger

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
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
  return speech_to_text(request.data)

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
