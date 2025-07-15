import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from utils.enums.enums import LogLevel
from utils.logger.logger import Logger
from utils.nlp.chatbot import Chatbot
from utils.nlp.translator import Translator

# Load and configure environment variables
load_dotenv()
DEBUG = os.getenv("DEBUG")
ROUTE_STT = os.getenv("ROUTE_STT")
ROUTE_TTS = os.getenv("ROUTE_TTS")
SERVER_PORT = os.getenv("SERVER_PORT")
SERVER_HOST = os.getenv("SERVER_HOST")

# Initialize the chatbot instance
chatbot = Chatbot()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

### GETs
####################################################################################################


### POSTs
####################################################################################################
@app.route(ROUTE_STT, methods=["POST"])
def route_audio_prompt():
    try:
        response = Translator.handle_audio_prompt(chatbot, request)
        return response
    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing audio prompt, {e}")
        return jsonify({"error": str(e)}), 500


@app.route(ROUTE_TTS, methods=["POST"])
def route_text_prompt():
    try:
        text, audio = Translator.handle_text_prompt(chatbot, request)
        return jsonify({"text": text, "audio": audio}), 200
    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing text prompt, {e}")
        return jsonify({"error": str(e)}), 500


### Main
####################################################################################################
if __name__ == "__main__":
    app.run(port=SERVER_PORT, host=SERVER_HOST)
