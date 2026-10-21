import json
import re

from openai import OpenAI

from brain.memory import load_memory, save_memory
from config import (EXAMPLES_FILE, MAX_TURNS, OLLAMA_BASE_URL, OLLAMA_MODEL,
                    SYSTEM_PROMPT_FILE, TEMPERATURE)

# Point the client at Ollama on your computer instead of OpenAI's servers
client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")  # required by the library, ignored by Ollama


def _read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


SYSTEM_MESSAGE = {"role": "system", "content": _read_text(SYSTEM_PROMPT_FILE)}

with open(EXAMPLES_FILE, "r", encoding="utf-8") as f:
    EXAMPLE_TURNS = json.load(f)  # set the file to [] to turn examples off


def clean_reply(text):
    # Remove whole actions such as *smiles softly* (asterisk spans that contain a space)
    text = re.sub(r"\*[^*\n]*\s[^*\n]*\*", "", text)
    # Keep single-word emphasis such as *fascinating*, without the asterisks
    text = re.sub(r"\*([^*\s]+)\*", r"\1", text)
    text = re.sub(r"\([^)]*\)", "", text)  # remove action-style parentheses like (giggles)
    text = text.replace("*", "")           # remove any leftover asterisks
    return re.sub(r"\s+", " ", text).strip()


class Companion:
    def __init__(self):
        self.history = load_memory()  # saved exchanges, without the system prompt
        self._trim()

    def reply(self, user_text):
        self.history.append({"role": "user", "content": user_text})
        self._trim()
        try:
            response = self._request(self._build_messages())
        except Exception:
            self.history.pop()  # drop the unanswered message so memory stays consistent
            raise
        self.history.append({"role": "assistant", "content": response})
        return response

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
            text = self._request(self._build_messages([prompt]))
        except Exception:
            text = "Take care, trainer! I'll be right here when you come back."

        self.history.append({"role": "user", "content": user_text})
        self.history.append({"role": "assistant", "content": text})
        self._trim()
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
        return clean_reply(str(completion.choices[0].message.content))

    def _trim(self):
        # Keep only the most recent exchanges (2 messages each)
        self.history = self.history[-MAX_TURNS * 2:]