# How to start the project:

In the root folder of the project (the folder where app.py lives), run one of the following two commands:

A) `python gradio/app_gradio.py caption`

- This server is capable of accepting an image as an input and outputting a simple description of that image

B) `python gradio/app_gradio.py chat`

- This command will activate a chatbot built using OpenAI Community's GPT2-Large model
- src: https://huggingface.co/openai-community/gpt2-large

Once the chosen application is running, navigate to `http://0.0.0.0:1587`.

Have fun!
