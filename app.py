import sys

import gradio as gr

from enums.features import Features
from enums.logger import LogLevel

from models.captioner import Captioner
from models.chatbot import Chatbot

from utils.logger import Logger

captioner: Captioner
chatbot: Chatbot
logger = Logger()
startup_error = 'Missing or invalid input parameter. Please provide a valid input.\nAcceptable values are: [chat | caption]'

def launch_captioner():
  captioner = Captioner(logger)
  if (captioner is None):
    logger.log(LogLevel.ERROR, 'Captioner instance is null.')
    return
  
  demo = gr.Interface(fn=captioner.callback, inputs=gr.Image(), outputs="text", title="Image Captioning", description="Upload an image:")
  demo.launch(server_name="0.0.0.0", server_port= 7860)

def launch_chatbot():
  chatbot = Chatbot(logger)
  if (chatbot is None):
    logger.log(LogLevel.ERROR, 'Chatbot instance is null.')
    return

def main(argv):
  if argv[1].lower() == Features.IMAGE_CAPTIONING.value.lower():
    launch_captioner()
  elif argv[1].lower() == Features.CHATBOT.value.lower():
    launch_chatbot()
  else:
    logger.log(LogLevel.ERROR, startup_error)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    logger.log(LogLevel.ERROR, startup_error)
  else:
    main(sys.argv)