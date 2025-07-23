import ChatWindow from "./controls/chatWindow";
import InputText from "./controls/input.text";
import Button from "./controls/button";
import {IOService} from "../services/io.service";
import AudioRecorder from "./audio-recorder";
import React, {useState} from "react";
import InputCheckbox from "./controls/input.checkbox";

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
                <Button onClickHandler={() => IOService.postTextPrompt(message)} />
            </div>
            <div className="input-group-append">
                <AudioRecorder
                    callback={() => IOService.postAudioPrompt()}
                    mode="question"
                    text="QUESTION"
                />
                <AudioRecorder
                    callback={() => IOService.postAudioPrompt()}
                    mode="transcribe"
                    text="TRANSCRIBE"
                />
            </div>
        </div>
    )
}

export default Chatbot;