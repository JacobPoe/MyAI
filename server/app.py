import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from utils.enums import LogLevel
from utils.logger import Logger
from utils.nlp.chatbot import Chatbot

# Load and configure environment variables
load_dotenv()
_DEBUG = os.getenv("DEBUG")
DEBUG = _DEBUG.lower() == "true" if _DEBUG else False
ROUTE_ASR = os.getenv("ROUTE_ASR", "/api/v1/asr")
ROUTE_TTS = os.getenv("ROUTE_TTS", "/api/v1/tts")
SERVER_PORT = os.getenv("SERVER_PORT", 5000)
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")

# Initialize the chatbot instance
chatbot = Chatbot(DEBUG)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

### GETs
####################################################################################################


### POSTs
####################################################################################################
@app.route(ROUTE_ASR, methods=["POST"])
def route_audio_prompt():
    try:
        response = chatbot.handle_audio_prompt(request)
        return jsonify(response), 200
    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing audio prompt, {e}")
        return jsonify({"error": str(e)}), 500


@app.route(ROUTE_TTS, methods=["POST"])
def route_text_prompt():
    try:
        response = chatbot.handle_text_prompt(request)
        return jsonify(response), 200
    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing text prompt, {e}")
        return jsonify({"error": str(e)}), 500


### Main
####################################################################################################
if __name__ == "__main__":
    app.run(port=SERVER_PORT, host=SERVER_HOST, debug=DEBUG, use_reloader=False)
