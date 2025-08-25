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

const postAudioPrompt = async (blob, props) => {
    const response = await HTTPService.post({
        endpoint: "api/v1/asr",
        body: blob,
        headers: {
            "Content-Type": "audio/webm; codecs=opus"
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
        const defaultMimeType = 'audio/webm;codecs=opus';
        const mimeType = (
            window.MediaRecorder &&
            MediaRecorder.isTypeSupported &&
            MediaRecorder.isTypeSupported(defaultMimeType)
        )
            ? defaultMimeType
            : undefined;

        mediaRecorderRef.current =
            new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
        if (!mediaRecorderRef.current) {
            throw new Error("MediaRecorder is not supported in this browser.");
        }

        mediaRecorderRef.current.start(500);
    }).catch(error => {
        console.error("Error accessing media devices:", error);
        throw error;
    });
};

const stopRecordingAudio = (mediaRecorderRef, audioChunksRef) => {
    return new Promise((resolve) => {
        const onStop = () => {
            const chunks = audioChunksRef?.current || [];
            const type = mediaRecorderRef.current.mimeType || 'audio/webm;codecs=opus';
            const blob = new Blob(chunks, { type });

            // // TODO: Great global debug flag to control this
            // // play back audio for debugging purposes
            // await handleAudioPlayback({ blob: blob })
            //     .catch(error => console.error('Error playing audio:', error));

            resolve(blob);
        };

        mediaRecorderRef.current.addEventListener('stop', onStop, { once: true });
        mediaRecorderRef.current.stop();
    })
};

export const IOService = {
    postAudioPrompt,
    postTextPrompt,
    startRecordingAudio,
    stopRecordingAudio
};