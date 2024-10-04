import os
import json
from worker import speech_to_text, text_to_speech, openai_process_message

from flask import Flask, render_template, request
from flask_cors import CORS

from utils.logger import Logger
from enums.logger import LogLevel

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
logger = Logger()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/speech-to-text', methods=['POST'])
def speech_to_text_route():
    return None


@app.route('/process-message', methods=['POST'])
def process_prompt_route():
    response = app.response_class(
        response=json.dumps({"openaiResponseText": None, "openaiResponseSpeech": None}),
        status=200,
        mimetype='application/json'
    )
    return response


if __name__ == "__main__":
    # Sanity checking myself that we are loading
    # env vars on a local machine
    message = 'MY_ENV_VAR: ' + os.getenv('MY_ENV_VAR')
    logger.log(LogLevel.INFO, message)
    app.run(port=8000, host='0.0.0.0')
    
