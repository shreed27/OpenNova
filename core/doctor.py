import importlib.util
import os
import platform
import socket
import sys


OPTIONAL_GROUPS = {
    "gui": ["PyQt6", "psutil", "pyaudio"],
    "voice": ["speech_recognition", "pyaudio", "pyttsx3"],
    "gemini_live": ["google.genai"],
    "whatsapp": ["selenium", "webdriver_manager"],
    "detection": ["ultralytics", "torch", "torchvision"],
}

SKILL_OPTIONAL_GROUPS = {
    "whatsapp_skill": "whatsapp",
    "detection_skill": "detection",
    "gemini_live_skill": "gemini_live",
}

ENV_KEYS = [
    "JARVIS_BRAIN",
    "GROQ_API_KEY",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "OPENWEATHERMAP_API_KEY",
    "EMAIL_ADDRESS",
    "TELEGRAM_BOT_TOKEN",
    "JARVIS_TRUSTED_MODE",
]


def _module_available(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ValueError):
        return False


def _ollama_available(host="127.0.0.1", port=11434, timeout=0.2) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def run_doctor() -> dict:
    optional_groups = {}
    for group, modules in OPTIONAL_GROUPS.items():
        optional_groups[group] = {
            "installed": [module for module in modules if _module_available(module)],
            "missing": [module for module in modules if not _module_available(module)],
        }

    return {
        "python": {
            "version": platform.python_version(),
            "major": sys.version_info.major,
            "minor": sys.version_info.minor,
        },
        "platform": platform.platform(),
        "env": {key: "set" if os.environ.get(key) else "missing" for key in ENV_KEYS},
        "optional_groups": optional_groups,
        "skill_optional_groups": SKILL_OPTIONAL_GROUPS,
        "ollama": {"available": _ollama_available()},
        "notes": [
            "Camera, microphone, screen capture, and browser automation still require local OS permissions.",
            "Skipped optional skills can be enabled by installing the matching optional group.",
        ],
    }
