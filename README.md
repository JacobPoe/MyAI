# MyAI
This project began as a way to document my progression through the IBM AI Developer certification course. As the course
progressed, I realized that the manner in which the course conducted many of its labs was not an optimal format. The 
labs were performed inside in-browser virtual IDEs with no way to reference your past work. Additionally, I felt that
the labs could all be leveraged as opportunities to build out an entire AI application with multiple features, not just
a simple one-dimensional chatbot application.

With this in mind I built on my original app.py and implemented the following:
* A custom logger that can:
  * log informational messages to the console
  * save an array of logs to a file. 
    * This is with the intention of maintaining a conversation history between the user and the chatbot.
    * This directory is added to the .gitignore with the intention of keeping the user's conversation history private.
* Implement a Flask server to handle all interactions with different AI models and APIs
* Implement a React frontend
  * This initiative began in response to a lab around building a speech-to-text/text-to-speech application. I took the starter code from the lab and refactored it from a pure Javascript/HTML application that was far more readable and maintainable.

# How to start the project:
* TODO: Section about starting the web client
* TODO: Section about starting the server
* TODO: Section about Docker deployment

# Environment Variables
| Key                     | Value                                                                                                                           | Description                                                                |
|-------------------------|---------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| SERVER_HOST             | 0.0.0.0                                                                                                                         | Server address where local app is hosted                                   |
| SERVER_PORT             | 1587                                                                                                                            | Port number for your local application instance                            |


# NOTE: /src/gradio

This directory serves as one giant TODO

The IBM AI Developer certification course often conducts its labs via Gradio interfaces. This directory is meant to
serve as a container for all the different Gradio exercises the course has offered, with the intention of refactoring 
these Gradio interfaces into React components in the future. 

To run any Gradio project
In the root folder of the project run one of the following two commands:

A) `python server/src/gradio/app_gradio.py caption`

- This server is capable of accepting an image as an input and outputting a simple description of that image

B) `python server/src/gradio/app_gradio.py chat`

- This command will activate a chatbot built using OpenAI Community's GPT2-Large model
- src: https://huggingface.co/openai-community/gpt2-large

Once the chosen application is running, navigate to `http://0.0.0.0:1587`.

Have fun!