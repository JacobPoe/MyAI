import numpy as np

from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

from enums import LogLevel
from logger import Logger

log_level: LogLevel = LogLevel.CAPTION

conversation_history: list
model: BlipForConditionalGeneration
processor: BlipProcessor

class Captioner:
  def __init__(self):
    self.conversation_history = []

    # Initialize the processor and model from Hugging Face
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    self.model = model
    self.processor = processor

  def __del__(self):
    Logger.save_log(log_level, self.conversation_history)
    Logger.log(log_level, 'Captioner instance destroyed.')

  # Callback method for the gradio captioner interface
  def callback(self, image):
    raw_image = Image.fromarray(image).convert('RGB')
    return self.caption_img(raw_image)

  def analyze_img(self, image: np.ndarray):
    # unconditional image captioning
    inputs = processor(image, return_tensors="pt")
    out = self.model.generate(**inputs)
    toReturn = self.processor.decode(out[0], skip_special_tokens=True)
    Logger.log(log_level, toReturn)
    self.conversation_history.append('[analyze_img] ::' + toReturn)

    return toReturn

  def caption_img(self, image: np.ndarray):
    text = 'This is a photo of'
    inputs = self.processor(image, text, return_tensors='pt')

    out = self.model.generate(**inputs)
    toReturn = self.processor.decode(out[0], skip_special_tokens=True)
    Logger.log(log_level, toReturn)
    self.conversation_history.append('[caption_img] ::' + toReturn)
    
    return toReturn
