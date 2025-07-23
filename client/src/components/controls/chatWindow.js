import React, {useState} from "react";
import InputCheckbox from "./input.checkbox";

const ChatWindow = (props) => {
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
        </div>
    )
}

export default ChatWindow;