import os

import gradio as gr

from enums.enums import LogLevel
from logging.logger import Logger

from nlp.captioner import Captioner
from nlp.chatbot import Chatbot
from nlp.translator import Translator

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


def launch_chatbot():
    chatbot = Chatbot()
    if chatbot is None:
        Logger.log(LogLevel.ERROR, "Chatbot failed to launch.")
        return

    demo = gr.Interface(
        fn=chatbot.generate_reply,
        inputs=gr.Textbox(),
        outputs="text",
        title="Chatbot",
        description="Input prompt:",
    )
    demo.launch(server_name=SERVER_HOST, server_port=SERVER_PORT)


def launch_stt():
    demo = gr.Interface(
        fn=Translator.transcribe_audio,
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
        2. Chat
        3. STT
        """
        )

        selection = input("Feature: ")
        if selection == "1":
            launch_captioner()
            is_prompting = False
            break
        elif selection == "2":
            launch_chatbot()
            is_prompting = False
            break
        elif selection == "3":
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
