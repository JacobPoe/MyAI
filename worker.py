from openai import OpenAI
import requests

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

openai_client = OpenAI()


def speech_to_text(audio_binary):
    return None


def text_to_speech(text, voice=""):
    return None


def openai_process_message(user_message):
    return None
