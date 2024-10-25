import tkinter as tk
import pyaudio
import wave
import speech_recognition as sr
import threading

# Parameters for audio recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "recorded.wav"

# Initialize recognizer
recognizer = sr.Recognizer()
is_recording = False
audio = None
stream = None
frames = []

# Supported languages dictionary
LANGUAGES = {
    "English": "en-US",
    "Chinese": "zh-CN",
    "Malay": "ms-MY",
    "Hindi": "hi-IN",
    "Tamil": "ta-IN"
}

# Starts the audio recording process
def start_recording():
    global is_recording, audio, stream, frames
    is_recording = True
    frames = []

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    def record():
        while is_recording:
            data = stream.read(CHUNK)
            frames.append(data)

    threading.Thread(target=record).start()
    record_button.config(text="Stop", command=stop_recording)

#Stops the audio recording process
def stop_recording():
    global is_recording, audio, stream
    is_recording = False

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    convert_speech_to_text(WAVE_OUTPUT_FILENAME)
    record_button.config(text="Start", command=start_recording)

# Converts speech to text
def convert_speech_to_text(audio_file):
    """Function to convert speech in an audio file to text."""
    selected_language = language_var.get()
    language_code = LANGUAGES.get(selected_language, "en-US")

    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language=language_code)
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

record_button = tk.Button(root, text="Start", command=start_recording)
record_button.pack(pady=20)

language_var = tk.StringVar(root)
language_var.set("English")  # default value

language_menu = tk.OptionMenu(root, language_var, *LANGUAGES.keys())
language_menu.pack(pady=20)

result_label = tk.Label(root, text="")
result_label.pack(pady=20)

root.mainloop()

