import io
import scipy
import time

from pydub import AudioSegment
from transformers import GPT2Tokenizer, GPT2LMHeadModel, pipeline, set_seed

from services.sanitize import Sanitize

from utils.enums import (
    AudioRequestMode,
    LogLevel,
    Models,
    Tasks,
    PipelineFrameworks,
)
from utils.logger import Logger
from utils.nlp.synthesizer import Synthesizer


model: GPT2LMHeadModel
tokenizer: GPT2Tokenizer

log_level: LogLevel = LogLevel.CHATBOT
conversation_history: list
DEBUG: bool


class Chatbot:
    def __init__(self, debug: bool = False):
        Logger.log(log_level, "Initializing Chatbot...")
        self.DEBUG = debug

        self.tokenizer = GPT2Tokenizer.from_pretrained(Models.GPT2.value)
        self.model = GPT2LMHeadModel.from_pretrained(Models.GPT2.value)

        # TODO: Read in the conversation history from a JSON file
        self.conversation_history = []

        generator = pipeline(
            Tasks.TEXT_GENERATION.value, model=Models.GPT2.value
        )
        set_seed(67)
        generator("Hello!", truncation=False, num_return_sequences=10)

        Logger.log(log_level, "Chatbot initialized successfully.")

    def __del__(self):
        Logger.save_log(log_level, self.conversation_history)
        Logger.log(log_level, "Chatbot instance destroyed.")

    def generate_reply(self, user_input: str):
        # Encode the input and add conversation history for context
        conversation_context = " ".join(
            [entry["user_input"] for entry in self.conversation_history]
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
        headers = Sanitize.decode_headers(request.query_string)
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
        audio_data = self.load_request_audio(request.data)
        request_transcription = Synthesizer.stt_pipeline(audio_data)

        # If the request is a question, generate a reply from the model using the input transcription as a prompt
        if headers.get("mode") == AudioRequestMode.QUESTION.value:
            reply = self.generate_reply(request_transcription.get("text", ""))

        if headers.get("narrateResponse") == "true":
            audio = Synthesizer.generate_audio(reply)

        return {
            "reply": reply,
            "audio": audio,
            "transcription": request_transcription.get("text", "")
        }

    def handle_text_prompt(self, request):
        Logger.log(LogLevel.INFO, "Handling text prompt")

        headers = Sanitize.decode_headers(request.query_string)
        assert (
            headers.get("userMessage") is not None
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
        reply = self.generate_reply(headers.get("userMessage"))
        # Return no audio data unless requested
        audio_base64 = None

        # If the user requested an STT response
        if headers.get("narrateResponse") == "true":
            audio_base64 = Synthesizer.generate_audio(reply)

        return {"reply": reply, "audio": audio_base64}

    def load_request_audio(self, data):
        Logger.log(LogLevel.INFO, "Loading audio data from request...")
        audio_buffer = io.BytesIO(data)
        wav_buffer = io.BytesIO()

        audio = AudioSegment.from_file(audio_buffer)
        audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0)

        if self.DEBUG:
            Logger.log(LogLevel.DEBUG, "Saving audio data to debug.raw")
            with open("debug.raw", "wb") as f:
                f.write(audio_buffer.read())

        # Read the audio data from the wav_buffer
        sampling_rate, audio_data = scipy.io.wavfile.read(wav_buffer)
        Logger.log(LogLevel.INFO, "Audio data loaded successfully.")

        wav_buffer.close()
        return audio_data
