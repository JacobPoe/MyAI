import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from utils.enums import LogLevel
from utils.logger import Logger
from nlp.worker import speech_to_text, text_to_speech

# Load environment variables
from dotenv import load_dotenv

load_dotenv()
DEBUG = os.getenv("DEBUG")
ROUTE_STT = os.getenv("ROUTE_STT")
ROUTE_TTS = os.getenv("ROUTE_TTS")
SERVER_PORT = os.getenv("SERVER_PORT")
SERVER_HOST = os.getenv("SERVER_HOST")

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

### GETs
####################################################################################################


### POSTs
####################################################################################################
@app.route(ROUTE_STT, methods=["POST"])
def speech_to_text_route():
    try:
        response = speech_to_text(request.data)
        return response
    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing speech to text, {e}")
        return jsonify({"error": str(e)}), 500


@app.route(ROUTE_TTS, methods=["POST"])
def text_to_speech_route():
    try:
        response = text_to_speech(request.data)
        return response
    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing text to speech, {e}")
        return jsonify({"error": str(e)}), 500


### Main
####################################################################################################
if __name__ == "__main__":
    app.run(port=SERVER_PORT, host=SERVER_HOST)
