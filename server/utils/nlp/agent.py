import json
import os
import time
import torch

from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed

from services.audio import AudioService
from services.env import EnvService, EnvVars
from services.sanitize import SanitizeService

from utils.nlp.enums import (
    AudioRequestMode,
    ConfigType,
    DeviceMap,
    PipelineFrameworks,
    Models,
    Roles,
)
from utils.logger import Logger, LogLevel
from utils.nlp.synthesizer import Synthesizer

AGENT_MODEL = EnvService.get(EnvVars.DEFAULT_MODEL.value, Models.GPT2.value)
DEVICE_MAP = EnvService.get(EnvVars.DEVICE_MAP.value, DeviceMap.AUTO.value)
MAX_NEW_TOKENS = EnvService.get_int(EnvVars.MAX_NEW_TOKENS.value, 32)
PRETRAINED_MODEL_DIR = EnvService.get(EnvVars.PRETRAINED_MODEL_DIR.value)


class Agent:
    """
    The base model which interacts with the user via the web client.
    Long-term, Agent will be able to parse user input, determine if the input is a general text generation request
    (i.e. a question or ongoing conversation), or a task request. If the request is a task, Agent will leverage the base
    model to determine the steps required to complete this task, leverage any pipelines in the .nlp package, and return
    a response to the user via the web client.
    """

    def __init__(self, debug: bool = False):
        self.conversation_history = []
        self.DEBUG = debug
        self.agent_config = None
        self.model_config = None
        self.model = None
        self.tokenizer = None

        Agent.check_and_build_model_dirs()
        pretrained_model_dir = (
                EnvService.get(EnvVars.PRETRAINED_MODEL_DIR.value)
                + "/results/"
                + AGENT_MODEL
        )

        try:
            self.synthesizer = Synthesizer()
            self.tokenizer = Agent.get_tokenizer_from_pretrained()
            self.init_model(pretrained_model_dir)
        except Exception as e:
            Logger.log(
                LogLevel.ERROR,
                "Failed to load agent providers from path: {}. Providers will be loaded using default pretrained model. Error: {}".format(
                    pretrained_model_dir, e
                ),
            )

        if self.model is None or self.tokenizer is None:
            self.init_default_providers()

    def __del__(self):
        Logger.save_log(LogLevel.AGENT, self.conversation_history)
        Logger.log(LogLevel.AGENT, "Agent instance destroyed.")

    def generate_reply(self, user_input: str):
        self.record_interaction_to_history(Roles.USER, user_input)

        if self.tokenizer.chat_template is not None:
            Logger.log(
                LogLevel.AGENT,
                "Using tokenizer's built-in chat template for tokenization.",
            )
            to_tokenize = self.tokenizer.apply_chat_template(
                self.conversation_history,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            to_tokenize = self.conversation_history[-1].get("content")

        model_inputs = self.tokenizer(
            [to_tokenize], return_tensors=PipelineFrameworks.PYTORCH.value
        ).to(self.model.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=MAX_NEW_TOKENS,
        )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]) :].tolist()
        response = self.tokenizer.decode(
            output_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )

        self.record_interaction_to_history(Roles.AGENT, response)
        return response

    def handle_audio_prompt(self, request):
        headers = SanitizeService.decode_headers(request.query_string)
        if self.DEBUG:
            Logger.log(
                LogLevel.AGENT,
                f"Handling audio prompt of type '{headers.get("mode")}'",
            )
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
        audio_data = AudioService.load_audio(request.data, self.DEBUG)

        if self.synthesizer.stt_pipeline is None:
            self.synthesizer.init_stt_pipeline()

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

    def init_default_providers(self):
        if self.model is None:
            if self.DEBUG:
                Logger.log(
                    LogLevel.AGENT,
                    f"Model is not initialized, defaulting to model '{AGENT_MODEL}'.",
                )
            self.init_model(None)

        if self.tokenizer is None:
            if self.DEBUG:
                Logger.log(
                    LogLevel.AGENT,
                    f"Tokenizer is not initialized, defaulting to tokenizer '{AGENT_MODEL}.",
                )
            self.tokenizer = Agent.get_tokenizer_from_pretrained()

        self.set_token_padding()
        Logger.log(LogLevel.AGENT, "Agent initialized using default providers.")

    def init_model(self, model_dir: str | None):
        path = Agent.load_most_recently_trained_model(model_dir)
        if path is not None:
            Logger.log(
                LogLevel.AGENT,
                f"Using most recently trained model: {path}",
            )
        else:
            path = AGENT_MODEL
            Logger.log(LogLevel.AGENT, f"Using default model: {path}")

        self.model = AutoModelForCausalLM.from_pretrained(
            path,
            use_safetensors=True,
            torch_dtype=torch.float32,
            device_map=DEVICE_MAP,
        )

        self.model_config = self.load_config(ConfigType.MODEL.value)
        for k, v in self.model_config.items():
            setattr(self.model.generation_config, k, v)

    def load_config(self, config_type: str):
        config_path = os.path.join(
            os.path.abspath(os.path.join(__file__, "../../../config")),
            f"{config_type}.json",
        )
        if self.DEBUG:
            Logger.log(
                LogLevel.DEBUG,
                f"Loading {config_type} config from: {config_path}",
            )
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            if self.DEBUG:
                Logger.log(
                    LogLevel.DEBUG, f"{config_type} config loaded: {config}"
                )
            return config
        except FileNotFoundError:
            Logger.log(
                LogLevel.ERROR,
                f"Config file {config_path} not found.",
            )
            return None

    def record_interaction_to_history(self, role: Roles, content: str | set):
        self.conversation_history.append(
            {
                "timestamp": int(time.time()),
                "role": role.value,
                "content": content,
            }
        )
        if self.DEBUG:
            Logger.log(
                LogLevel.AGENT,
                f"Interaction saved: {self.conversation_history[-1]}",
            )

    def set_token_padding(self):
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model.config.pad_token_id = self.model.config.eos_token_id

    def wake_agent(self):
        """
        A bootstrapping method to instantiate the agent with the default model and tokenizer and a user-defined config.
        """
        try:
            self.agent_config = self.load_config(ConfigType.AGENT.value)
            startup_prompt = self.agent_config.get("startup_prompt", "")

            if (
                self.tokenizer.pad_token is None
                and self.tokenizer.eos_token is not None
            ):
                self.set_token_padding()

            emb_rows = self.model.get_input_embeddings().weight.shape[0]
            if emb_rows != len(self.tokenizer):
                self.model.resize_token_embeddings(len(self.tokenizer))

            set_seed(self.agent_config.get("seed", 67))

            startup_msg = self.generate_reply(startup_prompt)
            self.record_interaction_to_history(Roles.AGENT, startup_msg)

            return startup_msg

        except Exception as e:
            Logger.log(
                LogLevel.ERROR,
                f"Failed to initialize agent. Initial prompts may take longer than expected. Error: {e}",
            )

    @staticmethod
    def check_and_build_model_dirs():
        os.makedirs(PRETRAINED_MODEL_DIR, exist_ok=True)
        os.makedirs(PRETRAINED_MODEL_DIR + "/logs", exist_ok=True)
        os.makedirs(PRETRAINED_MODEL_DIR + "/results", exist_ok=True)

    @staticmethod
    def get_tokenizer_from_pretrained(model: str = AGENT_MODEL):
        return AutoTokenizer.from_pretrained(model)

    @staticmethod
    def load_most_recently_trained_model(directory):
        """
        Loads the most recent model from the specified directory.
        Assumes that the models are saved to folders which follow a regular naming convention
        which ends in a timestamp.
        """
        os.makedirs(PRETRAINED_MODEL_DIR + "/results/" + AGENT_MODEL, exist_ok=True)

        folders = [
            f
            for f in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, f))
        ]
        # Return the alphabetically last folder name
        return directory + "/" + max(folders) if folders else None
