<div align="center">
  <h1>🤖 JARVIS PROTOCOL v2.0</h1>
  <p><b>The local, autonomous, multimodal AI gateway for your machine.</b></p>
  
  [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Local AI](https://img.shields.io/badge/Ollama-Local_First-000000.svg)](https://ollama.ai)
  [![Status](https://img.shields.io/badge/Status-Cracked-ff69b4.svg)]()
</div>

---

**JARVIS** is not just another wrapper. It is a highly extensible, modular, and autonomous AI assistant designed to run as a secure local gateway on your machine. Inspired by the OG open-source agent frameworks, JARVIS connects state-of-the-art LLMs directly to your local file system, OS commands, and external messaging platforms.

It features a **Futuristic Cyber HUD** (built in PyQt6) with real-time mic visualizers and system hardware telemetry, a **Multi-Brain Engine** supporting local and remote models, and a **Telegram Remote Gateway** so you can securely command your Mac from your phone.

## 🌟 Elite Features

- **🧠 Multi-Brain Architecture**: Instantly switch between **Groq**, **Ollama** (100% local/offline), **Gemini** (Live Multimodal), and **OpenAI**. No vendor lock-in.
- **📱 Telegram Remote Gateway**: Text your home computer to take screenshots, run shell commands, or trigger complex skills securely from anywhere.
- **🖥️ Cybernetic HUD**: An insanely polished PyQt6 interface featuring:
  - **Voice-Pulse Arc Reactor**: The core dynamically expands and glows based on your real-time mic audio levels (RMS).
  - **Live Hardware Telemetry**: Real-time CPU, RAM, and Disk metrics feeding directly into the UI.
  - **Glassmorphic Terminal**: Drop down into the built-in terminal and chat with JARVIS via text without leaving the HUD.
- **🔌 Modular Skill System**: Drop a new Python file into the `skills/` directory and JARVIS learns a new capability instantly.

## 🛠️ The Arsenal (Skills)

JARVIS comes loaded with powerful capabilities out of the box:
- **System Control**: Screen brightness, volume control, file manipulation, and direct application execution (`system_ops`, `file_ops`).
- **Vision & Sensing**: YOLO-powered real-time object detection (`detection_skill`), Webcam capture (`camera_skill`), and screen awareness (`screenshot_ops`).
- **Communication Automation**: Headless WhatsApp message dispatching (`whatsapp_skill`) and Email management (`email_ops`).
- **Web Intelligence**: Search the web and scrape data autonomously (`web_ops`).
- **Gemini Live**: Native WebSockets connection to Gemini 2.0 Flash for real-time video/audio conversation (`gemini_live_skill`).

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/shreed27/OpenNova.git
cd JARVIS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root directory. Mix and match the keys for the brains and gateways you want to use.
```ini
# --- THE BRAIN ---
# Set to: groq, ollama, gemini, or openai
JARVIS_BRAIN=groq

GROQ_API_KEY=your_groq_key
# GEMINI_API_KEY=your_gemini_key
# OPENAI_API_KEY=your_openai_key
# OLLAMA_MODEL=llama3 (defaults to localhost:11434)

# --- THE GATEWAY (Optional) ---
# TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 3. Initialize the Protocol
**Launch Full HUD (Voice + Text + Telemetry):**
```bash
python main.py
```
- The HUD will boot up.
- Speak naturally to interact. The Arc Reactor will pulse with your voice.
- Click the reactor to pause voice recognition and type directly into the terminal.

**Launch Stealth Text-Only Mode:**
```bash
python main.py --text
```

## 🏗️ Architecture
```
JARVIS/
├── core/               # The Engine (BrainManager, SkillRegistry, Voice I/O)
├── gui/                # Cyber HUD (PyQt6 rendering, PyAudio threads, Telemetry)
├── skills/             # The Arsenal (Drop-in Python modules)
└── main.py             # Entry point & Thread Orchestrator
```

## 🛡️ Security Warning
JARVIS has the ability to execute shell commands, read files, and manipulate your system. Do **not** expose the Telegram Gateway without properly securing your bot token, and be extremely careful when granting JARVIS root-level access. You are building an autonomous agent on your local hardware. **With great power comes great responsibility.**

---
<div align="center">
<i>Built for the hackers, by the hackers.</i>
</div>
