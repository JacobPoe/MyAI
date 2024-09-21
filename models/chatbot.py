from transformers import GPT2Tokenizer, GPT2Model, pipeline, set_seed

generator: pipeline
model: GPT2Model
tokenizer: GPT2Tokenizer

# TODO: Type
output = None

class Chatbot:
  def __init__(self):
    print('[models.Chatbot::__init__()] Chatbot initialized')

    tokenizer = GPT2Tokenizer.from_pretrained('gpt2-xl')
    model = GPT2Model.from_pretrained('gpt2-xl')

    text = "My first prompt to you is: what does this input parameter do?"
    encoded_input = tokenizer(text, return_tensors='pt')
    output = model(**encoded_input)

    self.output = output
    self.tokenizer = tokenizer
    self.model = model

    generator = pipeline('text-generation', model='gpt2-xl')
    set_seed(42)
    generator("Hello, I'm a language model,", max_length=30, num_return_sequences=5)
    self.generator = generator
