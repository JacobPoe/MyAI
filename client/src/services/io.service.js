import { HTTPService } from "./http.service";

const handleAudioPlayback = async (data) => {
    const df = document.createDocumentFragment();
    const blob = new Blob([Uint8Array.from(atob(data), c => c.charCodeAt(0))], { type: 'audio/wav' });
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);

    df.appendChild(audio); // keep in fragment until finished playing
    audio.addEventListener("ended", function () {
        df.removeChild(audio);
    });
    audio.play().catch(error => console.error('Error playing audio:', error));
    return audio;
};

const postTextPrompt = async (data) => {
    const response = await HTTPService.post({
        endpoint: '/api/v1/tts',
        body: JSON.stringify({ userMessage: data.message, narrateResponse: data.requestNarratedResponses, mode: "question" }),
        headers: { "Content-Type": "application/json" }
    });

    if (response.audio) {
        await IOService.handleAudioPlayback(response.audio);
    }

    return response.text;
};

const postAudioPrompt = async (audioBlob, mode, requestNarratedResponse) => {
    // Create an obj of type FormData() to send both the audio and the generateAudioResponses flag
    const requestBody = new FormData();
    requestBody.append("narrateResponse", requestNarratedResponse);
    requestBody.append("mode", mode);
    requestBody.append("audio", audioBlob, "audio.wav");

    const response = await HTTPService.post({
        endpoint: "api/v1/asr",
        body: requestBody,
        headers: { "Accept": "application/json" }
    });

    if (response.audio) {
        await IOService.handleAudioPlayback(response.audio);
    }
};

const startRecordingAudio = (mediaRecorderRef, audioChunksRef) => {
    audioChunksRef.current = [];

    return navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
        mediaRecorderRef.current = new MediaRecorder(stream);
        if (!mediaRecorderRef.current) {
            throw new Error("MediaRecorder is not supported in this browser.");
        }

        mediaRecorderRef.current.ondataavailable = (event) => {
            audioChunksRef.current.push(event.data);
        }

        mediaRecorderRef.current.start();
    }).catch(error => {
        console.error("Error accessing media devices:", error);
        throw error;
    });
};

const stopRecordingAudio = async (mediaRecorderRef, audioChunksRef) => {
    return new Promise((resolve) => {
        mediaRecorderRef.current.onstop = () => {
            const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
            resolve(blob);

            // Stop all tracks in the stream
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorderRef.current.stop();
    });
};

export const IOService = {
    handleAudioPlayback,
    postTextPrompt,
    postAudioPrompt,
    startRecordingAudio,
    stopRecordingAudio
};