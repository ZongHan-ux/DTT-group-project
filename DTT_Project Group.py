import tkinter as tk
import pyaudio
import wave
import speech_recognition as sr

# Parameters for audio recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "recorded.wav"

# Initialize recognizer
recognizer = sr.Recognizer()

def record_audio():
    """Function to record audio and save it as a WAV file."""
    audio = pyaudio.PyAudio()

    # Open stream
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    frames = []

    print("Recording...")
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Recording complete")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded data as a WAV file
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    # Convert speech to text
    convert_speech_to_text(WAVE_OUTPUT_FILENAME)

def convert_speech_to_text(audio_file):
    """Function to convert speech in an audio file to text."""
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            print("Text: " + text)
            result_label.config(text="Text: " + text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            result_label.config(text="Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            result_label.config(text="Error with the speech recognition service")

# Set up the GUI
root = tk.Tk()
root.title("Voice Recorder")

record_button = tk.Button(root, text="Record", command=record_audio)
record_button.pack(pady=20)

result_label = tk.Label(root, text="")
result_label.pack(pady=20)

root.mainloop()

