import json
import os

from datetime import datetime
from enums.logger import LogLevel

class Logger:
  def log(self, level: LogLevel, message: str):
    # TODO: Control flow to check if level is part of enum
    print(f"[MyAI-{level.value}] :: {message}")
  
  def save_log(self, caller: LogLevel, conversation_history):
    self.log(LogLevel.INFO, 'Saving conversation history...')
        
    # Ensure the history directory exists
    os.makedirs(f'history/{caller.value}', exist_ok=True)
    
    # Define the file path
    timestamp = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
    file_path = os.path.join(f'history/{caller.value}', timestamp + '.json')
    
    # Write the conversation history to the JSON file
    with open(file_path, 'w') as f:
      json.dump(conversation_history, f, indent=2)
    
    self.log(LogLevel.INFO, f'Conversation history saved to {file_path}')
    return