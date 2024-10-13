import React, { useState, useEffect, useRef } from "react";
import { createRoot } from "react-dom/client";

const VoiceAssistant = () => {
  const [message, setMessage] = useState("");
  const [recording, setRecording] = useState(false);
  const [voiceOption, setVoiceOption] = useState("default");
  const [lightMode, setLightMode] = useState(true);
  const [messages, setMessages] = useState([]);
  const [loadingUser, setLoadingUser] = useState(false);
  const [loadingBot, setLoadingBot] = useState(false);
  const recorderRef = useRef(null);
  const baseUrl = window.location.origin;

  const toggleLightMode = () => setLightMode(!lightMode);

  const cleanTextInput = (value) => {
    return value
      .trim()
      .replace(/[\n\t]/g, "")
      .replace(/<[^>]*>/g, "")
      .replace(/[<>&;]/g, "");
  };

  const handleSendMessage = async () => {
    if (message.trim()) {
      setMessages([...messages, { type: "user", content: message }]);
      setMessage(""); // Clear input
      await populateBotResponse(message, "TTS");
    }
  };

  const toggleRecording = async () => {
    if (!recording) {
      // Start recording
      recorderRef.current = await recordAudio();
      recorderRef.current.start();
      setRecording(true);
    } else {
      // Stop recording and process audio
      const audio = await recorderRef.current.stop();
      const userMessage = await getSpeechToText(audio);
      setMessages([...messages, { type: "user", content: userMessage }]);
      await populateBotResponse(userMessage, "STT");
      setRecording(false);
    }
  };

  const getSpeechToText = async (userRecording) => {
    const response = await fetch(`${baseUrl}/speech-to-text`, {
      method: "POST",
      body: userRecording.audioBlob,
      headers: { "Content-Type": "audio/mpeg" },
    });
    const data = await response.json();
    return data.text;
  };

  const populateBotResponse = async (userMessage, inputType) => {
    setLoadingBot(true);
    const payload = inputType === "TTS" ? JSON.stringify({ userMessage, voice: voiceOption }) : userMessage;
    const headers = inputType === "TTS" ? { "Content-Type": "application/json" } : { "Content-Type": "audio/mpeg"};
    const response = await fetch(`${baseUrl}/text-to-speech`, {
      method: "POST",
      body: payload,
      headers,
    });
    const data = await response.json();
    setMessages((prevMessages) => [...prevMessages, { type: "bot", content: data.text }]);
    setLoadingBot(false);
  };

  return (
    <>
      <div className={`myai-container ${lightMode ? "light-mode" : "dark-mode"}`}>
      <div className="row">
        <div className="col-12 text-center">
          <h1>Voice Assistant</h1>
          <p>Your personal assistant powered by Suno's TTS model.</p>
          <div>
            <label>
              <input type="checkbox" checked={lightMode} onChange={toggleLightMode} /> Toggle light/dark mode
            </label>
          </div>
        </div>

        <div className="col-12 col-md-8 mx-auto">
          <div id="chat-window">
            {messages.map((msg, index) => (
              <div key={index} className={`message-line ${msg.type}`}>
                <div className={`message-box ${msg.type === "bot" ? "bot-text" : "my-text"}`}>
                  {msg.content}
                </div>
              </div>
            ))}
            {loadingBot && <div>Bot is typing...</div>}
          </div>

          <div className="input-group mt-1">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(cleanTextInput(e.target.value))}
              className="form-control"
              placeholder="Type your message here..."
            />
            <div className="input-group-append">
              <button onClick={toggleRecording} className="btn btn-primary">
                {recording ? <i className="fa fa-stop"></i> : <i className="fa fa-microphone"></i>}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    </>
  );
};

// Helper functions outside the component
const recordAudio = () => {
  return new Promise(async (resolve, reject) => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const audioChunks = [];

      mediaRecorder.addEventListener("dataavailable", (event) => {
        audioChunks.push(event.data);
      });

      const start = () => mediaRecorder.start();
      const stop = () =>
        new Promise((resolve) => {
          mediaRecorder.addEventListener("stop", () => {
            const audioBlob = new Blob(audioChunks, { type: audioChunks[0].type });
            const audioUrl = URL.createObjectURL(audioBlob);
            resolve({ audioBlob, audioUrl });
          });
          mediaRecorder.stop();
        });

      resolve({ start, stop });
    } catch (error) {
      console.error("Error accessing microphone:", error);
      reject(error);
    }
  });
};

const container = document.getElementById("root");
const root = createRoot(container);
root.render(<VoiceAssistant />);
