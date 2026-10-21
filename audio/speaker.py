import os
import queue
import re
import threading

import numpy as np
import soundfile as sf
import torch
import winsound  # built-in Windows player; waits until playback finishes
from chatterbox.tts import ChatterboxTTS

from config import (CHATTERBOX_CFG_WEIGHT, CHATTERBOX_DEVICE,
                    CHATTERBOX_EXAGGERATION, REPLY_AUDIO_FILE, VOICE_REFERENCE)

from transformers import logging as hf_logging
hf_logging.set_verbosity_error()  # hides warnings, still shows real errors


def split_sentences(text):
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", text.strip()) if p.strip()]
    merged = []
    pending = ""  # a fragment too short to speak on its own
    for part in parts:
        if pending:
            part = pending + " " + part
            pending = ""
        if len(part.split()) < 4:
            pending = part  # hold it and join it to the next sentence
        else:
            merged.append(part)
    if pending:
        if merged:
            merged[-1] += " " + pending  # a short last fragment joins the previous sentence
        else:
            merged.append(pending)  # the whole reply was short, so speak it as one piece
    return merged


class Speaker:
    def __init__(self):
        device = CHATTERBOX_DEVICE
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading voice model on {device} (first run downloads it)...")
        # Loaded once at startup
        self.model = ChatterboxTTS.from_pretrained(device=device)
        self.sample_rate = self.model.sr

        # Use the reference clip if it exists, otherwise the default voice
        self.voice_prompt = VOICE_REFERENCE if os.path.exists(VOICE_REFERENCE) else None
        if self.voice_prompt is None:
            print("No reference clip found, so using the default voice.")

    def speak(self, text, path=REPLY_AUDIO_FILE):
        sentences = split_sentences(text)
        if not sentences:
            return

        base, ext = os.path.splitext(path)
        pause = np.zeros(int(0.25 * self.sample_rate), dtype=np.float32)
        parts = queue.Queue(maxsize=2)  # the generator stays at most two sentences ahead
        errors = []

        def generate_parts():
            try:
                for i, sentence in enumerate(sentences):
                    wav = self.model.generate(
                        sentence,
                        audio_prompt_path=self.voice_prompt,
                        exaggeration=CHATTERBOX_EXAGGERATION,
                        cfg_weight=CHATTERBOX_CFG_WEIGHT,
                    )
                    audio = np.concatenate([wav.squeeze().cpu().numpy(), pause])
                    part_path = f"{base}-part{i}{ext}"
                    sf.write(part_path, audio, self.sample_rate, subtype="PCM_16")
                    parts.put(part_path)
            except Exception as e:
                errors.append(e)  # keep the error so the main thread can report it
            finally:
                parts.put(None)  # tells the player there are no more parts

        threading.Thread(target=generate_parts, daemon=True).start()

        # Plays each sentence as soon as it's ready, while the next one generates
        while True:
            part_path = parts.get()
            if part_path is None:
                break
            winsound.PlaySound(part_path, winsound.SND_FILENAME)

        if errors:
            raise errors[0]