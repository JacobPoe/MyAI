import React from "react";
import "./chat-window.css";

const ChatWindow = ({ messages = [] }) => {
    return (
        <section className="chat-window">
            <div className="messages" role="list" aria-label="Conversation">
                {messages.map((m, i) => (
                    <article key={i} className={`chat-bubble ${m.role}`} role="listitem">
                        <div className="message-body">{m.text}</div>
                        <div className="message-meta">
                            <span className="role-pill">{m.role}</span>
                            {m.ts ? (
                                <time className="timestamp" dateTime={new Date(m.ts).toISOString()}>
                                    {new Date(m.ts).toLocaleTimeString()}
                                </time>
                            ) : null}
                        </div>
                    </article>
                ))}
            </div>
        </section>
    );
};

export default ChatWindow;
