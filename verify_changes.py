import os
import subprocess
import sys

from dotenv import load_dotenv

from core.registry import SkillRegistry


def run(command):
    print(f"$ {' '.join(command)}")
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def show_config_status():
    load_dotenv()
    keys = [
        "JARVIS_BRAIN",
        "GROQ_API_KEY",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "OPENWEATHERMAP_API_KEY",
        "EMAIL_ADDRESS",
        "TELEGRAM_BOT_TOKEN",
    ]
    for key in keys:
        value = "set" if os.environ.get(key) else "missing"
        print(f"{key}: {value}")


def show_skill_status():
    registry = SkillRegistry()
    skills_dir = os.path.join(os.path.dirname(__file__), "skills")
    registry.load_skills(skills_dir)
    print(f"Loaded skills: {', '.join(sorted(registry.skills))}")
    if registry.skipped_modules:
        print("Skipped skills:")
        for name, error in sorted(registry.skipped_modules.items()):
            print(f"- {name}: {error}")


if __name__ == "__main__":
    show_config_status()
    show_skill_status()
    run([sys.executable, "-m", "pytest", "-q"])
