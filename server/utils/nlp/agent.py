import json
import os
import time
import torch

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, set_seed

from services.audio import AudioService
from services.env import EnvService, EnvVars
from services.sanitize import SanitizeService

from utils.nlp.enums import (
    AudioRequestMode,
    DeviceMap,
    PipelineFrameworks,
    Models,
    Roles,
    Tasks,
)
from utils.logger import Logger, LogLevel
from utils.nlp.synthesizer import Synthesizer

LOG_LEVEL: LogLevel = LogLevel.AGENT
DEFAULT_MODEL = EnvService.get(EnvVars.DEFAULT_MODEL.value, Models.QWEN3.value)
DEVICE_MAP = EnvService.get(EnvVars.DEVICE_MAP.value, DeviceMap.AUTO.value)
PRETRAINED_MODEL_DIR = EnvService.get(EnvVars.PRETRAINED_MODEL_DIR.value)
SELECTED_PRETRAINED_MODEL = EnvService.get(
    EnvVars.SELECTED_PRETRAINED_MODEL.value
)


class Agent:
    def __init__(self, debug: bool = False):
        Logger.log(LOG_LEVEL, "Initializing Agent...")
        self.conversation_history = []
        self.DEBUG = debug
        self.agent_config = None
        self.model = None
        self.tokenizer = None
        self.pipeline = None

        pretrained_model_dir = (
            EnvService.get(EnvVars.PRETRAINED_MODEL_DIR.value) + "/results/"
        )

        try:
            self.synthesizer = Synthesizer()
            path = Agent.get_most_recent_training_results(pretrained_model_dir)
            self.tokenizer = Agent.get_tokenizer_from_pretrained()
            self.model = Agent.get_model_from_pretrained(path)
            Logger.log(LOG_LEVEL, "Agent initialized successfully.")
        except Exception as e:
            Logger.log(
                LogLevel.ERROR,
                "Failed to load agent providers from path: {}. Providers will be loaded using default pretrained model. Error: {}".format(
                    pretrained_model_dir, e
                ),
            )
            self.init_default_providers()

    def __del__(self):
        Logger.save_log(LOG_LEVEL, self.conversation_history)
        Logger.log(LOG_LEVEL, "Agent instance destroyed.")

    def init_default_providers(self):
        if self.model is None:
            self.model = Agent.get_model_from_pretrained()

        if self.tokenizer is None:
            self.tokenizer = Agent.get_tokenizer_from_pretrained()

        self.set_token_padding()
        Logger.log(LOG_LEVEL, "Agent initialized using default providers.")

    def generate_reply(self, user_input: str):
        Agent.record_interaction_to_history(
            self.conversation_history, Roles.USER, user_input
        )

        if self.pipeline is None:
            self.wake_agent()

        to_tokenize = None
        if self.tokenizer.chat_template is not None:
            Logger.log(LogLevel.AGENT, "Using tokenizer's built-in chat template for tokenization.")
            to_tokenize = self.tokenizer.apply_chat_template(
                self.conversation_history,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            to_tokenize = "\n".join(str(attr) for attr in self.conversation_history[-1])

        model_inputs = self.tokenizer([to_tokenize], return_tensors=PipelineFrameworks.PYTORCH.value).to(self.model.device)

        generated_ids = self.model.generate(
            **model_inputs
        )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
        response = self.tokenizer.decode(
            output_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
        )

        Agent.record_interaction_to_history(
            self.conversation_history, Roles.AGENT, response
        )
        return response

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
        request_transcription = self.synthesizer.stt_pipeline(audio_data)

        # If the request is a question, generate a reply from the model using the input transcription as a prompt
        if headers.get("mode") == AudioRequestMode.QUESTION.value:
            reply = self.generate_reply(request_transcription.get("text", ""))

        if headers.get("narrateResponse") == "true":
            audio = self.synthesizer.generate_audio(reply)

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
            audio_base64 = self.synthesizer.generate_audio(reply)

        return {"reply": reply, "audio": audio_base64}

    def set_token_padding(self):
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model.config.pad_token_id = self.model.config.eos_token_id

    def wake_agent(self):
        try:
            config_path = os.path.join(
                os.path.abspath(os.path.join(__file__, "../../../config")),
                "agent.json",
            )
            Logger.log(
                LogLevel.AGENT, f"Loading agent config from: {config_path}"
            )
            with open(config_path, "r", encoding="utf-8") as f:
                self.agent_config = json.load(f)
                Logger.log(
                    LogLevel.AGENT, f"Agent config loaded: {self.agent_config}"
                )

            seed = self.agent_config.get("seed", 67)
            startup_prompt = self.agent_config.get("startup_prompt", "")

            if (
                self.tokenizer.pad_token is None
                and self.tokenizer.eos_token is not None
            ):
                self.set_token_padding()

            max_ctx = getattr(
                self.model.config, "max_position_embeddings", None
            ) or getattr(self.model.config, "n_positions", None)
            if max_ctx is not None:
                self.tokenizer.model_max_length = max_ctx

            emb_rows = self.model.get_input_embeddings().weight.shape[0]
            if emb_rows != len(self.tokenizer):
                self.model.resize_token_embeddings(len(self.tokenizer))

            self.pipeline = pipeline(
                task=Tasks.TEXT_GENERATION.value,
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=128,
            )
            set_seed(seed)
            startup_msg = self.pipeline(
                startup_prompt,
                padding=False,
                truncation=True,
                max_length=self.tokenizer.model_max_length,
            )[0]["generated_text"]

            Agent.record_interaction_to_history(
                self.conversation_history, Roles.AGENT, startup_msg
            )
            return startup_msg

        except Exception as e:
            Logger.log(
                LogLevel.ERROR,
                f"Failed to initialize agent. Initial prompts may take longer than expected. Error: {e}",
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

    @staticmethod
    def get_model_from_pretrained(model: str = DEFAULT_MODEL):
        return AutoModelForCausalLM.from_pretrained(
            model,
            use_safetensors=True,
            torch_dtype=torch.float32,
            device_map=DEVICE_MAP,
        )

    @staticmethod
    def get_tokenizer_from_pretrained(model: str = DEFAULT_MODEL):
        return AutoTokenizer.from_pretrained(model)

    @staticmethod
    def record_interaction_to_history(
        history: list, role: Roles, content: str | set
    ):
        history.append(
            {
                "timestamp": int(time.time()),
                "role": role.value,
                "content": content,
            }
        )
        Logger.log(LogLevel.AGENT, f"Interaction saved: {history[-1]}")
