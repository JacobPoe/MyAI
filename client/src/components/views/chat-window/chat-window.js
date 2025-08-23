import React from "react";

import "./chat-window.css";

const ChatWindow = (props) => {
    return (
        <div className="chat-window">
            {props.messages?.map((msg, index) => {
                return (
                    <div key={index} className={`chat-bubble chat-bubble__${msg.type}`}>
                        {msg.text && (
                            <span>
                                {msg.text}
                            </span>
                        )
                        }
                        {msg.transcription && (
                            <span>
                                <strong>Transcription:</strong> {msg.transcription}
                            </span>
                        )
                        }
                    </div>
                );
            })}
        </div>
    )
}

export default ChatWindow;