import datetime
import json
import os

from enums.logger import LogLevel

class Logger:
  def log(self, level: LogLevel, message: str):
    # TODO: Control flow to check if level is part of enum
    print(f"[{level.value}] :: {message}")
  
  def save_conversation_history(self, caller: str, conversation_history):
    self.log(LogLevel.INFO.value, 'Saving conversation history...')
        
    # Ensure the history directory exists
    os.makedirs(f'history/{caller}', exist_ok=True)
    
    # Define the file path
    timestamp = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
    file_path = os.path.join(f'history/{caller}', timestamp + '.json')
    
    # Write the conversation history to the JSON file
    with open(file_path, 'w') as f:
      json.dump(conversation_history, f, indent=2)
    
    self.log(LogLevel.INFO.value, f'Conversation history saved to {file_path}')
    return