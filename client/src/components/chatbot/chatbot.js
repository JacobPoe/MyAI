import React, {useState} from "react";

import { IOService } from "../../services/io.service";

import AudioRecorder from "../controls/audio-recorder/audio-recorder";
import ChatWindow from "../views/chat-window/chat-window";
import Checkbox from "../controls/input/checkbox/checkbox";
import Text from "../controls/input/text/text";
import Button from "../controls/button/button";

import "./chatbot.css";

const ttsWarningMsg = "Request TTS replies (this will significantly increase response times and resource consumption).";

const Chatbot = (props) => {
    const [message, setMessage] = React.useState("");
    const [messages, setMessages] = React.useState([]);
    const [requestNarratedResponses, setRequestNarratedResponses] = useState(false);

    const submitTextPrompt = async () => {
        setMessages(prevMessages => [...prevMessages, {text: message, type: 'user'}]);
        setMessage("");
        await IOService.postTextPrompt({message, requestNarratedResponses})
            .then((response) => {
                setMessages(prevMessages => [...prevMessages, {text: response.text, type: 'system'}]);
            })
    }

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
                        mode="question"
                        text="TALK"
                    />
                    <AudioRecorder
                        id={"post-prompt__audio__transcribe"}
                        requestNarratedResponses={requestNarratedResponses}
                        setMessagesRef={setMessages}
                        mode="transcribe"
                        text="TRANSCRIBE"
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