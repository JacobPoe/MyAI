import sys

import gradio as gr
from PIL import Image

from enums.features import Features
from enums.logger import LogLevel

from models.captioner import Captioner
from models.chatbot import Chatbot

from utils.logger import Logger

logger = Logger()
startup_error = 'Missing or invalid input parameter. Please provide a valid input.\nAcceptable values are: [chat | caption]'

# Callback method for the captioner
def caption(image):
  cap = Captioner(logger)
  raw_image = Image.fromarray(image).convert('RGB')

  return cap.caption_img(raw_image)

def launch_captioner():
  demo = gr.Interface(fn=caption, inputs=gr.Image(), outputs="text", title="Image Captioning", description="Upload an image:")
  demo.launch(server_name="0.0.0.0", server_port= 7860)

def launch_chatbot(logger: Logger):
  chat = Chatbot(logger)

def main(argv):
  if argv[1].lower() == Features.IMAGE_CAPTIONING.value.lower():
    launch_captioner(logger)
  elif argv[1].lower() == Features.CHATBOT.value.lower():
    launch_chatbot(logger)
  else:
    logger.log(LogLevel.ERROR, startup_error)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    logger.log(LogLevel.ERROR, startup_error)
  else:
    main(sys.argv)