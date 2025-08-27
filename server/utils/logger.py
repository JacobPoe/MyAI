import json
import os

from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    AGENT = "AGENT"
    CAPTION = "CAPTION"
    DATA = "DATA"
    DEBUG = "DEBUG"
    ERROR = "ERROR"
    INFO = "INFO"
    SYNTHESIZER = "SYNTH"
    TRAINER = "TRAINER"


class Logger:
    @staticmethod
    def log(level: LogLevel, message: str):
        assert LogLevel(level) is not None, f"Invalid log level: {level}"
        print(f"[MyAI-{level.value} | {datetime.now().strftime("%Y-%m-%d__%H-%M-%S")}] :: {message}")

    @staticmethod
    def save_log(level: LogLevel, conversation_history):
        Logger.log(LogLevel.INFO, "Saving conversation history...")

        # Ensure the history directory exists
        os.makedirs(f"prompts/history/{level.value}", exist_ok=True)

        # Define the file path
        timestamp = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
        file_path = os.path.join(f"prompts/history/{level.value}", timestamp + ".json")

        # Write the conversation history to the JSON file
        with open(file_path, "w") as f:
            json.dump(conversation_history, f, indent=2)

        Logger.log(LogLevel.INFO, f"Conversation history saved to {file_path}")
