import React, { useState, useRef } from "react";

const AudioRecorder = (props) => {
    const [recording, setRecording] = useState(false);
    const toggleRecording = async () => {};

    return (
        <div>
            <button onClick={toggleRecording} className="btn btn-primary">
                {recording ? "[STOP]" : `[${props.text}]`}
            </button>
        </div>
    );
};

export default AudioRecorder;