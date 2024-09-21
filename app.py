import sys

import gradio as gr
from PIL import Image

from models.captioner import Captioner
from models.chatbot import Chatbot

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
  if argv[1] == "caption":
      launch_captioner()
  elif argv[1] == "chat":
      launch_chatbot()

if __name__ == '__main__':
    main(sys.argv)