import os
import sys
import argparse
import threading 
import time
import queue
import re
from queue import Empty
from typing import Any, Dict, Optional, Tuple
from dotenv import load_dotenv
from core.voice import speak, listen
from core.registry import SkillRegistry
from core.engine import JarvisEngine

# Load Env
load_dotenv()


def _normalize_queued_command(command: Any) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    if isinstance(command, dict):
        text = command.get("text")
        if isinstance(text, str):
            return text, command
        return None, command

    if isinstance(command, str):
        return command, None

    return None, None


def _send_telegram_response(registry: SkillRegistry, metadata: Optional[Dict[str, Any]], response: str):
    if not metadata or metadata.get("source") != "telegram" or not response:
        return

    send_telegram_message = registry.get_function("send_telegram_message")
    if not send_telegram_message:
        return

    try:
        send_telegram_message(
            text=response,
            chat_id=str(metadata.get("chat_id", "")),
            reply_to_message_id=str(metadata.get("message_id", "")),
        )
    except Exception as exc:
        print(f"Failed to send Telegram response: {exc}")


def _strip_wake_word(command: str) -> str:
    return re.sub(r"\bjarvis\b", "", command, flags=re.IGNORECASE).strip()


def jarvis_loop(context, registry, args):
    """
    Main loop for JARVIS, running in a separate thread.
    Checks command_queue for typed commands, or listens for voice.
    """
    pause_event = context.get("pause_event")
    command_queue = context.get("command_queue")
    log_queue = context.get("log_queue")
    
    def log(msg):
        print(msg)
        if log_queue:
            log_queue.put(msg)

    # Initialize Engine
    jarvis = JarvisEngine(registry)

    if args.text:
        log("<span style='color: #00FFFF;'>[SYS] JARVIS Online. Ready for command (Text Mode).</span>")
    else:
        log("<span style='color: #00FFFF;'>[SYS] JARVIS Online. Ready for voice command.</span>")
        speak("Jarvis Online. Ready for command.")

    while True:
        user_query = None
        command_metadata = None
        
        # 1. Check for Typed Commands (Highest Priority)
        try:
            if command_queue:
                queued_command = command_queue.get_nowait()
                user_query, command_metadata = _normalize_queued_command(queued_command)
        except Empty:
            pass
            
        # 2. If no typed command, try voice/cli (if not paused)
        if not user_query:
            if pause_event and pause_event.is_set():
                time.sleep(0.5)
                continue
                
            if args.text:
                try:
                    # In text mode without GUI, input() blocks. 
                    # If using GUI, args.text usually isn't used for CLI input anymore.
                    time.sleep(0.5) 
                    continue
                except EOFError:
                    break
            else:
                user_query = listen()
                
            # Double check pause after listening
            if pause_event and pause_event.is_set():
                continue

        if user_query == "none" or not user_query:
            continue

        normalized_query = user_query.lower()
        
        if "quit" in normalized_query:
            log("<span style='color: #FF3333;'>[SYS] Shutting down JARVIS loop...</span>")
            speak("Shutting down.")
            break
        
        # Wake word / Command filtering Logic
        direct_commands = [
            "open", "volume", "search", "create", "write", "read", "make",
            "who", "what", "when", "where", "how", "why", "thank", "hello"
        ]
        
        is_direct = any(cmd in normalized_query for cmd in direct_commands)
        
        if "jarvis" not in normalized_query and not is_direct:
            log(f"<span style='color: #555;'>Ignored background chatter: {user_query}</span>")
            continue
            
        clean_query = _strip_wake_word(user_query)
        
        try:
            log(f"<span style='color: #FFA500;'>[JARVIS] Processing: {clean_query}...</span>")
            response = jarvis.run_conversation(clean_query)
            if response:
                _send_telegram_response(registry, command_metadata, response)
            
            if pause_event and pause_event.is_set() and not args.text:
                log("<span style='color: #555;'>[SYS] Skipped speech due to pause.</span>")
                # Still log the response text to the HUD
                log(f"<span style='color: #00FFCC;'>[JARVIS]</span> {response}")
                continue

            if response:
                log(f"<span style='color: #00FFCC;'>[JARVIS]</span> {response}")
                if not args.text:
                    speak(response)
        except Exception as e:
            log(f"<span style='color: #FF3333;'>[ERROR] Main Loop Error: {e}</span>")
            _send_telegram_response(registry, command_metadata, f"System error: {e}")
            if not args.text:
                speak("System error.")

def main():
    parser = argparse.ArgumentParser(description="JARVIS AI Assistant")
    parser.add_argument("--text", action="store_true", help="Run in text mode (no voice I/O)")
    args = parser.parse_args()
    run_app(args)


def build_context():
    # 1. Setup Thread Context
    pause_event = threading.Event()
    command_queue = queue.Queue()
    log_queue = queue.Queue()
    
    context = {
        "pause_event": pause_event,
        "command_queue": command_queue,
        "log_queue": log_queue
    }
    return context


def load_registry(context):
    # 2. Initialize Registry and Load Skills
    registry = SkillRegistry()
    skills_dir = os.path.join(os.path.dirname(__file__), "skills")
    registry.load_skills(skills_dir, context=context)
    return registry


def run_text_loop(context):
    command_queue = context.get("command_queue")

    while True:
        try:
            text = input("JARVIS> ").strip()
        except (EOFError, KeyboardInterrupt):
            text = "quit"

        if command_queue:
            command_queue.put(text)

        if text.lower() == "quit":
            break


def run_app(args):
    context = build_context()
    registry = load_registry(context)

    if args.text:
        t = threading.Thread(target=jarvis_loop, args=(context, registry, args), daemon=True)
        t.start()
        run_text_loop(context)
        t.join(timeout=2)
        return
    
    # 3. Start JARVIS Loop in Background Thread
    t = threading.Thread(target=jarvis_loop, args=(context, registry, args), daemon=True)
    t.start()
    
    # 4. Start GUI in Main Thread (Required for PyQt)
    run_gui(context)


def run_gui(context):
    from gui.app import run_gui as run_gui_app

    run_gui_app(context)

if __name__ == "__main__":
    main()
