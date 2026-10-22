import json
import re

from openai import OpenAI

from brain.memory import load_memory, save_memory
from config import (EMOTIONS, EXAMPLES_FILE, MAX_TURNS, OLLAMA_BASE_URL,
                    OLLAMA_MODEL, SYSTEM_PROMPT_FILE, TEMPERATURE)

# Point the client at Ollama on your computer instead of OpenAI's servers
client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")  # required by the library, ignored by Ollama

# Matches an emotion tag at the very end of a reply, such as "[shy]" or "[happy]."
EMOTION_TAG = re.compile(r"\[(\w+)\][.!?\s]*$")


def _read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


SYSTEM_MESSAGE = {"role": "system", "content": _read_text(SYSTEM_PROMPT_FILE)}

with open(EXAMPLES_FILE, "r", encoding="utf-8") as f:
    EXAMPLE_TURNS = json.load(f)  # set the file to [] to turn examples off


def split_emotion(text):
    # Removes the trailing emotion tag and returns (clean_text, emotion)
    match = EMOTION_TAG.search(text)
    if not match:
        return text.strip(), "neutral"
    emotion = match.group(1).lower()
    if emotion not in EMOTIONS:
        emotion = "neutral"
    return text[:match.start()].strip(), emotion


def clean_reply(text):
    text = re.sub(r"\*[^*\n]*\s[^*\n]*\*", "", text)  # remove whole actions like *smiles softly*
    text = re.sub(r"\*([^*\s]+)\*", r"\1", text)      # keep single-word emphasis, without asterisks
    text = re.sub(r"\([^)]*\)", "", text)             # remove action-style parentheses like (giggles)
    text = re.sub(r"\[[^\]]*\]", "", text)            # remove any leftover square-bracket tags
    text = text.replace("*", "")                      # remove any remaining asterisks
    return re.sub(r"\s+", " ", text).strip()


class Companion:
    def __init__(self):
        self.history = load_memory()  # saved exchanges, without the system prompt
        self.last_emotion = "neutral"  # emotion from the most recent reply
        self._trim()

    def reply(self, user_text):
        self.history.append({"role": "user", "content": user_text})
        self._trim()
        try:
            text, emotion = self._request(self._build_messages())
        except Exception:
            self.history.pop()  # drop the unanswered message so memory stays consistent
            raise
        self.history.append({"role": "assistant", "content": text})
        self.last_emotion = emotion
        return text

    def farewell(self, user_text):
        prompt = {
            "role": "user",
            "content": (
                f"The trainer just said '{user_text}' and is leaving now. "
                "Write one short, warm goodbye in character, mentioning something from "
                "our conversation if you can. Keep it to two sentences."
            ),
        }
        try:
            # The farewell instruction is sent once and never saved to history
            text, emotion = self._request(self._build_messages([prompt]))
        except Exception:
            text, emotion = "Take care, trainer! I'll be right here when you come back.", "neutral"

        self.history.append({"role": "user", "content": user_text})
        self.history.append({"role": "assistant", "content": text})
        self._trim()
        self.last_emotion = emotion
        return text

    def save(self):
        save_memory(self.history)

    def _build_messages(self, extra=None):
        return [SYSTEM_MESSAGE] + EXAMPLE_TURNS + self.history + (extra or [])

    def _request(self, messages):
        completion = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=messages,
            temperature=TEMPERATURE,
        )
        raw = str(completion.choices[0].message.content)
        text, emotion = split_emotion(raw)  # take the tag off before cleaning
        return clean_reply(text), emotion

    def _trim(self):
        # Keep only the most recent exchanges (2 messages each)
        self.history = self.history[-MAX_TURNS * 2:]