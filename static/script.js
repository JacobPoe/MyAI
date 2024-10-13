let lightMode = true;
let recorder = null;
let recording = false;
let voiceOption = "default";
const responses = [];
const botRepeatButtonIDToIndexMap = {};
const userRepeatButtonIDToRecordingMap = {};
const baseUrl = window.location.origin;

async function showBotLoadingAnimation() {
  await sleep(500);
  $(".loading-animation")[1].style.display = "inline-block";
}

function hideBotLoadingAnimation() {
  $(".loading-animation")[1].style.display = "none";
}

async function showUserLoadingAnimation() {
  await sleep(100);
  $(".loading-animation")[0].style.display = "flex";
}

function hideUserLoadingAnimation() {
  $(".loading-animation")[0].style.display = "none";
}

const getSpeechToText = async (userRecording) => {
  let response = await fetch(baseUrl + "/speech-to-text", {
    method: "POST",
    body: userRecording.audioBlob,
    headers: {
      "Content-Type": "audio/mpeg"
    }
  });
  response = await response.json();
  return response.text;
};


const cleanTextInput = (value) => {
  return value
    .trim() // remove starting and ending spaces
    .replace(/[\n\t]/g, "") // remove newlines and tabs
    .replace(/<[^>]*>/g, "") // remove HTML tags
    .replace(/[<>&;]/g, ""); // sanitize inputs
};

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
            const audio = new Audio(audioUrl);
            const play = () => audio.play();
            resolve({ audioBlob, audioUrl, play });
          });

          mediaRecorder.stop();
        });

      resolve({ start, stop });
    } catch (error) {
      console.error("Error accessing microphone:", error);
      reject(error);  // Reject promise if there's an error
    }
  });
};

const sleep = (time) => new Promise((resolve) => setTimeout(resolve, time));

const toggleRecording = async () => {
  if (!recording) {
    recorder = await recordAudio();
    recording = true;
    recorder.start();
  } else {
    const audio = await recorder.stop();
    return audio;
  }
};

const getRandomID = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};
const scrollToBottom = () => {
  // Scroll the chat window to the bottom
  $("#chat-window").animate({
    scrollTop: $("#chat-window")[0].scrollHeight,
  });
};
const populateUserMessage = (userMessage, userRecording) => {
  // Clear the input field
  $("#message-input").val("");

  // Append the user's message to the message list

  if (userRecording) {
    const userRepeatButtonID = getRandomID();
    userRepeatButtonIDToRecordingMap[userRepeatButtonID] = userRecording;
    hideUserLoadingAnimation();
    $("#message-list").append(
      `<div class='message-line my-text'><div class='message-box my-text${
        !lightMode ? " dark" : ""
      }'><div class='me'>${userMessage}</div></div>
            <button id='${userRepeatButtonID}' class='btn volume repeat-button' onclick='userRepeatButtonIDToRecordingMap[this.id].play()'><i class='fa fa-volume-up'></i></button>
            </div>`
    );
  } else {
    $("#message-list").append(
      `<div class='message-line my-text'><div class='message-box my-text${
        !lightMode ? " dark" : ""
      }'><div class='me'>${userMessage}</div></div></div>`
    );
  }

  scrollToBottom();
};

const processUserMessage = async (userMessage, endpoint, isAudio = false) => {
  console.log("Processing user message:", userMessage);
  const payload = isAudio ? userMessage : JSON.stringify({ userMessage: userMessage, voice: voiceOption });
  const headers = isAudio ? {} : { "Content-Type": "application/json" };

  await fetch(baseUrl + endpoint, {
    method: "POST",
    body: payload,
    headers: headers,
  });
};

const populateBotResponse = async (userMessage, inputType) => {
  await showBotLoadingAnimation();

  let response = {};
  switch (inputType) {
    case 'TTS':
      response = await processUserMessage(userMessage, "/text-to-speech");
      break;
    case 'STT':
      response = await processUserMessage(userMessage, "/speech-to-text", true);
      break;
  }

  if (response.headers?.get("Content-Type") === "application/json") {
    const text = await response.json();

    $("#message-list").append(
      `<div class='message-line'><div class='message-box${
        !lightMode ? " dark" : ""
      }'>${text}</div></div>`
    );
  } else {
    await playResponseAudio(response);
  }

  responses.push(response);
  hideBotLoadingAnimation();
  scrollToBottom();
};

const playResponseAudio = async (data) => {
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

$(document).ready(function () {
  // Listen for the "Enter" key being pressed in the input field
  $("#message-input").keyup(function (event) {
    let inputVal = cleanTextInput($("#message-input").val());

    if (event.keyCode === 13 && inputVal != "") {
      const message = inputVal;

      populateUserMessage(message, null);
      populateBotResponse(message, 'TTS');
    }

    inputVal = $("#message-input").val();

    if (inputVal == "" || inputVal == null) {
      $("#send-button")
        .removeClass("send")
        .addClass("microphone")
        .html("<i class='fa fa-microphone'></i>");
    } else {
      $("#send-button")
        .removeClass("microphone")
        .addClass("send")
        .html("<i class='fa fa-paper-plane'></i>");
    }
  });

  // When the user clicks the "Send" button
  $("#send-button").click(async function () {
    if ($("#send-button").hasClass("microphone") && !recording) {
      toggleRecording();
      $(".fa-microphone").css("color", "#f44336");
      recording = true;
    } else if (recording) {
      toggleRecording().then(async (userRecording) => {
        await showUserLoadingAnimation();
        const userMessage = await getSpeechToText(userRecording);

        populateUserMessage(userMessage, userRecording);
        populateBotResponse(userRecording, 'STT');
      });
      $(".fa-microphone").css("color", "#125ee5");
      recording = false;
    } else {
      // Get the message the user typed in
      const message = cleanTextInput($("#message-input").val());

      populateUserMessage(message, null);
      populateBotResponse(message, 'TTS');

      $("#send-button")
        .removeClass("send")
        .addClass("microphone")
        .html("<i class='fa fa-microphone'></i>");
    }
  });

  // handle the event of switching light-dark mode
  $("#light-dark-mode-switch").change(function () {
    $("body").toggleClass("dark-mode");
    $(".message-box").toggleClass("dark");
    $(".loading-dots").toggleClass("dark");
    $(".dot").toggleClass("dark-dot");
    lightMode = !lightMode;
  });

  $("#voice-options").change(function () {
    voiceOption = $(this).val();
    console.log(voiceOption);
  });
});
