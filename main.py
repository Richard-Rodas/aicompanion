import config  # must be first: sets up warning filters and loads .env

from audio.listener import speech_to_text
from audio.speaker import Speaker
from brain.chat import Companion
from config import GOODBYE_WORDS


def main():
    companion = Companion()
    speaker = Speaker()
    print("AI Companion is listening. Say 'goodbye' to end, or press Ctrl+C.")

    try:
        while True:
            user_text = speech_to_text()
            if user_text is None:
                print("---")
                continue

            print("What I said:", user_text)
            if user_text.lower().strip(" .!?") in GOODBYE_WORDS:
                farewell = companion.farewell(user_text)
                print("Emotion:", companion.last_emotion)
                print("AI Companion:", farewell)
                speaker.speak(farewell)
                break

            reply = companion.reply(user_text)
            print("Ganyu response:", reply)
            print("Emotion:", companion.last_emotion)
            speaker.speak(reply)
    except KeyboardInterrupt:
        print("\nSee you later!")
    finally:
        companion.save()  # runs on goodbye, Ctrl+C, or an error


if __name__ == "__main__":
    main()