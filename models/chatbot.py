import time
import gradio as gr

from transformers import GPT2Tokenizer, GPT2LMHeadModel, pipeline, set_seed

from enums.logger import LogLevel
from utils.logger import Logger

generator: pipeline
model: GPT2LMHeadModel
tokenizer: GPT2Tokenizer


log_level: LogLevel = LogLevel.CHATBOT
conversation_history: list

class Chatbot:
  def __init__(self, logger: Logger):
    logger.log(log_level, 'Initializing Chatbot...')

    tokenizer = GPT2Tokenizer.from_pretrained('gpt2-medium')
    model = GPT2LMHeadModel.from_pretrained('gpt2-medium')

    self.logger = logger
    self.conversation_history = []
    self.model = model
    self.tokenizer = tokenizer

    generator = pipeline('text-generation', model='gpt2-medium')
    set_seed(67)
    generator("Facilitate conversation", max_length=30, num_return_sequences=1)
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
    encoded_input = self.tokenizer(user_input, return_tensors='pt')
  
    # Decode the output tensor to a string
    model_output = self.model.generate(**encoded_input, max_new_tokens=500)
    output = self.tokenizer.decode(model_output[0], skip_special_tokens=True)
    
    self.logger.log(log_level, output)
    self.conversation_history.append({
      int(time.time()): {
        'user_input': user_input,
        'bot_output': output
      }
    })

    return output