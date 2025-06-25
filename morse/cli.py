# cli.py
import json
import sys
import pyaudio
import subprocess
from audio_recorder import AudioRecorder
from code_generator import CodeGenerator
from openai import OpenAI

# Constant.
AUDIO_FILE_PATH = "/Users/brian/Code/Morse/audio.wav"
MORSE_FILE_PATH = "/Users/brian/Code/Morse/morse.wav"
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "generate_morse_audio",
            "description": "Generate a .wav file of Morse code from a given Morse code (dot-dash) string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "morse_code": {
                        "type": "string",
                        "description": "The Morse code text.",
                    },
                },
                "required": ["morse_code"],
            },
        },
    }
]

def transcribe_audio(client, audio_path):
    with open(audio_path, "rb") as file:
        return client.audio.transcriptions.create(model="whisper-1", file=file)


def convert_text_to_morse_code(client, transcript_text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a tool that converts text into international Morse code.",
            },
            {
                "role": "system",
                "content": "Return Morse code only. Always end with .-.-.-",
            },
            {
                "role": "user",
                "content": f"Convert this text into Morse code:\n{transcript_text}",
            },
        ],
    )
    return response.choices[0].message.content.strip()


def convert_to_morse_code_audio_file(client, code_generator, messages):
    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        message = response.choices[0].message
        messages.append(message.model_dump())

        if not message.tool_calls:
            return message.content

        for tool_call in message.tool_calls:
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                print(
                    f"Invalid JSON arguments: {tool_call.function.arguments}",
                    file=sys.stderr,
                )
                continue

            if tool_call.function.name == "generate_morse_audio":
                morse_code = args["morse_code"]
                code_generator.generate_morse_code(morse_code)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "generate_morse_audio",
                        "content": f"Morse code audio saved.",
                    }
                )
            else:
                print(f"Unknown function: {tool_call.function.name}", file=sys.stderr)


# Main
def main():
    while True:
        # Create the OpenAI client and initialize the audio recorder and code generator.
        client = OpenAI()
        audio_recorder = AudioRecorder(
            samplerate=44100,
            channels=1,
            frames_per_buffer=1024,
            format=pyaudio.paInt16,
            filename=AUDIO_FILE_PATH,
        )
        code_generator = CodeGenerator(
            wpm=20, freq=600, sample_rate=44100, filename=MORSE_FILE_PATH
        )

        # Record and play the audio.
        input("Press ENTER to start recording: ")
        audio_recorder.start()
        input("   Recording... Press ENTER to stop")
        audio_recorder.stop()

        print("\nPlaying recorded audio...")
        subprocess.call(["afplay", AUDIO_FILE_PATH])
        print(f"   Playback complete")


        # Transcribe the audio and convert it to Morse code.
        print("\nTranscribing audio:")
        transcript = transcribe_audio(client, AUDIO_FILE_PATH)
        print(f"   Transcript is: '{transcript.text}'")

        # Convert the transcript to Morse code text.
        print(f"\nConverting '{transcript.text}' to Morse code text:")
        morse_code = convert_text_to_morse_code(client, transcript.text)
        print(f"   Morse code text is: '{morse_code}'")

        # Convert the Morse code text to the Morse code audio file.
        print(f"\nConverting '{morse_code}' to Morse code audio:")
        convert_to_morse_code_audio_file(
            client,
            code_generator,
            [
                {"role": "system", "content": "You are a Morse code assistant."},
                {
                    "role": "user",
                    "content": f"Please generate the Morse Code audio from this Morse code:\n{morse_code}",
                },
            ],
        )
        print(f"   Conversion complete")

        print("\nPlaying Morse code audio...")
        subprocess.call(["afplay", MORSE_FILE_PATH])
        print(f"   Playback complete")
        print()

if __name__ == "__main__":
    main()
