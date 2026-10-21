
import threading
import pyaudio
import speech_recognition as sr

from config import CHUNK, RECOGNITION_LANGUAGE, SAMPLE_RATE


def record_until_enter():
    # Records from the microphone until the user presses Enter again
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE,
                    input=True, frames_per_buffer=CHUNK)
    frames = []
    stop_event = threading.Event()

    def capture():
        while not stop_event.is_set():
            frames.append(stream.read(CHUNK, exception_on_overflow=False))

    recorder = threading.Thread(target=capture, daemon=True)
    recorder.start()
    try:
        input()  # waits here while the recorder thread collects audio
    finally:
        stop_event.set()
        recorder.join()
        stream.stop_stream()
        stream.close()
        p.terminate()
    return b"".join(frames)


def speech_to_text():
    input("\nPress Enter to start talking (Ctrl+C to quit)... ")
    print("Recording... press Enter when you're done.")
    audio_bytes = record_until_enter()
    print("Done recording")

    if not audio_bytes:
        print("Nothing was recorded.")
        return None

    print("Recognizing the text")
    recognizer = sr.Recognizer()
    audio = sr.AudioData(audio_bytes, SAMPLE_RATE, 2)  # 2 bytes per sample (16-bit)
    try:
        return recognizer.recognize_google(audio, language=RECOGNITION_LANGUAGE)
    except sr.UnknownValueError:
        print("Couldn't understand that.")
    except sr.RequestError as e:
        print(f"Google service error: {e}")
    return None