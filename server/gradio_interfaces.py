import os

import gradio as gr

from utils.enums import LogLevel
from utils.logger import Logger

from utils.nlp.captioner import Captioner
from utils.nlp.synthesizer import Synthesizer

SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = os.getenv("SERVER_PORT")
STARTUP_ERROR = "Missing or invalid input parameter. Please provide a valid input.\nAcceptable values are: [chat | caption]"


def launch_captioner():
    captioner = Captioner()
    if captioner is None:
        Logger.log(LogLevel.ERROR, "Captioner failed to launch.")
        return

    demo = gr.Interface(
        fn=captioner.caption_img,
        inputs=gr.Image(),
        outputs="text",
        title="Image Captioning",
        description="Upload an image:",
    )
    demo.launch(server_name=SERVER_HOST, server_port=SERVER_PORT)


def launch_stt():
    demo = gr.Interface(
        fn=Synthesizer.transcribe_audio,
        inputs=gr.Audio(),
        outputs="text",
        title="Speech-to-Text",
        description="Upload an audio file or record one with your onboard microphone:",
    )
    demo.launch(server_name=SERVER_HOST, server_port=SERVER_PORT)


def main():
    is_prompting = True
    while is_prompting:
        print(
            """
        Select a Gradio interface to launch:
        1. Caption
        2. STT
        """
        )

        selection = input("Feature: ")
        if selection == "1":
            launch_captioner()
            is_prompting = False
            break
        elif selection == "2":
            launch_stt()
            is_prompting = False
            break
        else:
            Logger.log(
                LogLevel.ERROR,
                "Invalid selection. Please choose a valid feature.",
            )


if __name__ == "__main__":
    main()
