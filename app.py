import os
import json
from worker import speech_to_text, text_to_speech

from flask import Flask, render_template, request
from flask_cors import CORS


# Load environment variables
from dotenv import load_dotenv
load_dotenv()
SERVER_PORT = os.getenv("SERVER_PORT")
SERVER_HOST = os.getenv("SERVER_HOST")

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

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
  return text_to_speech(request.data)

### Main
####################################################################################################
if __name__ == "__main__":
  app.run(port=SERVER_PORT, host=SERVER_HOST)
