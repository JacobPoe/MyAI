import React, {useState} from "react";
import Checkbox from "../../controls/input/checkbox/checkbox";

const ChatWindow = (props) => {
    return (
        <div className="col-12">
            <div id="chat-window">
                {props.messages?.map((msg, index) => (
                    <div key={index} className={`row message-line ${msg.type}`}>
                        {msg.text && (
                            <div className={`message-box ${msg.type === "bot" ? "bot-text" : ""}`}>
                                {msg.text}
                            </div>
                            )
                        }
                        {msg.transcription && (
                            <div className={`transcription-box ${msg.type === "bot" ? "bot-text" : ""}`}>
                                <strong>Transcription:</strong> {msg.transcription}
                            </div>
                            )
                        }
                    </div>
                ))}
            </div>
        </div>
    )
}

export default ChatWindow;