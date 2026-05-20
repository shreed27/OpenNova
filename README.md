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

**Open-Nova** is an aggressively engineered, fully modular AI orchestrator built for the cracked dev. No bloated web wrappers. No mandatory subscriptions. Just pure, unadulterated Python hooking raw LLM power directly into your OS.

Inspired by the OG viral agents, Nova turns your local rig into a highly autonomous node. Whether you are running Llama 3 locally via Ollama, pushing 1000 t/s with Groq, or streaming live multimodal websockets with Gemini, Nova controls your machine, reads your files, and executes your will.

## 🔥 WHY IT'S CRACKED

* 🧠 **MULTI-BRAIN HYPER-ROUTER:** Seamlessly switch between `groq`, `ollama` (100% offline), `openai`, and `gemini`. Hot-swap models in a `.env` file without breaking a sweat.
* 🖥️ **PYQT6 CYBER HUD:** An insanely polished, transparent glassmorphic UI. 
  * Features a **Real-Time PyAudio Arc Reactor** that physically pulses to your voice.
  * **Live Hardware Telemetry** (`psutil`) streaming CPU, RAM, and Disk metrics directly to the HUD.
* 📱 **TELEGRAM REMOTE C&C:** Securely text your machine from your phone. Take remote screenshots, run shell commands, or query local documents while you're offline.
* ⚡ **DYNAMIC SKILL INJECTION:** Drop a `.py` file in the `/skills` folder. Nova instantly parses it, generates the OpenAI tool schema, and equips the ability in real-time.

## 🛠️ THE ARSENAL

Out of the box, Nova is weaponized with:
- `system_ops.py` & `file_ops.py`: Brightness, volume, file CRUD, app execution.
- `camera_skill.py` & `screenshot_ops.py`: Local webcam capture and screen awareness.
- `detection_skill.py`: YOLO-based real-time object detection.
- `whatsapp_skill.py`: Headless WhatsApp automation.
- `gemini_live_skill.py`: Next-Gen WebSocket A/V streaming.

## 🚀 JACKING IN (QUICK START)

### 1. Initialize the Node
```bash
git clone https://github.com/shreed27/OpenNova.git
cd Nova
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

For a lighter install, start with `requirements-base.txt` and add optional groups only when needed:
`requirements-gui.txt`, `requirements-voice.txt`, `requirements-gemini-live.txt`, `requirements-whatsapp.txt`, or `requirements-detection.txt`.

### 2. Configure Neural Links
Create `.env` in the root. Start from `.env.template` and supply the providers you want.
```ini
# CORE PROTOCOL [groq | ollama | gemini | openai]
JARVIS_BRAIN=groq

# KEYS TO THE CITY
GROQ_API_KEY=gsk_your_key_here
# GEMINI_API_KEY=AIza...
# OPENAI_API_KEY=sk-...

# OLLAMA OVERRIDE (for local runners)
OLLAMA_MODEL=llama3

# WEATHER (optional)
# OPENWEATHERMAP_API_KEY=...
# DEFAULT_CITY=Mumbai

# EMAIL (optional)
# EMAIL_ADDRESS=you@gmail.com
# EMAIL_PASSWORD=gmail_app_password
# EMAIL_IMAP_SERVER=imap.gmail.com

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
python3 main.py --text
```

Text mode starts the assistant without importing the PyQt HUD. Type commands at `JARVIS>` and use `quit` to stop.

**Run first-use diagnostics:**
```bash
python3 main.py --doctor
```

## 🔐 SAFE MODE
Risky actions such as file writes, app launches, screenshots, volume changes, and external messages require explicit confirmation by default. Tool calls can pass `confirm=true`, or you can opt into trusted local mode:
```ini
JARVIS_TRUSTED_MODE=true
```

## ✅ VERIFY
```bash
python3 verify_changes.py
python3 -m pytest -q
PYTHONPYCACHEPREFIX=/private/tmp/project_jarvis_pycache python3 -m compileall -q core gui skills main.py gemini_client.py
```

`verify_changes.py` prints local config status, loads available skills, reports skipped optional skills, and runs pytest. The WhatsApp browser login smoke test is marked as manual because it opens a browser and waits for QR login.

## OPTIONAL CAPABILITY NOTES
- **GUI HUD:** requires `PyQt6`, `psutil`, `PyAudio`, and microphone permissions.
- **Voice:** `SpeechRecognition` and `PyAudio` are needed for listening; macOS `say` is used as a robust speech fallback.
- **WhatsApp:** requires `selenium`, `webdriver-manager`, Chrome/Chromium, and a local browser profile login.
- **Gemini Live:** requires `GEMINI_API_KEY` and the `google-genai` runtime.
- **Object Detection:** requires `ultralytics`, `torch`, `torchvision`, and the local `yolov8n.pt` model.

Detailed setup guides live in `docs/`:
- `docs/ollama.md`
- `docs/gemini-live.md`
- `docs/whatsapp.md`
- `docs/email.md`
- `docs/detection.md`
- `docs/macos-permissions.md`

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
