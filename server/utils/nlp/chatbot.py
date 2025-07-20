import io
import json
import scipy
import time
import torch

from flask import jsonify
from pydub import AudioSegment
from transformers import GPT2Tokenizer, GPT2LMHeadModel, pipeline, set_seed

from utils.enums import LogLevel, Models, Tasks, PipelineFrameworks
from utils.logger import Logger
from utils.nlp.synthesizer import Synthesizer

model: GPT2LMHeadModel
tokenizer: GPT2Tokenizer

log_level: LogLevel = LogLevel.CHATBOT
conversation_history: list

Logger.log(LogLevel.INFO, "Loading STT pipeline...")
stt_pipeline = pipeline(
    Tasks.ASR.value,
    Models.WHISPER_LARGE_V3_TURBO.value,
    torch_dtype=torch.float32,
)
Logger.log(LogLevel.INFO, "STT pipeline loaded successfully.")


class Chatbot:
    def __init__(self):
        Logger.log(log_level, "Initializing Chatbot...")

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
        Logger.log(LogLevel.INFO, "Processing audio prompt")

        request_audio = request.files.get("wav").read()
        audio_buffer = io.BytesIO(request_audio)
        wav_buffer = io.BytesIO()

        audio = AudioSegment.from_file(audio_buffer)
        audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0)

        # Read the audio data from the wav_buffer
        sampling_rate, audio_data = scipy.io.wavfile.read(wav_buffer)

        # Pass the audio data to the whisper pipeline
        transcription = stt_pipeline(audio_data)
        Logger.log(LogLevel.INFO, f"STT transcription: {transcription}")

        reply = self.generate_reply(transcription["text"])
        Logger.log(LogLevel.INFO, f"Chatbot reply: {reply}")

        audio_base64 = None
        if request.form.get("requestAudioResponses"):
            audio_base64 = Synthesizer.generate_audio(reply)

        return jsonify(
            {
                "transcription": transcription,
                "reply": reply,
                "audio": audio_base64,
            }
        )

    def handle_text_prompt(self, request):
        Logger.log(LogLevel.INFO, "Processing text prompt")

        # Decode the request
        decoded_request = request.data.decode("utf-8")
        data = json.loads(decoded_request)

        # Generate the reply and save it to the response
        transcript = self.generate_reply(data["userMessage"])
        # Return no audio data unless requested
        audio_base64 = None

        # If the user requested an STT response
        if data["generateAudioResponses"]:
            audio_base64 = Synthesizer.generate_audio(transcript)

        return jsonify({"text": transcript, "audio": audio_base64})
