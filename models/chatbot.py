import json
import os

from datetime import datetime
from transformers import GPT2Tokenizer, GPT2LMHeadModel, pipeline, set_seed

generator: pipeline
model: GPT2LMHeadModel
tokenizer: GPT2Tokenizer

conversation_history: list

class Chatbot:
  def __init__(self):
    print('[models.Chatbot::__init__()] Chatbot initialized')

    tokenizer = GPT2Tokenizer.from_pretrained('gpt2-xl')
    model = GPT2LMHeadModel.from_pretrained('gpt2-xl')

    self.tokenizer = tokenizer
    self.model = model
    self.conversation_history = []

    generator = pipeline('text-generation', model='gpt2-xl')
    set_seed(42)
    generator("Hello, I'm a language model,", max_length=30, num_return_sequences=5)
    self.generator = generator

    self.chat(True)
    self.save_conversation_history()

    print('[models.Chatbot::chat()] Chatbot conversation terminated.')

  def chat(self, ongoing: bool):
    print('[models.Chatbot::chat()] Chatbot is ready to chat. Type "exit" to end the conversation.')
    
    i = 0
    output = ''
    while ongoing:
      user_input = input("  >\t")

      if user_input == 'exit':
        ongoing = False
        encoded_input = self.tokenizer('User has terminated conversation. Goodbye!', return_tensors='pt')
      else:
        encoded_input = self.tokenizer(user_input, return_tensors='pt')
      
      # Decode the output tensor to a string
      model_output = self.model.generate(**encoded_input, max_new_tokens=100)
      output = self.tokenizer.decode(model_output[0], skip_special_tokens=True)
    
      print('ch@\t', output)

      self.conversation_history.append({
        i: {
          'user_input': user_input,
          'bot_output': output
        }
      })

      i += 1
    return
  
  def save_conversation_history(self):
    print('[models.Chatbot::save_conversation_history()] Saving conversation history...')
        
    # Ensure the history directory exists
    os.makedirs('history', exist_ok=True)
    
    # Define the file path
    timestamp = datetime.now().strftime("%Y-%m-%d%H-%M-%S")
    file_path = os.path.join('history', 'chat__' + timestamp + '.json')
    
    # Write the conversation history to the JSON file
    with open(file_path, 'w') as f:
      json.dump(self.conversation_history, f, indent=2)
    
    print(f'[models.Chatbot::save_conversation_history()] Conversation history saved to {file_path}')
    return