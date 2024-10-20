import React, { useState, useRef } from "react";
import { createRoot } from "react-dom/client";

const VoiceAssistant = () => {
  const [message, setMessage] = useState("");
  const [recording, setRecording] = useState(false);
  const [voiceOption, setVoiceOption] = useState("default");
  const [lightMode, setLightMode] = useState(true);
  const [messages, setMessages] = useState([]);
  const [loadingBot, setLoadingBot] = useState(false);
  const recorderRef = useRef(null);
  const baseUrl = window.location.origin;

  const handleAudioInput = async (userRecording) => {
    const response = await fetch(`${baseUrl}/speech-to-text`, {
      method: "POST",
      body: userRecording.audioBlob,
      headers: { "Content-Type": "audio/mpeg" },
    });
    const data = await response.json();
    setMessages([...messages, { type: "transcription", content: data.text }]);
  };

  const handleAudioPlayback = async (data) => {
    const df = document.createDocumentFragment();
    const blob = await data.blob();
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);

    df.appendChild(audio); // keep in fragment until finished playing
    audio.addEventListener("ended", function () {
      df.removeChild(audio);
    });
    audio.play().catch(error => console.error('Error playing audio:', error));
    return audio;
  }

  const handleTextInput = async () => {
    setMessages([...messages, { type: "user", content: message }]);
    setLoadingBot(true);

    const response = await fetch(`${baseUrl}/text-to-speech`, {
      method: "POST",
      body: JSON.stringify({ userMessage: message, voice: voiceOption }),
      headers: { "Content-Type": "application/json" },
    });

    await handleAudioPlayback(response);
    setLoadingBot(false);
    setMessage(""); // Clear input
  };

  const sanitize = (value) => {
    return value
      .replace(/[\n\t]/g, "")
      .replace(/<[^>]*>/g, "")
      .replace(/[<>&;]/g, "");
  };
  const toggleLightMode = () => setLightMode(!lightMode);
  const toggleRecording = async () => {
    const isRecording = !recording;
    setRecording(isRecording);

    if (!recording) {
      // Start recording
      recorderRef.current = await recordAudio();
      recorderRef.current.start();
    } else {
      // Stop recording and process audio
      const audio = await recorderRef.current.stop();
      await handleAudioInput(audio);
    }
  };

  return (
    <>
      <div className={`myai-container ${lightMode ? "light-mode" : "dark-mode"}`}>
        <div className="row">
          <div className="col-12 text-center">
            <h1>Voice Assistant</h1>
            <p>Your personal assistant powered by Suno's TTS model on <a href="https://huggingface.co/suno/bark">HuggingFace</a>.</p>
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
                  <div className={`message-box ${msg.type === "bot" ? "bot-text" : ""}`}>
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
                  onChange={(e) => setMessage(sanitize(e.target.value))}
                  className="form-control"
                  placeholder="Type your message here..."
              />
              <div className="input-group-append">
                <button onClick={handleTextInput} className="btn btn-primary">
                  Send
                </button>
              </div>

              <button onClick={toggleRecording} className="btn btn-primary">
                {recording ? <i className="fa fa-stop">[STOP]</i> : <i className="fa fa-microphone">[START]</i>}
              </button>
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
