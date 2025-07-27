import os
import time

from transformers import GPT2Tokenizer, GPT2LMHeadModel, pipeline, set_seed

from services.audio import AudioService
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

model: GPT2LMHeadModel
tokenizer: GPT2Tokenizer

# TODO: Read in the conversation history from a JSON file
conversation_history: list = []
DEBUG: bool
log_level: LogLevel = LogLevel.MODEL


class Model:
    def __init__(self, debug: bool = False):
        Logger.log(log_level, "Initializing Chatbot...")
        self.DEBUG = debug
        self.conversation_history = []

        self.tokenizer = GPT2Tokenizer.from_pretrained(Models.GPT2.value)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        model_path = "./../../training_data/gpt2-finetuned"
        if os.path.exists(model_path):
            self.model = GPT2LMHeadModel.from_pretrained(model_path)
        else:
            self.model = GPT2LMHeadModel.from_pretrained("gpt2")
        self.model.config.pad_token_id = self.model.config.eos_token_id

        generator = pipeline(Tasks.TEXT_GENERATION.value, model=self.model, tokenizer=self.tokenizer)
        set_seed(67)
        generator("Hello!", padding=False, truncation=True, max_length=512)

        Logger.log(log_level, "Chatbot initialized successfully.")

    def __del__(self):
        Logger.save_log(log_level, self.conversation_history)
        Logger.log(log_level, "Chatbot instance destroyed.")

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
