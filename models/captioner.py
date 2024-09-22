import numpy as np

from transformers import BlipProcessor, BlipForConditionalGeneration

from enums.logger import LogLevel
from utils.logger import Logger

log_level: LogLevel = LogLevel.CAPTION

logger: Logger
model: BlipForConditionalGeneration
processor: BlipProcessor

class Captioner:
  def __init__(self, logger: Logger):
  # Initialize the processor and model from Hugging Face
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    self.logger = logger
    self.model = model
    self.processor = processor

  def caption_img(self, image: np.ndarray):
    text = 'This is a photo of'
    inputs = self.processor(image, text, return_tensors='pt')

    out = self.model.generate(**inputs)
    toReturn = self.processor.decode(out[0], skip_special_tokens=True)
    logger.log(log_level, toReturn)
    
    return toReturn

  def analyze_image(self, image: np.ndarray):
    # unconditional image captioning
    inputs = processor(image, return_tensors="pt")
    out = self.model.generate(**inputs)
    toReturn = self.processor.decode(out[0], skip_special_tokens=True)
    self.logger.log(log_level, toReturn)

    return toReturn
