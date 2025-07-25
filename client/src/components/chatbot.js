import React, {useState} from "react";

import { IOService } from "../services/io.service";

import AudioRecorder from "./audio-recorder";
import ChatWindow from "./controls/chatWindow";
import InputCheckbox from "./controls/input.checkbox";
import InputText from "./controls/input.text";
import Button from "./controls/button";

const ttsWarningMsg = "Request TTS replies (this will significantly increase response times and resource consumption).";

const Chatbot = (props) => {
    const [message, setMessage] = React.useState("");
    const [messages, setMessages] = React.useState([]);
    const [requestNarratedResponses, setRequestNarratedResponses] = useState(false);

    return (
        <div id={ props.id ? props.id : '' + "--chatbot-view" } className="row">
            <ChatWindow id={props.id} messages={messages} />
            <InputCheckbox
                checked={requestNarratedResponses}
                onChangeHandler={setRequestNarratedResponses}
                label={ttsWarningMsg}
            />
            <div className="input-group mt-1">
                <InputText id={"prompt-chatbot"} text={message} onChangeHandler={setMessage} />
                <Button onClickHandler={async () => {
                    setMessages(prevMessages => [...prevMessages, {text: message, type: 'user'}]);
                    setMessage("");
                    await IOService.postTextPrompt({message, requestNarratedResponses})
                        .then((response) => {
                            setMessages(prevMessages => [...prevMessages, {text: response, type: 'bot'}]);
                        })
                }} />
            </div>
            <div className="input-group-append">
                <AudioRecorder mode="question" text="QUESTION" />
                <AudioRecorder mode="transcribe"  text="TRANSCRIBE" />
            </div>
        </div>
    )
}

export default Chatbot;