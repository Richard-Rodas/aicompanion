# 🤖 Project Kira

A voice-based AI companion that listens through your microphone, replies in character, and speaks the reply aloud.

This is a personal, non-commercial fan project. The character KIRA is an acronym that stands for
Kawaii Intelligent Responsive Assistant.

## ✨ Features 

- Press-to-talk speech input with Google's free speech recognition
- Replies from a local language model through Ollama
- Speech output with Chatterbox, running locally on a GPU when available
- Saved conversation memory between sessions

## 🛠️ Requirements 

- Windows (the audio playback uses `winsound`)
- Python 3.12
- A microphone
- [Ollama](https://ollama.com), with the `gemma3:12b` model downloaded
- An NVIDIA GPU is recommended for Chatterbox

## ⚙️ Setup 

1. Create and activate a virtual environment:
```
   py -3.12 -m venv .venv
   .venv\Scripts\activate
```
2. Install the requirements:
```
   python -m pip install -r requirements.txt
```
3. Install the CUDA build of PyTorch, if you have an NVIDIA GPU:
```
   python -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128
```
4. Download the language model:
```
   ollama pull gemma3:12b
```
5. Optional: add a voice reference clip. Save a 10 to 20 second recording of a voice you have permission to use as `assets/voice_reference.wav`. Without it, Chatterbox uses its default voice.

## ▶️ Usage 

Start Ollama, then run:

```
python main.py
```

Press Enter to start talking, and press Enter again when you finish. Say "goodbye" to end the session.

## 📁 Project structure 

- `main.py`: the main loop
- `config.py`: settings
- `audio/`: microphone input and speech output
- `brain/`: conversation logic and memory
- `personality/`: the character prompt and example exchanges
- `data/`: saved conversation and generated audio (not included in the repository)
- `assets/`: optional voice reference clip (not included in the repository)

## 🎤 Notes on voice and content 

Only use a voice reference from someone who has agreed to its use. Do not commit recordings of other people's voices to the repository.

## 🔗 Third-party components and content

- **Gemma 3** (downloaded through Ollama) is subject to Google's Gemma Terms of Use, not an open-source license. Check the terms before using or redistributing the model.
- **Chatterbox** (`chatterbox-tts`) is a separate project with its own license. Its model weights are downloaded separately and may have their own terms, so check its GitHub repository and Hugging Face model page.
- **Ollama** is a separate project with its own license.
- **Python packages** listed in `requirements.txt`, such as SpeechRecognition, PyAudio, openai, numpy, soundfile, and python-dotenv, are separate projects with their own licenses. Installing them doesn't change this project's MIT license.
- **Speech recognition** uses Google's web speech service through the SpeechRecognition library. Its terms are set by Google, and the service may change or stop working.
- **Voice reference clips:** This project doesn't include any voice recordings. A reference clip you add must come from someone who has agreed to its use, and the MIT license doesn't cover it.