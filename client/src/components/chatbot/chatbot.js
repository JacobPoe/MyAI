import React, {useState} from "react";

import { IOService } from "../../services/io.service";

import AudioRecorder from "../controls/audio-recorder/audio-recorder";
import ChatWindow from "../views/chat-window/chat-window";
import Checkbox from "../controls/input/checkbox/checkbox";
import Text from "../controls/input/text/text";
import Button from "../controls/button/button";

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
                setMessages(prevMessages => [...prevMessages, {text: response.text, type: 'bot'}]);
            })
    }

    return (
        <div id={ props.id ? props.id : '' + "--chatbot-view" } className="row">
            <ChatWindow id={props.id} messages={messages} />
            <Checkbox
                checked={requestNarratedResponses}
                onChangeHandler={setRequestNarratedResponses}
                label={ttsWarningMsg}
            />
            <div className="">
                <Text id={"prompt-chatbot"} text={message} onChangeHandler={setMessage} />
                <Button onClickHandler={submitTextPrompt} />
            </div>
            <div className="">
                <AudioRecorder requestNarratedResponses={requestNarratedResponses} setMessagesRef={setMessages} mode="question" text="QUESTION" />
                <AudioRecorder requestNarratedResponses={requestNarratedResponses} setMessagesRef={setMessages} mode="transcribe"  text="TRANSCRIBE" />
            </div>
        </div>
    )
}

export default Chatbot;