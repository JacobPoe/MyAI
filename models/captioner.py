from transformers import BlipProcessor, BlipForConditionalGeneration

import numpy as np

processor: BlipProcessor
model: BlipForConditionalGeneration

class Captioner:
  def __init__(self, processor: BlipProcessor, model: BlipForConditionalGeneration):
    self.processor = processor
    self.model = model

  def caption_img(self, image: np.ndarray):
    text = 'This is a photo of'
    inputs = self.processor(image, text, return_tensors='pt')

    out = self.model.generate(**inputs)
    toReturn = self.processor.decode(out[0], skip_special_tokens=True)
    print('[models.Captioner::caption_img()]\t'+ toReturn, type(toReturn))
    
    return toReturn

  def analyze_image(self, image: np.ndarray):
    # unconditional image captioning
    inputs = processor(image, return_tensors="pt")
    out = self.model.generate(**inputs)
    toReturn = self.processor.decode(out[0], skip_special_tokens=True)
    print('[models.Captioner::analyze_image()]\t'+ toReturn, type(toReturn))

    return toReturn
