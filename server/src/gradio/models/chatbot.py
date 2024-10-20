import time

from transformers import GPT2Tokenizer, GPT2LMHeadModel, pipeline, set_seed

from enums import LogLevel
from logger import Logger

generator: pipeline
model: GPT2LMHeadModel
tokenizer: GPT2Tokenizer

log_level: LogLevel = LogLevel.CHATBOT
conversation_history: list

class Chatbot:
  def __init__(self, logger: Logger):
    logger.log(log_level, 'Initializing Chatbot...')

    tokenizer = GPT2Tokenizer.from_pretrained('gpt2-large')
    model = GPT2LMHeadModel.from_pretrained('gpt2-large')

    self.logger = logger
    self.conversation_history = []
    self.model = model
    self.tokenizer = tokenizer

    generator = pipeline('text-generation', model='gpt2-large')
    set_seed(67)
    generator("Hello!", max_length=30, num_return_sequences=5)
    self.generator = generator

    self.logger.log(log_level, 'Chatbot initialized successfully.')

  def __del__(self):
    self.logger.save_log(log_level, self.conversation_history)
    self.logger.log(log_level, 'Chatbot instance destroyed.')

  def callback(self, input):
    if input == None:
      self.logger.log(LogLevel.ERROR, 'Failed to submit query. Please try again.')
      return
    return self.chat(input)

  def chat(self, user_input: str):
    # Encode the input and add conversation history for context
    conversation_context = " ".join([entry['user_input'] for entry in self.conversation_history[-5:]])
    input_text = f"{conversation_context} {user_input}"
    encoded_input = self.tokenizer(input_text, return_tensors='pt')

    # Generate the output with adjusted parameters
    model_output = self.model.generate(
      **encoded_input,
      max_new_tokens=5000,
      temperature=0.7,
      top_k=50,
      top_p=0.95,
      no_repeat_ngram_size=2
    )

    output = self.tokenizer.decode(model_output[0], skip_special_tokens=True)
    self.logger.log(log_level, output)
    self.conversation_history.append({
        'timestamp': int(time.time()),
        'user_input': user_input,
        'bot_output': output
      })

    return output