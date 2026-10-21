import os
import warnings

#from dotenv import load_dotenv

# Silence noisy library messages. This file is imported first, so these run before Kokoro loads.
os.environ["HF_HUB_VERBOSITY"] = "error"
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*dropout option adds dropout.*")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
PERSONALITY_DIR = os.path.join(BASE_DIR, "personality")

os.makedirs(DATA_DIR, exist_ok=True)
#load_dotenv(os.path.join(BASE_DIR, ".env"))

# Files
MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")
REPLY_AUDIO_FILE = os.path.join(DATA_DIR, "ai-reply.wav")
SYSTEM_PROMPT_FILE = os.path.join(PERSONALITY_DIR, "companion.txt")
EXAMPLES_FILE = os.path.join(PERSONALITY_DIR, "examples.json")
# VOICE_REFERENCE = os.path.join(ASSETS_DIR, "voice_reference.wav")  # used when Chatterbox is added

# Speech recognition
SAMPLE_RATE = 16000
CHUNK = 1024
RECOGNITION_LANGUAGE = "en-US"

# Chat model (Ollama)
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_MODEL = "gemma3:12b" # Ollama model currently used for chat.
TEMPERATURE = 0.9 
MAX_TURNS = 10  # exchanges kept in memory

# Text to speech (Chatterbox, runs locally)
CHATTERBOX_DEVICE = "auto"      # uses the GPU when PyTorch can see it
CHATTERBOX_EXAGGERATION = 0.6   # expressiveness: higher = more emotion
CHATTERBOX_CFG_WEIGHT = 0.5     # pacing: lower = slower, more deliberate
VOICE_REFERENCE = os.path.join(ASSETS_DIR, "voice_reference.wav")  # the cloned voice

# Words that end the conversation
GOODBYE_WORDS = ("goodbye", "bye", "exit", "quit", "stop", "end", "see you", "later", "farewell")