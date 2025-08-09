from flask import Flask, jsonify, request
from flask_cors import CORS

from services.env import EnvService, EnvVars

from utils.enums import LogLevel
from utils.logger import Logger
from utils.nlp.model import Model
from utils.nlp.trainer import Trainer

DEBUG = EnvService.is_debug()
ROUTE_ASR = EnvService.get(EnvVars.ROUTE_ASR.value)
ROUTE_TRAINING_INIT = EnvService.get(EnvVars.ROUTE_TRAINING_INIT.value)
ROUTE_TTS = EnvService.get(EnvVars.ROUTE_TTS.value)
SERVER_HOST = EnvService.get(EnvVars.SERVER_HOST.value)
SERVER_PORT = EnvService.get(EnvVars.SERVER_PORT.value)

# Initialize the LLM instance
model = Model(DEBUG)
trainer: Trainer or None = None

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


### GETs
####################################################################################################
@app.route(ROUTE_TRAINING_INIT, methods=["GET"])
def route_training_init():
    try:
        global trainer
        if trainer is None:
            trainer = Trainer(model=model.model, tokenizer=model.tokenizer)
        trainer.init_training(request)
        return jsonify({"message": "Training sequence completed. Please validate your results."}), 200
    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error running training sequence, {e}")
        return jsonify({"error": "Error running training sequence."}), 500


### POSTs
####################################################################################################
@app.route(ROUTE_ASR, methods=["POST"])
def route_audio_prompt():
    try:
        response = model.handle_audio_prompt(request)
        return jsonify(response), 200
    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing audio prompt, {e}")
        return jsonify({"error": "Error processing audio prompt."}), 500


@app.route(ROUTE_TTS, methods=["POST"])
def route_text_prompt():
    try:
        response = model.handle_text_prompt(request)
        return jsonify(response), 200
    except Exception as e:
        Logger.log(LogLevel.ERROR, f"Error processing text prompt, {e}")
        return jsonify({"error": "Error processing text prompt."}), 500


### Main
####################################################################################################
if __name__ == "__main__":
    app.run(port=SERVER_PORT, host=SERVER_HOST, debug=DEBUG, use_reloader=False)
