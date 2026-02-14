import React, {useState} from "react";

import { IOService } from "jake-compoenents/dist/services/io.service";

import AudioRecorder from "jake-compoenents/dist/components/controls/audio-recorder/audio-recorder";
import Checkbox from "jake-compoenents/dist/components/controls/input/checkbox/checkbox";
import Text from "jake-compoenents/dist/components/controls/input/text/text";
import Button from "jake-compoenents/dist/components/controls/button/button";

import "./chatbot.css";
import ChatWindow from "../views/chat-window/chat-window";
import { HTTPService } from "../../services/http.service";

const ttsWarningMsg = "Request TTS replies (this will significantly increase response times and resource consumption).";
const recorderLabelTranscribe = "Transcribe audio to text only (no chatbot response).";
const recorderLabelTalk = "Record audio using your system microphone and get a chatbot response.";

const Chatbot = (props) => {
    const [message, setMessage] = React.useState("");
    const [messages, setMessages] = React.useState([]);
    const [requestNarratedResponses, setRequestNarratedResponses] = useState(false);

    const submitTextPrompt = async () => {
        setMessages(prevMessages => [...prevMessages, {text: message, type: 'user'}]);
        setMessage("");

        await HTTPService.post({
                endpoint: 'api/v1/tts',
                params: {
                    "narrateResponse": props.requestNarratedResponses || false,
                    "mode": props.mode || "question"
                },
                formData: {
                    "userMessage": props.message || ""
                }
            }).then(async (response) => {
            if (response.audio) {
                await IOService.handleAudioPlayback(response);
            }
        })
    }

    const postAudioPrompt = async (blob, props) => {
        const response = await HTTPService.post({
            endpoint: "api/v1/asr",
            body: blob,
            headers: {
                "Content-Type": "audio/webm; codecs=opus"
            },
            params: {
                "narrateResponse": props.requestNarratedResponses || false,
                "mode": props.mode || "question"
            }
        }).then(async (response) => {
            if (response.audio) {
                await IOService.handleAudioPlayback(response);
            }
        })

        return {
            text: response.reply || "",
            transcription: response.transcription || "",
        }
    };

    return (
        <div id={ props.id ? props.id : '' + "--chatbot-view" }>
            <ChatWindow id={props.id} messages={messages} />
            <div className={"prompt-container"}>
                <div className={"row post-prompt__text"}>
                    <Text id={"prompt-chatbot"} text={message} onChangeHandler={setMessage} />
                    <Button id={"post-prompt__text"} onClickHandler={submitTextPrompt} text={"Send ⮚"} />
                    <AudioRecorder
                        id={"post-prompt__audio__question"}
                        requestNarratedResponses={requestNarratedResponses}
                        setMessagesRef={setMessages}
                        postAudioPromptCallback={postAudioPrompt}
                        mode="question"
                        text="TALK"
                        buttonLabel={recorderLabelTalk}
                    />
                    <AudioRecorder
                        id={"post-prompt__audio__transcribe"}
                        requestNarratedResponses={requestNarratedResponses}
                        setMessagesRef={setMessages}
                        postAudioPromptCallback={postAudioPrompt}
                        mode="transcribe"
                        text="TRANSCRIBE"
                        buttonLabel={recorderLabelTranscribe}
                    />
                    <div className={"row-right post-prompt__tts"}>
                        <Checkbox
                            id={"request-narrated-responses"}
                            action={"TTS"}
                            alignment={"right"}
                            checked={requestNarratedResponses}
                            onChangeHandler={setRequestNarratedResponses}
                            label={ttsWarningMsg}
                            type={"checkbox"}
                        />
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Chatbot;