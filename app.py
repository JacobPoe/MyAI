import sys

import gradio as gr
from PIL import Image

from enums.features import Features

from models.captioner import Captioner
from models.chatbot import Chatbot

startup_error = 'Missing or invalid input parameter. Please provide a valid input.\nAcceptable values are: [chat | caption]'

def caption(image):
  cap = Captioner()
  raw_image = Image.fromarray(image).convert('RGB')

  return cap.caption_img(raw_image)

def launch_captioner():
  demo = gr.Interface(fn=caption, inputs=gr.Image(), outputs="text", title="Image Captioning", description="Upload an image:")
  demo.launch(server_name="0.0.0.0", server_port= 7860)

def launch_chatbot():
  chat = Chatbot()

def main(argv):
  if argv[1].lower() == Features.IMAGE_CAPTIONING.value.lower():
      launch_captioner()
  elif argv[1].lower() == Features.CHATBOT.value.lower():
      launch_chatbot()
  else:
      print(startup_error)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(startup_error)
    else:
      main(sys.argv)