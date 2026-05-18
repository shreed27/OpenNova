<div align="center">

<pre>
      ___           ___           ___           ___           ___           ___     
     /\  \         /\  \         /\  \         /\__\         /\  \         /\  \    
    _\:\  \       /::\  \       /::\  \       /:/  /        _\:\  \       /::\  \   
   /\ \:\  \     /:/\:\  \     /:/\:\  \     /:/  /        /\ \:\  \     /:/\ \  \  
  _\:\ \:\  \   /::\~\:\  \   /::\~\:\  \   /:/__/  ___   _\:\ \:\  \   _\:\~\ \  \ 
 /\ \:\ \:\__\ /:/\:\ \:\__\ /:/\:\ \:\__\  |:|  | /\__\ /\ \:\ \:\__\ /\ \:\ \:\__\
 \:\ \:\/:/  / \/__\:\/:/  / \/_|::\/:/  /  |:|  |/:/  / \:\ \:\/:/  / \:\ \:\ \/__/
  \:\ \::/  /       \::/  /     |:|::/  /   |:|__/:/  /   \:\ \::/  /   \:\ \:\__\  
   \:\/:/  /        /:/  /      |:|\/__/     \::::/__/     \:\/:/  /     \:\/:/  /  
    \::/  /        /:/  /       |:|  |        ~~~~          \::/  /       \::/  /   
     \/__/         \/__/         \|__|                       \/__/         \/__/    
</pre>

<h1>⚡ Open-Nova ⚡</h1>

<b>The autonomous, local-first, multimodal OS controller that breaks the matrix.</b>

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-cyan.svg?style=for-the-badge&logo=python)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-magenta.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Local AI](https://img.shields.io/badge/Ollama-Offline_First-000000.svg?style=for-the-badge&logo=ollama)](https://ollama.ai)
[![Cyberpunk](https://img.shields.io/badge/Vibe-Cyberpunk-ff0055.svg?style=for-the-badge)]()

</div>

<br>

> **"Wake up, Samurai. We have a system to automate."**

**JARVIS** is an aggressively engineered, fully modular AI orchestrator built for the cracked dev. No bloated web wrappers. No mandatory subscriptions. Just pure, unadulterated Python hooking raw LLM power directly into your OS.

Inspired by the OG viral agents, JARVIS turns your local rig into a highly autonomous node. Whether you are running Llama 3 locally via Ollama, pushing 1000 t/s with Groq, or streaming live multimodal websockets with Gemini, JARVIS controls your machine, reads your files, and executes your will.

## 🔥 WHY IT'S CRACKED

* 🧠 **MULTI-BRAIN HYPER-ROUTER:** Seamlessly switch between `groq`, `ollama` (100% offline), `openai`, and `gemini`. Hot-swap models in a `.env` file without breaking a sweat.
* 🖥️ **PYQT6 CYBER HUD:** An insanely polished, transparent glassmorphic UI. 
  * Features a **Real-Time PyAudio Arc Reactor** that physically pulses to your voice.
  * **Live Hardware Telemetry** (`psutil`) streaming CPU, RAM, and Disk metrics directly to the HUD.
* 📱 **TELEGRAM REMOTE C&C:** Securely text your machine from your phone. Take remote screenshots, run shell commands, or query local documents while you're offline.
* ⚡ **DYNAMIC SKILL INJECTION:** Drop a `.py` file in the `/skills` folder. JARVIS instantly parses it, generates the OpenAI tool schema, and equips the ability in real-time.

## 🛠️ THE ARSENAL

Out of the box, JARVIS is weaponized with:
- `system_ops.py` & `file_ops.py`: Brightness, volume, file CRUD, app execution.
- `camera_skill.py` & `screenshot_ops.py`: Local webcam capture and screen awareness.
- `detection_skill.py`: YOLO-based real-time object detection.
- `whatsapp_skill.py`: Headless WhatsApp automation.
- `gemini_live_skill.py`: Next-Gen WebSocket A/V streaming.

## 🚀 JACKING IN (QUICK START)

### 1. Initialize the Node
```bash
git clone https://github.com/shreed27/OpenNova.git
cd JARVIS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Neural Links
Create `.env` in the root. Supply what you want, ignore what you don't.
```ini
# CORE PROTOCOL [groq | ollama | gemini | openai]
JARVIS_BRAIN=groq

# KEYS TO THE CITY
GROQ_API_KEY=gsk_your_key_here
# GEMINI_API_KEY=AIza...
# OPENAI_API_KEY=sk-...

# OLLAMA OVERRIDE (For local runners)
OLLAMA_MODEL=llama3

# TELEGRAM C&C LINK (Optional)
# TELEGRAM_BOT_TOKEN=your_bot_token
```

### 3. Execute
**Boot Full Cyber HUD (Voice + Telemetry + Terminal):**
```bash
python main.py
```
*HUD loads.* Speak your command. Watch the reactor pulse. Click the core to drop into secure text-only override and type commands directly into the terminal!

**Boot Stealth Mode (CLI Only):**
```bash
python main.py --text
```

## 🏗️ SYSTEM ARCHITECTURE
```text
JARVIS/
├── core/               # Neural Pathways (BrainManager, Registry, Audio I/O)
├── gui/                # Cybernetic HUD (PyQt6 rendering, PyAudio threaded streams)
├── skills/             # Modular Arsenals (Auto-loaded tools)
└── main.py             # Main Orchestration Loop
```

## ⚠️ WARNING
This software grants an autonomous agent root-level access to execute shell commands, edit files, and send messages on your hardware. **DO NOT** expose your Telegram Bot Token or run experimental skills without checking the code. 

**With absolute power comes absolute responsibility. Don't brick your rig.**

---
<div align="center">
<i>Built for the hackers, by the hackers. Code is Law.</i>
</div>
