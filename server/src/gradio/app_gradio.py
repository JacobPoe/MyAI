import os
import sys

import gradio as gr

from models.captioner import Captioner
from models.chatbot import Chatbot
from models.stt import STT

from enums import Features, LogLevel
from logger import Logger

captioner: Captioner
chatbot: Chatbot

server_host = os.getenv("SERVER_HOST")
server_port = 1587
startup_error = 'Missing or invalid input parameter. Please provide a valid input.\nAcceptable values are: [chat | caption]'

def launch_captioner():
  captioner = Captioner()
  if captioner is None:
    Logger.log(LogLevel.ERROR, 'Captioner failed to launch.')
    return
  
  demo = gr.Interface(fn=captioner.callback, inputs=gr.Image(), outputs="text", title="Image Captioning", description="Upload an image:")
  demo.launch(server_name=server_host, server_port=server_port)

def launch_chatbot():
  chatbot = Chatbot()
  if chatbot is None:
    Logger.log(LogLevel.ERROR, 'Chatbot failed to launch.')
    return
  
  demo = gr.Interface(fn=chatbot.callback, inputs=gr.Textbox(), outputs="text", title="Chatbot", description="Input prompt:")
  demo.launch(server_name=server_host, server_port=server_port)

def launch_stt():
  stt = STT()
  if stt is None:
      Logger.log(LogLevel.ERROR, 'STT failed to launch.')
      return

  demo = gr.Interface(fn=stt.callback, inputs=gr.Audio(), outputs="text", title="Speech-to-Text", description="Upload an audio file or record one with your onboard microphone:")
  demo.launch(server_name=server_host, server_port=server_port)

def main(argv):
  if argv[1].lower() == Features.IMAGE_CAPTIONING.value.lower():
    launch_captioner()
  elif argv[1].lower() == Features.CHATBOT.value.lower():
    launch_chatbot()
  elif argv[1].lower() == Features.STT.value.lower():
    launch_stt()
  else:
    Logger.log(LogLevel.ERROR, startup_error)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    Logger.log(LogLevel.ERROR, startup_error)
  else:
    main(sys.argv)