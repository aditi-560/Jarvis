import os
import webbrowser
import google.generativeai as genai
import sys
import types
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import datetime
import urllib.parse
# Configure environment and Gemini
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not set. LLM features will be disabled.")
genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_OUTPUT_TOKENS = int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "80"))
RESPONSE_STYLE = os.getenv("RESPONSE_STYLE", "concise_voice").strip().lower()

if RESPONSE_STYLE == "concise_voice":
    SYSTEM_INSTRUCTION = (
        "You are a voice assistant. Answer in 1-2 short sentences, direct and "
        "precise, using simple words. If needed, ask at most one brief follow-up "
        "question. Do not use markdown or lists unless explicitly asked."
    )
else:
    SYSTEM_INSTRUCTION = "Be helpful and accurate."

model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_INSTRUCTION)
if GEMINI_API_KEY:
    print(f"Gemini configured with model: {MODEL_NAME}")
REQUIRE_WAKE_WORD = os.getenv("REQUIRE_WAKE_WORD", "false").strip().lower() in ("1", "true", "yes", "on")

def ask_llm(prompt):
    try:
        resp = model.generate_content(
            prompt,
            generation_config={
                "temperature": LLM_TEMPERATURE,
                "max_output_tokens": LLM_MAX_OUTPUT_TOKENS,
            },
        )
        text = getattr(resp, "text", "") or ""
        text = text.strip()
        return text if text else "I couldn't generate a response."
    except Exception as e:
        print(f"LLM error: {repr(e)}")
        if not GEMINI_API_KEY:
            return "GEMINI_API_KEY is not set. Please add it to your .env and restart."
        return "I had an issue contacting the AI service."

# Text-to-Speech
engine = pyttsx3.init()
def speak(text):
    print("🤖 Jarvis:", text)
    engine.say(text)
    engine.runAndWait()

# Speech-to-Text
recognizer = sr.Recognizer()
def listen(timeout=5.0, phrase_time_limit=8.0):
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return ""
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return ""
    except Exception:
        return ""

def extract_command_after_wake(text, wake="jarvis"):
    t = text.lower().strip()
    if not t.startswith(wake):
        return None
    return t[len(wake):].strip()

# Task Execution
def execute_command(command):
    command = command.lower()

    if "open youtube" in command:
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube")
        return True

    elif "open google" in command:
        webbrowser.open("https://google.com")
        speak("Opening Google")
        return True

    elif "time" in command:
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
        return True

    elif "open spotify" in command:
        try: 
            # search_url = "https://open.spotify.com/search/" + urllib.parse.quote(query)
            # webbrowser.open(search_url)
            os.startfile("spotify")
            speak("Opening Spotify")
            return True
        except Exception:
            speak("I couldn't open Spotify. Please make sure it is installed and try again.")
            return False

    elif "play" in command and "spotify" in command:
        song = command.replace("play", "").replace("on spotify", "").strip()
        if song:
            speak(f"Searching for {song} on Spotify")
            os.startfile(f"spotify:search:{song}")
        else:
            speak("What would you like me to play on spotify?")

        return True

    elif "shutdown" in command:
        confirm_and_shutdown()
        return True

    return False  # Not a direct system command, send to Gemini

# Main Jarvis Loop
def confirm_and_shutdown():
    speak("Do you really want to shut down? Say 'yes' to confirm.")
    resp = listen()
    if resp and "yes" in resp.lower():
        speak("Shutting down now.")
        os.system("shutdown /s /t 1")
    else:
        speak("Cancelled shutdown.")

def jarvis():
    speak("Hello, I am Jarvis. How can I help you?")
    while True:
        query = listen()
        if not query:
            continue

        print("🗣️ You:", query)

        if "exit" in query or "quit" in query:
            speak("Goodbye, shutting down.")
            break

        if REQUIRE_WAKE_WORD:
            cmd = extract_command_after_wake(query)
            if cmd is None:
                # Ignore speech without the wake word
                continue
        else:
            cmd = query

        # Check if it's a system command
        if not execute_command(cmd):
            # Otherwise, ask Gemini safely
            answer = ask_llm(cmd)
            speak(answer)

# Run Jarvis
jarvis()
