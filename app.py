from transformers import BlipProcessor, BlipForConditionalGeneration
from models.captioner import Captioner as cap
from PIL import Image

import gradio as gr

# Initialize the processor and model from Hugging Face
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

cap = cap(processor, model)

def caption(image):
    raw_image = Image.fromarray(image).convert('RGB')
    return cap.caption_img(raw_image)

demo = gr.Interface(fn=caption, inputs=gr.Image(), outputs="text", title="Image Captioning", description="Upload an image:")

demo.launch(server_name="0.0.0.0", server_port= 7860)