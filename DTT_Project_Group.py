import streamlit as st
import pyaudio
import wave
import speech_recognition as sr
import threading
import os
from googletrans import Translator
from pydub import AudioSegment  # Import pydub for audio conversion if needed

# Parameters for audio recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "recorded.wav"

# Initialize recognizer and translator
recognizer = sr.Recognizer()
translator = Translator()
is_recording = False
audio = None
stream = None
frames = []

# Supported languages dictionary for speech recognition
SPEECH_LANGUAGES = {
    "English": "en-US",
    "Chinese": "zh-CN",
    "Malay": "ms-MY",
    "Hindi": "hi-IN",
    "Tamil": "ta-IN"
}

# Supported languages for translation
TRANSLATION_LANGUAGES = {
    "English": "en",
    "Chinese": "zh-cn",
    "Malay": "ms",
    "Hindi": "hi",
    "Tamil": "ta"
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
    st.button("Stop", on_click=stop_recording)

# Stops the audio recording process
def stop_recording():
    global is_recording, audio, stream
    is_recording = False

    if stream is not None:
        stream.stop_stream()
        stream.close()
    if audio is not None:
        audio.terminate()

    if frames:
        try:
            # Write the audio frames to a WAV file
            with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                if audio is not None:
                    wf.setsampwidth(audio.get_sample_size(FORMAT))  # Ensure sample width is set
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

            # Optionally, convert to a valid PCM WAV format using pydub (if necessary)
            convert_wav_format(WAVE_OUTPUT_FILENAME)

            # Check if the file exists and has content
            if os.path.exists(WAVE_OUTPUT_FILENAME) and os.path.getsize(WAVE_OUTPUT_FILENAME) > 0:
                st.write("Recording saved successfully.")
                convert_speech_to_text(WAVE_OUTPUT_FILENAME)
            else:
                st.write("Error: No audio data recorded.")
        except Exception as e:
            st.write(f"Error saving the file: {e}")
    else:
        st.write("No frames recorded.")

# Function to ensure WAV file is valid PCM format (optional)
def convert_wav_format(file_path):
    try:
        # Using pydub to convert the file to a proper format
        audio = AudioSegment.from_wav(file_path)
        audio = audio.set_frame_rate(RATE)  # Ensure correct sample rate
        audio = audio.set_channels(CHANNELS)  # Ensure correct channels
        audio = audio.set_sample_width(2)  # 2 bytes per sample for 16-bit depth (required)
        audio.export(file_path, format="wav")  # Export the file back in proper format
        st.write("WAV format conversion complete.")
    except Exception as e:
        st.write(f"Error converting WAV file: {e}")

# Converts speech to text and then translates to English
def convert_speech_to_text(audio_file):
    selected_language = st.session_state.language
    speech_language_code = SPEECH_LANGUAGES.get(selected_language, "en-US")
    translation_language_code = TRANSLATION_LANGUAGES.get(selected_language, "en")

    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language=speech_language_code)
            st.write(f"Recognized Text: {text}")

            # Translate text to English
            translation = translator.translate(text, src=translation_language_code, dest='en')
            translated_text = translation.text
            st.write(f"Translated Text: {translated_text}")
    except ValueError as e:
        st.write(f"Error with the audio file: {e}")
    except sr.UnknownValueError:
        st.write("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        st.write(f"Could not request results from Google Speech Recognition service; {e}")
    except Exception as e:
        st.write(f"Translation error: {e}")

# Set up the Streamlit app
st.title("Voice Recorder")

# Language selection
st.write("Select Language:")
language = st.selectbox("Choose language", options=list(SPEECH_LANGUAGES.keys()))
st.session_state.language = language  # store the selected language

# Start and stop recording
if st.button("Start Recording"):
    start_recording()

# Display result
st.write("Recording will appear here")
