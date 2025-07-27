from flask import Flask, jsonify, request
from flask_cors import CORS

from services.env import EnvService

from utils.enums import LogLevel
from utils.logger import Logger
from utils.nlp.model import Model
from utils.nlp.trainer import Trainer

DEBUG = EnvService.get_debug()
ROUTE_ASR = EnvService.get_route_asr()
ROUTE_TTS = EnvService.get_route_tts()
ROUTE_TRAINING = EnvService.get_route_training()
SERVER_PORT = EnvService.get_server_port()
SERVER_HOST = EnvService.get_server_host()

# Initialize the LLM instance and trainer
model = Model(DEBUG)
trainer = Trainer(model.model, model.tokenizer)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


### GETs
####################################################################################################
@app.route(ROUTE_TRAINING, methods=["GET"])
def route_training():
    try:
        trainer.init_training()
        return 200
    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing training request, {e}")
        return jsonify({"error": str(e)}), 500


### POSTs
####################################################################################################
@app.route(ROUTE_ASR, methods=["POST"])
def route_audio_prompt():
    try:
        response = model.handle_audio_prompt(request)
        return jsonify(response), 200
    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing audio prompt, {e}")
        return jsonify({"error": str(e)}), 500


@app.route(ROUTE_TTS, methods=["POST"])
def route_text_prompt():
    try:
        response = model.handle_text_prompt(request)
        return jsonify(response), 200
    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing text prompt, {e}")
        return jsonify({"error": str(e)}), 500


### Main
####################################################################################################
if __name__ == "__main__":
    app.run(port=SERVER_PORT, host=SERVER_HOST, debug=DEBUG, use_reloader=False)
