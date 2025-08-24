import React, { useState, useRef } from "react";

import Button from "../button/button";

import { IOService } from "../../../services/io.service";

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
                IOService.stopRecordingAudio(mediaRecorderRef, audioChunksRef);
                await IOService.postAudioPrompt(audioChunksRef.current,
                    {
                        mode: props.mode,
                        requestNarratedResponses: props.requestNarratedResponses
                    }).then((response) => {
                        props.setMessagesRef(prevMessages => [...prevMessages, {text: response.text, transcription: response.transcription, type: 'bot'}])
                });
            } else {
                await IOService.startRecordingAudio(mediaRecorderRef, audioChunksRef);
            }
        }
    }

    return (
        <div className={"audio-recorder__" + props.id}>
            <Button
                id={"audio-recorder__" + props.id}
                type={"icon"}
                onClickHandler={async () => await toggleRecording()}
                text={recording ? "STOP ⭕" : `${props.text} 🎤`}
                label={props.buttonLabel ? props.buttonLabel : ''}
            />
        </div>
    );
};

export default AudioRecorder;