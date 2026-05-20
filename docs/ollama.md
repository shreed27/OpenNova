# Ollama Setup

1. Install Ollama from https://ollama.com.
2. Pull a model, for example:
   ```bash
   ollama pull llama3
   ```
3. Set local mode in `.env`:
   ```ini
   JARVIS_BRAIN=ollama
   OLLAMA_MODEL=llama3
   ```
4. Check setup:
   ```bash
   python3 main.py --doctor
   ```
