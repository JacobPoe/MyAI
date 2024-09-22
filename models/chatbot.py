from transformers import GPT2Tokenizer, GPT2LMHeadModel, pipeline, set_seed

from enums.logger import LogLevel
from utils.logger import Logger

generator: pipeline
model: GPT2LMHeadModel
tokenizer: GPT2Tokenizer


chat_level: LogLevel = LogLevel.CHATBOT
conversation_history: list


class Chatbot:
  def __init__(self, logger: Logger):
    logger.log(chat_level, 'Initializing Chatbot...')

    tokenizer = GPT2Tokenizer.from_pretrained('gpt2-xl')
    model = GPT2LMHeadModel.from_pretrained('gpt2-xl')

    self.logger = logger
    self.conversation_history = []
    self.model = model
    self.tokenizer = tokenizer

    generator = pipeline('text-generation', model='gpt2-xl')
    set_seed(42)
    generator("Hello, I'm a language model,", max_length=30, num_return_sequences=1)
    self.generator = generator

    self.logger.log(chat_level, 'Chatbot initialized successfully.')
    self.chat()

  def chat(self, i = -1):
    i+=1
    self.logger.log(chat_level, 'Chatbot is ready to chat. Type "exit" to end the conversation.')
    
    output = ''
    user_input = input("  >\t")

    if user_input == 'exit':
      self.logger.log(chat_level, 'Exiting chat...')
      self.logger.save_conversation_history('Chatbot', self.conversation_history)
      return
    
    encoded_input = self.tokenizer(user_input, return_tensors='pt')
  
    # Decode the output tensor to a string
    model_output = self.model.generate(**encoded_input, max_new_tokens=500)
    output = self.tokenizer.decode(model_output[0], skip_special_tokens=True)
  
    self.logger.log(chat_level, output)
    self.conversation_history.append({
      i: {
        'user_input': user_input,
        'bot_output': output
      }
    })

    self.chat(i)