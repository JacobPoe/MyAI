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
| Key                    | Value                                                 | Description                                     |
|------------------------|-------------------------------------------------------|-------------------------------------------------|
| DEBUG                  | True                                                  | Enable or disable debug mode                    |
| SERVER_HOST            | 0.0.0.0                                               | Server address where local app is hosted        |
| SERVER_PORT            | 1587                                                  | Port number for your local application instance |
| ROUTE_ASR              | /api/v1/ASR                                           | Endpoint for automatic-speech-recognition API                 |
| ROUTE_TTS              | /api/v1/tts                                           | Endpoint for text-to-speech API                 |
| STT_COMPUTATION_DEVICE | cpu                                                   | Device index for stt computation (e.g., GPU)    |
| STT_SAMPLE_RATE        | 16000                                                 | Sample rate for speech-to-text processing       |

Have fun!