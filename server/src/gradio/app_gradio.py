import sys

import gradio as gr

from models.captioner import Captioner
from models.chatbot import Chatbot

from server.src.enums import Features, LogLevel
from server.src.utils.logger import Logger

captioner: Captioner
chatbot: Chatbot
logger = Logger()

server_name = '0.0.0.0'
server_port = 1587
startup_error = 'Missing or invalid input parameter. Please provide a valid input.\nAcceptable values are: [chat | caption]'

def launch_captioner():
  captioner = Captioner(logger)
  if captioner is None:
    logger.log(LogLevel.ERROR, 'Captioner failed to launch.')
    return
  
  demo = gr.Interface(fn=captioner.callback, inputs=gr.Image(), outputs="text", title="Image Captioning", description="Upload an image:")
  demo.launch(server_name=server_name, server_port=server_port)

def launch_chatbot():
  chatbot = Chatbot(logger)
  if chatbot is None:
    logger.log(LogLevel.ERROR, 'Chatbot failed to launch.')
    return
  
  demo = gr.Interface(fn=chatbot.callback, inputs=gr.Textbox(), outputs="text", title="Chatbot", description="Input prompt:")
  demo.launch(server_name=server_name, server_port=server_port)

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