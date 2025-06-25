# code_generator/code_generator.py
import numpy as np
import soundfile as sf
from audio_recorder.audio_recorder import AudioRecorder
from openai import OpenAI

MORSE_CODE = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    ",": "--..--",
    ".": ".-.-.-",
    " ": "/",
}

class CodeGenerator:
    def __init__(self, wpm, freq, sample_rate, filename):
        self.wpm = wpm
        self.freq = freq
        self.sample_rate = sample_rate
        self.filename = filename

    def generate_morse_code(self, text):
        # Calculate the timing of Morse code dits and dahs based on WPM.
        dit_duration = 1.2 / self.wpm
        dah_duration = 3 * dit_duration

        # Calculate the timing of Morse code gaps.
        gap = dit_duration
        char_gap = 3 * dit_duration
        word_gap = 7 * dit_duration

        def tone(duration):
            t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
            return 0.5 * np.sin(2 * np.pi * self.freq * t)

        def silence(duration):
            return np.zeros(int(self.sample_rate * duration))

        audio = []
        for symbol in text:
            if symbol == ".":
                audio.extend(tone(dit_duration))
                audio.extend(silence(gap))
            elif symbol == "-":
                audio.extend(tone(dah_duration))
                audio.extend(silence(gap))
            elif symbol == " ":
                audio.extend(silence(char_gap - gap))
            elif symbol == "/":
                audio.extend(silence(word_gap - gap))
        sf.write(self.filename, np.array(audio, dtype=np.float32), self.sample_rate)
