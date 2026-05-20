import sys
import subprocess
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

# Initialize engine globally to avoid re-initialization issues
engine = pyttsx3.init() if pyttsx3 else None

# Set voice to deep male voice
def set_deep_male_voice():
    if not engine:
        return
    voices = engine.getProperty('voices')
    for voice in voices:
        # Prefer "Daniel" for deep male voice on Mac
        if "Daniel" in voice.name:
            engine.setProperty('voice', voice.id)
            return
    # Fallback to any male voice if Daniel not found
    for voice in voices:
        if "male" in voice.name.lower() or "male" in str(voice.gender).lower():
             engine.setProperty('voice', voice.id)
             return

set_deep_male_voice()

# Global flag to check if Jarvis is speaking
is_speaking = False

def speak(text):
    global is_speaking
    if "{" in text and "}" in text and "status" in text:
        text = "Task completed."
    
    # Print first so user sees it even if audio fails
    print(f"JARVIS: {text}")

    # Set flag to True before speaking
    is_speaking = True
    
    try:
        # On macOS with a GUI/Threading environment, pyttsx3's loop often conflicts 
        # with the main thread event loop (PyQt). Default to system 'say' command on macOS
        # to avoid hangs/crashes unless we are strictly in a non-GUI text mode.
        if sys.platform == "darwin":
            try:
                subprocess.run(["say", text], check=False)
                return
            except Exception as e2:
                print(f"TTS Fallback Error: {e2}")
                # Fall through to pyttsx3 if 'say' fails (unlikely)
    
        # Try pyttsx3
        if not engine:
            print("TTS is unavailable. Install pyttsx3 or use macOS say.")
            return

        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
            
    finally:
        # Ensure flag is reset to False even if errors occur
        is_speaking = False

def listen():
    global is_speaking
    # if system is speaking, don't listen
    if is_speaking:
        return "none"

    if not sr:
        print("Speech recognition is unavailable. Install SpeechRecognition and PyAudio for voice input.")
        return "none"

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 0.8
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5)
            print("Recognizing...")
            query = r.recognize_google(audio)
            return query.lower()
        except Exception:
            return "none"
