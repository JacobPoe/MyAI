import React, { useState, useRef } from "react";

import { HTTPService } from "../services/http.service";
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
                        await HTTPService.post({
                            baseUrl: props.baseUrl || 'http://localhost:1587',
                            endpoint: "api/v1/asr",
                            body: data,
                            params: {
                                "narrateResponse": props.requestNarratedResponses || false,
                                "mode": props.mode || "question"
                            }
                        });
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