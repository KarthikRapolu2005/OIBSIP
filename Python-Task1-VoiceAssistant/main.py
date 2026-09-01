"""
main.py -- Nova Voice Assistant
================================
Entry point that ties together speech I/O, NLU intent parsing, and all
skills. Supports two input modes:

  1. Voice mode  -- uses the microphone via speech_recognition
  2. Text mode   -- keyboard fallback, always available, used automatically
                     if the microphone isn't available, and selectable
                     manually at startup.

Run with:  python main.py

See README.md for full setup, feature list, and demo checklist.
"""

import sys

from config import ASSISTANT_NAME
from speech.tts import TextToSpeech
from speech.stt import SpeechToText, text_input
from nlu.intent_parser import parse_intent
from utils.logger import log

from skills.greeting import handle_greeting
from skills.datetime_skill import get_time, get_date
from skills.web_search import web_search
from skills.weather import get_weather
from skills.email_skill import send_email
from skills.reminder import ReminderManager
from skills.knowledge import answer_question
from skills.custom_commands import CustomCommandManager


HELP_TEXT = (
    "Here is what I can do:\n"
    "  - Say 'hello' for a greeting\n"
    "  - Ask 'what time is it' or 'what's the date'\n"
    "  - Say 'search for <topic>' to search the web\n"
    "  - Ask 'what's the weather in <city>'\n"
    "  - Say 'send an email' to compose and send/simulate an email\n"
    "  - Say 'remind me to <task> in <N> minutes' to set a reminder\n"
    "  - Ask general knowledge questions like 'who is Alan Turing'\n"
    "  - Say 'add a custom command' to teach me a new phrase\n"
    "  - Say 'exit' or 'quit' to stop\n"
)


class NovaAssistant:
    def __init__(self, voice_mode: bool):
        self.tts = TextToSpeech()
        self.stt = SpeechToText() if voice_mode else None
        self.voice_mode = voice_mode and self.stt is not None and self.stt.microphone_available
        self.reminder_manager = ReminderManager(self.tts)
        self.custom_commands = CustomCommandManager()
        self.running = True

    # ---------- Input helpers ----------

    def listen(self) -> str:
        """Get one utterance from the user, via mic or keyboard."""
        if self.voice_mode:
            result = self.stt.listen()
            if result is None:
                return None  # mic/timeout error -- handled by caller
            if result == "":
                self.tts.say("Sorry, I didn't catch that. Could you please repeat?")
                return ""
            return result
        else:
            return text_input()

    def ask(self, prompt: str) -> str:
        """Speak/print a follow-up question and get a single-value reply."""
        self.tts.say(prompt)
        if self.voice_mode:
            answer = self.stt.listen()
            return answer or ""
        return text_input()

    # ---------- Main loop ----------

    def run(self):
        mode_label = "VOICE" if self.voice_mode else "TEXT"
        log("Mode", mode_label)
        self.tts.say(
            f"{ASSISTANT_NAME} is online in {mode_label.lower()} mode. "
            "Say 'help' to see what I can do, or 'exit' to quit."
        )

        while self.running:
            utterance = self.listen()

            if utterance is None:
                # Mic became unavailable mid-session -- switch to text mode
                self.tts.say("I lost access to the microphone. Switching to text mode.")
                self.voice_mode = False
                continue

            if utterance == "":
                continue  # already handled: asked user to repeat

            self.dispatch(utterance)

    def dispatch(self, utterance: str):
        # 1. Custom commands take priority (user-taught phrases)
        custom_response = self.custom_commands.match(utterance)
        if custom_response:
            self.tts.say(custom_response)
            return

        # 2. NLU intent parsing
        intent = parse_intent(utterance)
        log("Intent", f"{intent.name} | entities={intent.entities}")

        handler = getattr(self, f"_intent_{intent.name}", None)
        if handler:
            try:
                handler(intent)
            except Exception as exc:
                # Catch-all so one skill failure never crashes the app
                self.tts.say(f"Something went wrong while handling that request: {exc}")
        else:
            self._intent_unknown(intent)

    # ---------- Intent handlers ----------

    def _intent_exit(self, intent):
        self.tts.say("Goodbye! Shutting down Nova now.")
        self.reminder_manager.cancel_all()
        self.running = False

    def _intent_greeting(self, intent):
        self.tts.say(handle_greeting())

    def _intent_time(self, intent):
        self.tts.say(get_time())

    def _intent_date(self, intent):
        self.tts.say(get_date())

    def _intent_help(self, intent):
        self.tts.say(HELP_TEXT)

    def _intent_web_search(self, intent):
        query = intent.entities.get("query")
        if not query:
            query = self.ask("What would you like me to search for?")
        self.tts.say(web_search(query))

    def _intent_weather(self, intent):
        city = intent.entities.get("city")
        if not city:
            city = self.ask("Which city's weather would you like?")
        self.tts.say(get_weather(city))

    def _intent_send_email(self, intent):
        self.tts.say("Sure, let's compose that email.")
        to_address = self.ask("What is the recipient's email address?")
        subject = self.ask("What should the subject line be?")
        body = self.ask("What should the email say?")
        self.tts.say(send_email(to_address, subject, body))

    def _intent_set_reminder(self, intent):
        task = intent.entities.get("task")
        minutes = intent.entities.get("minutes")
        if not task:
            task = self.ask("What should I remind you to do?")
        if not minutes:
            minutes = self.ask("In how many minutes should I remind you?")
        self.tts.say(self.reminder_manager.set_reminder(task, minutes))

    def _intent_knowledge_query(self, intent):
        topic = intent.entities.get("topic")
        if not topic:
            topic = self.ask("What would you like to know about?")
        self.tts.say(answer_question(topic))

    def _intent_add_custom_command(self, intent):
        self.tts.say("Let's create a new custom command.")
        trigger = self.ask("What phrase should trigger this command?")
        response = self.ask("What should I say when I hear that phrase?")
        self.tts.say(self.custom_commands.add_command(trigger, response))

    def _intent_unknown(self, intent):
        self.tts.say(
            "I'm not sure how to help with that yet. Say 'help' to see what I can do."
        )


def choose_mode() -> bool:
    """Ask the user at startup whether to use voice or text mode."""
    print(f"\n=== {ASSISTANT_NAME} Voice Assistant ===")
    print("1. Voice mode (microphone)")
    print("2. Text mode (keyboard fallback)")
    choice = input("Choose mode [1/2] (default 2): ").strip()
    return choice == "1"


def main():
    try:
        voice_mode = choose_mode()
    except (EOFError, KeyboardInterrupt):
        voice_mode = False

    assistant = NovaAssistant(voice_mode=voice_mode)

    if voice_mode and not assistant.voice_mode:
        print("[Nova] No working microphone detected. Falling back to text mode.")

    try:
        assistant.run()
    except KeyboardInterrupt:
        print("\n[Nova] Interrupted by user. Shutting down.")
        assistant.reminder_manager.cancel_all()
        sys.exit(0)


if __name__ == "__main__":
    main()
