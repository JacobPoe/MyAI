# MyAI

This project began as a way to document my progression through the IBM AI Developer certification course. As the course
progressed, I realized that the manner in which the course conducted many of its labs was not an optimal format. The
labs were performed inside in-browser virtual IDEs with no way to reference your past work. Additionally, I felt that
the labs could all be leveraged as opportunities to build out an entire AI application with multiple features, not just
a simple one-dimensional chatbot application.

With this in mind I built on my original app.py and implemented the following:

- A custom logger that can:
  - log informational messages to the console
  - save an array of logs to a file.
    - This is with the intention of maintaining a conversation history between the user and the chatbot.
    - This directory is added to the .gitignore with the intention of keeping the user's conversation history private.
- Implement a Flask server to handle all interactions with different AI models and APIs
- Implement a React frontend
  - This initiative began in response to a lab around building a speech-to-text/text-to-speech application. I took the starter code from the lab and refactored it from a pure Javascript/HTML application that was far more readable and maintainable.

# How to start the project:

- TODO: Section about starting the web client
  - install npm
  - `npm install`
  - `npm run start`
- TODO: Section about starting the server
  - install python
  - set up python venv
  - pip install -r requirements.txt
- TODO: Section about Docker deployment

# Environment Variables

| Key                       | ExampleValue     | Description                                                     |
| ------------------------- | ---------------- | --------------------------------------------------------------- |
| DEBUG                     | True             | Enable or disable debug mode.                                   |
| SERVER_HOST               | 0.0.0.0          | Server address where local app is hosted.                       |
| SERVER_PORT               | 1587             | Port number for your local application instance.                |
| ROUTE_ASR                 | /api/v1/asr      | Endpoint for automatic-speech-recognition API.                  |
| ROUTE_TTS                 | /api/v1/tts      | Endpoint for text-to-speech API.                                |
| ROUTE_TRAINING_INIT       | /api/v1/training | Endpoint to initialize training loop for user defined datasets. |
| STT_COMPUTATION_DEVICE    | cpu              | Device index for stt computation (e.g., GPU).                   |
| STT_SAMPLE_RATE           | 16000            | Sample rate for speech-to-text processing.                      |
| MAX_LENGTH                | 512              | Max number of tokens to generate when generating response.      |
| TRAINING_ARGS_NUM_EPOCHS  | 3                | Number of training cycles to execute when training local model. |
| PRETRAINED_MODEL_DIR      | C:/models        | Where on your local filesystem to save your trained models.     |
| SELECTED_PRETRAINED_MODEL | my_example_model | User-defined name of the model being trained.                   |

# Datasets.json

`datasets.json` is a configuration file designed to streamline the importation of multiple datasets at run time. At a high level, each entry takes the following structure:

```
{
	name: string, // Human-readable name of the dataset.
	hf_id: string, // The ID of the dataset in Hugging Face's datasets repo.
	pattern: string, // The pattern to be used to format the dataset prior to tokenization.
	columns: string[], // The dataset's column keys, used to build the prompt input along with pattern.
	config_type: "main" | "socratic", // Required second param when calling load_dataset() for GSM8K
	reference: obj // An object containing citation data for the dataset. Provided for credit and reference.
	split: "train" | "test" // Which portion of the dataset to use for building the model
}
```

This project uses the following datasets as its baseline training data. Its import configuration can be referenced in the file `server/datasets.json`.

- [ByteDance-Seed/WideSearch](https://huggingface.co/datasets/ByteDance-Seed/WideSearch)
- [datasets-examples/doc-formats-csv-1](https://huggingface.co/datasets/datasets-examples/doc-formats-csv-1)
- [fka/awesome-chatgpt-prompts](https://huggingface.co/datasets/fka/awesome-chatgpt-prompts)
- [openai/gsm8k](https://huggingface.co/datasets/openai/gsm8k/)

# System requirements
- [Cuda System Toolkit](https://developer.nvidia.com/cuda-downloads)
- [CUDA-compatible PyTorch](https://pytorch.org/)
  - Including `pytorch` in `requirements.txt` by default installs the PyTorch build which is only compatible with the CPU.

# References

## Projects

- [Hugging Face Kernel Hub](https://huggingface.co/kernels-community)

  - [Intro wiki](https://huggingface.co/blog/hello-hf-kernels)

Have fun!
