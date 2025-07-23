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
}

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

export const IOService = {
    handleAudioPlayback,
    postTextPrompt,
    postAudioPrompt
};