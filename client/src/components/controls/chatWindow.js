import React, {useState} from "react";
import InputCheckbox from "./input.checkbox";

const ttsWarningMsg = "Request TTS replies (this will significantly increase response times and resource consumption).";

const ChatWindow = (props) => {
    const [requestNarratedResponses, setRequestNarratedResponses] = useState(false);
    return (
        <div className="col-12">
            <div id="chat-window">
                {props.messages?.map((msg, index) => (
                    <div key={index} className={`message-line ${msg.type}`}>
                        <div className={`message-box ${msg.type === "bot" ? "bot-text" : ""}`}>
                            {msg.content}
                        </div>
                    </div>
                ))}
            </div>

            <InputCheckbox
                checked={requestNarratedResponses}
                onChangeHandler={setRequestNarratedResponses}
                label={ttsWarningMsg}
            />
        </div>
    )
}

export default ChatWindow;