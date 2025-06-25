# audio_recorder/audio_recorder.py
import pyaudio
import queue
import threading
import wave

# Recorder class to record audio files using PyAudio.
class AudioRecorder:
    def __init__(self, samplerate, channels, frames_per_buffer, format, filename):
        self.filename = filename
        self.samplerate = samplerate
        self.channels = channels
        self.format = format
        self.frames_per_buffer = frames_per_buffer
        self.q = queue.Queue()
        self.recording = False
        self.p = pyaudio.PyAudio()
        self.stream = None

    def _record(self):
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.samplerate,
            input=True,
            frames_per_buffer=self.frames_per_buffer,
        )

        while self.recording:
            data = self.stream.read(self.frames_per_buffer, exception_on_overflow=False)
            self.q.put(data)

    def start(self):
        self.recording = True
        self.thread = threading.Thread(target=self._record)
        self.thread.start()

    def stop(self):
        self.recording = False
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self._save()
        self.p.terminate()

    def _save(self):
        with wave.open(self.filename, "wb") as wf:
            wf.setcomptype("NONE", "not compressed")
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.samplerate)
            while not self.q.empty():
                wf.writeframes(self.q.get())
