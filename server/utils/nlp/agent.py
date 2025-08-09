import os
import time

from transformers import GPT2Tokenizer, GPT2LMHeadModel, pipeline, set_seed

from services.audio import AudioService
from services.env import EnvService, EnvVars
from services.sanitize import SanitizeService

from utils.enums import (
    AudioRequestMode,
    LogLevel,
    Models,
    PipelineFrameworks,
    Tasks,
)
from utils.logger import Logger
from utils.nlp.synthesizer import Synthesizer

log_level: LogLevel = LogLevel.AGENT
default_model = Models.GPT2.value

PRETRAINED_MODEL_DIR = EnvService.get(EnvVars.PRETRAINED_MODEL_DIR.value)
SELECTED_PRETRAINED_MODEL = EnvService.get(
    EnvVars.SELECTED_PRETRAINED_MODEL.value
)


class Agent:
    def __init__(self, debug: bool = False):
        Logger.log(log_level, "Initializing Agent...")
        self.conversation_history = []
        self.DEBUG = debug
        self.model = None
        self.tokenizer = None

        pretrained_model_dir = (
            EnvService.get(EnvVars.PRETRAINED_MODEL_DIR.value) + "/results/"
        )

        try:
            path = Agent.get_most_recent_training_results(pretrained_model_dir)
            self.model = GPT2LMHeadModel.from_pretrained(
                path, use_safetensors=True
            )
            self.tokenizer = GPT2Tokenizer.from_pretrained(default_model)
            self.set_token_padding()
            Logger.log(log_level, "Agent initialized successfully.")
        except Exception as e:
            Logger.log(
                LogLevel.ERROR,
                "Failed to load agent providers from path: {}. Providers will be loaded using default pretrained model. Error: {}".format(
                    pretrained_model_dir, e
                ),
            )
            self.init_default_providers()

    def __del__(self):
        Logger.save_log(log_level, self.conversation_history)
        Logger.log(log_level, "Agent instance destroyed.")

    def init_default_providers(self):
        if self.model is None:
            self.model = GPT2LMHeadModel.from_pretrained(default_model)

        if self.tokenizer is None:
            self.tokenizer = GPT2Tokenizer.from_pretrained(default_model)

        self.set_token_padding()
        Logger.log(log_level, "Agent initialized using default providers.")

    def generate_reply(self, user_input: str):
        # Encode the input and add conversation history for context
        conversation_context = " ".join(
            [entry.get("user_input") for entry in self.conversation_history]
        )
        input_text = f"{conversation_context} {user_input}"
        encoded_input = self.tokenizer(
            input_text, return_tensors=PipelineFrameworks.PYTORCH.value
        )

        # Generate the output with adjusted parameters
        model_output = self.model.generate(
            **encoded_input,
            max_new_tokens=128,
            top_k=50,
            no_repeat_ngram_size=2,
        )

        output = self.tokenizer.decode(
            model_output[0], skip_special_tokens=False
        )
        Logger.log(log_level, output)

        self.conversation_history.append(
            {
                "timestamp": int(time.time()),
                "user_input": user_input,
                "bot_output": output,
            }
        )

        return output

    def handle_audio_prompt(self, request):
        headers = SanitizeService.decode_headers(request.query_string)
        Logger.log(
            LogLevel.INFO,
            f"Handling audio prompt of type '{headers.get("mode")}'",
        )

        if self.DEBUG:
            Logger.log(LogLevel.DEBUG, f"Request headers: {headers}")

        assert (
            headers.get("mode") is not None
        ), "Request mode must be specified."
        assert AudioRequestMode(
            headers.get("mode")
        ), "Invalid request mode specified."

        reply, audio, transcription = None, None, None

        # Load the raw audio data from the request and transcribe it
        # TODO: Do I need to transcribe audio to text first in order to provide a prompt to call self.generate_reply?
        audio_data = AudioService.load_audio(request.data)
        request_transcription = Synthesizer.stt_pipeline(audio_data)

        # If the request is a question, generate a reply from the model using the input transcription as a prompt
        if headers.get("mode") == AudioRequestMode.QUESTION.value:
            reply = self.generate_reply(request_transcription.get("text", ""))

        if headers.get("narrateResponse") == "true":
            audio = Synthesizer.generate_audio(reply)

        return {
            "reply": reply,
            "audio": audio,
            "transcription": request_transcription.get("text", ""),
        }

    def handle_text_prompt(self, request):
        Logger.log(LogLevel.INFO, "Handling text prompt")

        headers = SanitizeService.decode_headers(request.query_string)
        assert (
            request.form.get("userMessage") is not None
        ), "User message must be provided."
        assert (
            headers.get("mode") is not None
        ), "Request mode must be specified."
        assert AudioRequestMode(
            headers.get("mode")
        ), "Invalid request mode specified."

        if self.DEBUG:
            Logger.log(LogLevel.DEBUG, f"Request headers: {headers}")

        # Generate the reply and save it to the response
        reply = self.generate_reply(request.form.get("userMessage"))
        # Return no audio data unless requested
        audio_base64 = None

        # If the user requested an STT response
        if headers.get("narrateResponse") == "true":
            audio_base64 = Synthesizer.generate_audio(reply)

        return {"reply": reply, "audio": audio_base64}

    def set_token_padding(self):
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model.config.pad_token_id = self.model.config.eos_token_id

    def warm_up_generator(self):
        try:
            generator = pipeline(
                Tasks.TEXT_GENERATION.value,
                model=self.model,
                tokenizer=self.tokenizer,
            )
            set_seed(67)
            generator(
                "Hello!", padding=False, truncation=True, max_new_tokens=10
            )
            Logger.log(log_level, "Generator warmed up successfully.")
        except Exception as e:
            Logger.log(
                LogLevel.ERROR,
                f"Failed to warm up generator. Initial prompts may take longer than expected. Error: {e}",
            )


    @staticmethod
    def get_most_recent_training_results(directory):
        """
        Loads the most recent model from the specified directory.
        Assumes that the models are saved to folders which follow a regular naming convention
        which ends in a timestamp.
        """

        folders = [
            f
            for f in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, f))
        ]
        # Return the alphabetically last folder name
        return directory + max(folders) if folders else None
