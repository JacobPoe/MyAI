import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from utils.enums import LogLevel
from utils.logger import Logger
from utils.nlp.chatbot import Chatbot
from utils.nlp.translator import handle_audio_prompt, handle_text_prompt

# Load environment variables
from dotenv import load_dotenv

load_dotenv()
DEBUG = os.getenv("DEBUG")
ROUTE_STT = os.getenv("ROUTE_STT")
ROUTE_TTS = os.getenv("ROUTE_TTS")
SERVER_PORT = os.getenv("SERVER_PORT")
SERVER_HOST = os.getenv("SERVER_HOST")

app = Flask(__name__)
chatbot = Chatbot()
cors = CORS(app, resources={r"/*": {"origins": "*"}})

### GETs
####################################################################################################


### POSTs
####################################################################################################
@app.route(ROUTE_STT, methods=["POST"])
def route_audio_prompt():
    try:
        response = handle_audio_prompt(chatbot, request.data)
        return response
    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing audio prompt, {e}")
        return jsonify({"error": str(e)}), 500


@app.route(ROUTE_TTS, methods=["POST"])
def route_text_prompt():
    try:
        text, audio = handle_text_prompt(chatbot, request.data)
        return jsonify({"text": text, "audio": audio})
    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing text prompt, {e}")
        return jsonify({"error": str(e)}), 500


### Main
####################################################################################################
if __name__ == "__main__":
    app.run(port=SERVER_PORT, host=SERVER_HOST)
