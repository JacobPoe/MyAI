import numpy as np

from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

from utils.nlp.enums import PipelineFrameworks
from utils.logger import Logger, LogLevel

log_level: LogLevel = LogLevel.CAPTION

conversation_history: list
model: BlipForConditionalGeneration
processor: BlipProcessor


class Captioner:
    def __init__(self):
        self.conversation_history = []

        # Initialize the processor and model from Hugging Face
        self.processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )
        self.model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )

    def __del__(self):
        Logger.save_log(log_level, self.conversation_history)
        Logger.log(log_level, "Captioner instance destroyed.")

    def analyze_img(self, image: np.ndarray):
        # unconditional image captioning
        inputs = processor(
            image, return_tensors=PipelineFrameworks.PYTORCH.value
        )
        out = self.model.generate(**inputs)
        to_return = self.processor.decode(out[0], skip_special_tokens=False)
        Logger.log(log_level, to_return)
        self.conversation_history.append("[analyze_img] ::" + to_return)

        return to_return

    def caption_img(self, data):
        image = Image.fromarray(data).convert("RGB")

        text = "This is a photo of"
        inputs = self.processor(
            image, text, return_tensors=PipelineFrameworks.PYTORCH.value
        )

        out = self.model.generate(**inputs)
        toReturn = self.processor.decode(out[0], skip_special_tokens=False)
        Logger.log(log_level, toReturn)
        self.conversation_history.append("[caption_img] ::" + toReturn)

        return toReturn
