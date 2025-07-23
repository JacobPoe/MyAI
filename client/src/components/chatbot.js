import ChatWindow from "./controls/chatWindow";
import InputText from "./controls/input.text";
import Button from "./controls/button";
import {IOService} from "../services/io.service";
import AudioRecorder from "./audio-recorder";
import React from "react";

const Chatbot = (props) => {
    const [message, setMessage] = React.useState("");
    const [messages, setMessages] = React.useState([]);
    return (
        <div id={ props.id ? props.id : '' + "--chatbot-view" } className="row">
            <ChatWindow id={props.id} messages={messages} />
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