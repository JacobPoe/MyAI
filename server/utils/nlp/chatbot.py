import time

from transformers import GPT2Tokenizer, GPT2LMHeadModel, pipeline, set_seed

from enums.enums import LogLevel, Models, Tasks
from logger.logger import Logger

model: GPT2LMHeadModel
tokenizer: GPT2Tokenizer

log_level: LogLevel = LogLevel.CHATBOT
conversation_history: list


class Chatbot:
    def __init__(self):
        Logger.log(log_level, "Initializing Chatbot...")

        self.tokenizer = GPT2Tokenizer.from_pretrained(Models.GPT2.value)
        self.model = GPT2LMHeadModel.from_pretrained(Models.GPT2.value)

        # TODO: Read in the conversation history from a JSON file
        self.conversation_history = []

        generator = pipeline(Tasks.TEXT_GENERATION.value, model=Models.GPT2.value)
        set_seed(67)
        generator("Hello!", truncation=True, num_return_sequences=5)

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
        encoded_input = self.tokenizer(input_text, return_tensors="pt")

        # Generate the output with adjusted parameters
        model_output = self.model.generate(
            **encoded_input,
            max_new_tokens=128,
            top_k=50,
            no_repeat_ngram_size=2,
        )

        output = self.tokenizer.decode(
            model_output[0], skip_special_tokens=True
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
