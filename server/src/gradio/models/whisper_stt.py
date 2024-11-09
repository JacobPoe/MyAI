import os
import requests
import torch
from transformers import pipeline

from enums import LogLevel
from logger import Logger
logger = Logger()

from dotenv import load_dotenv
load_dotenv()

########################################################################################################################
### Lab Code: Speech-to-Text (STT) using Hugging Face Transformers
########################################################################################################################

# The lab uses an audio file for speech-to-text (STT) processing. This
# block will download that file if not already present in the working directory.
if not os.path.isfile("downloaded_audio.mp3"):
    logger.log(LogLevel.INFO, "Downloading audio file for lab")

    # URL of the audio file to be downloaded
    url = os.getenv("WHISPER_STT_LAB_MP3_URL")

    # Send a GET request to the URL to download the file
    response = requests.get(url)

    # Define the local file path where the audio file will be saved
    audio_file_path = "downloaded_audio.mp3"

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # If successful, write the content to the specified local file path
        with open(audio_file_path, "wb") as file:
            file.write(response.content)
        logger.log(LogLevel.INFO, "File downloaded successfully")
    else:
        # If the request failed, print an error message
        logger.log(LogLevel.ERROR, "Failed to download the file")

# Initialize the speech-to-text pipeline from Hugging Face Transformers
# This uses the "openai/whisper-tiny.en" model for automatic speech recognition (ASR)
# The `chunk_length_s` parameter specifies the chunk length in seconds for processing
pipe = pipeline(
  "automatic-speech-recognition",
  model="openai/whisper-tiny.en",
  chunk_length_s=30,
)
# Define the path to the audio file that needs to be transcribed
sample = 'downloaded_audio.mp3'
# Perform speech recognition on the audio file
# The `batch_size=8` parameter indicates how many chunks are processed at a time
# The result is stored in `prediction` with the key "text" containing the transcribed text
prediction = pipe(sample, batch_size=8)["text"]
# Print the transcribed text to the console
logger.log(LogLevel.STT, prediction)

########################################################################################################################
### End Lab Code
########################################################################################################################