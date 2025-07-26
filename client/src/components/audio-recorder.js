import React, { useState, useRef } from "react";

import { IOService } from "../services/io.service";

const AudioRecorder = (props) => {
    const [recording, setRecording] = useState(false);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    const toggleRecording = async () => {
        if (!navigator.mediaDevices.getUserMedia) {
            alert("Unable to access media devices.")
            setRecording(false);
            return undefined;
        } else {
            setRecording((prevRecording) => !prevRecording);
            if (recording) {
                await IOService.stopRecordingAudio(mediaRecorderRef, audioChunksRef)
                    .then(async (data) => {
                        if (data.size === 0) {
                            alert("No audio recorded.");
                            setRecording(false);
                            return;
                        }
                        await IOService.postAudioPrompt(data,
                            {
                                mode: props.mode,
                                requestNarratedResponses: props.requestNarratedResponses
                            }).then((response) => {
                                props.setMessagesRef(prevMessages => [...prevMessages, {text: response.text, transcription: response.transcription, type: 'bot'}])
                        })
                    });
            } else {
                await IOService.startRecordingAudio(mediaRecorderRef, audioChunksRef);
            }
        }
    }

    return (
        <div>
            <button onClick={async () => await toggleRecording()} className="btn btn-primary">
                {recording ? "[STOP]" : `[${props.text}]`}
            </button>
        </div>
    );
};

export default AudioRecorder;