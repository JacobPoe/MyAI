import sys

from transformers import BlipProcessor, BlipForConditionalGeneration
from models.captioner import Captioner
from PIL import Image

import gradio as gr

# Initialize the processor and model from Hugging Face
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def caption(image):
  cap = Captioner(processor, model)
  raw_image = Image.fromarray(image).convert('RGB')

  return cap.caption_img(raw_image)

def launch_captioner():
  demo = gr.Interface(fn=caption, inputs=gr.Image(), outputs="text", title="Image Captioning", description="Upload an image:")
  demo.launch(server_name="0.0.0.0", server_port= 7860)

def launch_chatbot():
  print("Launching Chatbot")

def main(argv):
  if argv[1] == "caption":
      launch_captioner()
  elif argv[1] == "chat":
      launch_chatbot()

if __name__ == '__main__':
    main(sys.argv)