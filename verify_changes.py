import os
import subprocess
import sys

from dotenv import load_dotenv

from core.doctor import run_doctor
from core.registry import SkillRegistry


def run(command):
    print(f"$ {' '.join(command)}", flush=True)
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def show_config_status():
    load_dotenv()
    report = run_doctor()
    for key, value in report["env"].items():
        print(f"{key}: {value}", flush=True)
    print(f"Ollama available: {report['ollama']['available']}", flush=True)
    print("Optional install groups:", flush=True)
    for group, status in report["optional_groups"].items():
        missing = ", ".join(status["missing"]) if status["missing"] else "none"
        print(f"- {group}: missing {missing}", flush=True)


def show_skill_status():
    registry = SkillRegistry()
    skills_dir = os.path.join(os.path.dirname(__file__), "skills")
    registry.load_skills(skills_dir)
    print(f"Loaded skills: {', '.join(sorted(registry.skills))}", flush=True)
    if registry.skipped_modules:
        print("Skipped skills:", flush=True)
        for name, error in sorted(registry.skipped_modules.items()):
            report = run_doctor()
            group = report["skill_optional_groups"].get(name, "unknown")
            print(f"- {name}: {error} (install group: {group})", flush=True)


if __name__ == "__main__":
    show_config_status()
    show_skill_status()
    run([sys.executable, "-m", "pytest", "-q"])
