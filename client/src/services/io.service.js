import { HTTPService } from "./http.service";

const handleAudioPlayback = async (data) => {
    const df = document.createDocumentFragment();
    const blob = data.blob ? data.blob : new Blob([Uint8Array.from(atob(data.audio), c => c.charCodeAt(0))]);
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);

    df.appendChild(audio); // keep in fragment until finished playing
    audio.addEventListener("ended", function () {
        df.removeChild(audio);
    });
    audio.play().catch(error => console.error('Error playing audio:', error));
    return audio;
};

const postTextPrompt = async (props) => {
    const response = await HTTPService.post({
        endpoint: 'api/v1/tts',
        params: {
            "narrateResponse": props.requestNarratedResponses || false,
            "mode": props.mode || "question"
        },
        formData: {
            "userMessage": props.message || ""
        }
    });

    if (response.audio) {
        await handleAudioPlayback(response);
    }

    return {
        text: response.reply || ""
    };
};

const postAudioPrompt = async (data, props) => {
    console.log(`postAudioPrompt data:`, data)
    const response = await HTTPService.post({
        endpoint: "api/v1/asr",
        body: data,
        headers: {
            "Content-Type": "audio/webm"
        },
        params: {
            "narrateResponse": props.requestNarratedResponses || false,
            "mode": props.mode || "question"
        }
    });

    if (response.audio) {
        await handleAudioPlayback(response);
    }

    return {
        text: response.reply || "",
        transcription: response.transcription || "",
    }
};

const startRecordingAudio = async (audioChunksRef, mediaRecorderRef) => {
    return navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
        mediaRecorderRef.current = new MediaRecorder(stream);
        if (!mediaRecorderRef.current) {
            throw new Error("MediaRecorder is not supported in this browser.");
        }

        mediaRecorderRef.current.ondataavailable = (event) => {
            const audioRefData = audioChunksRef.current || [];
            audioRefData.push(event.data);
            audioChunksRef.current = audioRefData;
        }

        mediaRecorderRef.current.onstart = () => {
            audioChunksRef.current = [];
        }

        mediaRecorderRef.current.onstop = () => {
            const audioRefData = audioChunksRef.current || [];
            audioChunksRef.current = new Blob(audioRefData);

            // // TODO: Great global debug flag to control this
            // // play back audio for debugging purposes
            // await handleAudioPlayback({ blob: blob })
            //     .catch(error => console.error('Error playing audio:', error));

            // Stop all tracks in the stream
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorderRef.current.start(10);
    }).catch(error => {
        console.error("Error accessing media devices:", error);
        throw error;
    });
};

const stopRecordingAudio = (mediaRecorderRef) => {
    return new Promise((resolve) => {
        mediaRecorderRef.current.stop();

        resolve();
    })
};

export const IOService = {
    postAudioPrompt,
    postTextPrompt,
    startRecordingAudio,
    stopRecordingAudio
};