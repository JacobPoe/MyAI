import librosa
import os
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
from transformers.pipelines.automatic_speech_recognition import AutomaticSpeechRecognitionPipeline

from enums import Models, LogLevel, PipelineFrameworks
from logger import Logger

class STT:
    def __init__(self):
        pass

    def callback(self, audio):
        return self.transcribe_audio(audio)

    def transcribe_audio(self, audio_file_path):
        try:
            # Load the audio file to a NumPy array
            audio, sample_rate = librosa.load(audio_file_path, sr=16000)  # Whisper generally expects 16kHz

            model = AutoModelForSpeechSeq2Seq.from_pretrained(Models.WHISPER_TINY_EN.value)
            processor = AutoProcessor.from_pretrained(Models.WHISPER_TINY_EN.value)
            processor.chunk_length = 5
            processor.nb_max_frames = 3000
            processor.sampling_rate = sample_rate
            processor.raw = audio

            pipe = AutomaticSpeechRecognitionPipeline(
              model=model,
              feature_extractor=processor,
              framework=PipelineFrameworks.PYTORCH.value,
              chunk_length_s=5,
            )

            result = pipe(audio)
            Logger.log(LogLevel.STT, result["text"])
            return result["text"]
        except Exception as e:
            Logger.log(LogLevel.ERROR, f"Error processing speech to text, {e}")
            return f"Error processing speech to text, {e}"