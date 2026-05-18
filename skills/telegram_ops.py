import os
import requests
import threading
import time
from core.skill import Skill

class TelegramGatewaySkill(Skill):
    """
    Acts as a long-polling Telegram bot running in a daemon thread.
    Intercepts messages and feeds them directly into the JARVIS command queue.
    """
    def __init__(self):
        super().__init__()
        self.bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.running = False
        self.context = None
        self.last_chat_id = None
        
    def initialize(self, context):
        self.context = context
        if self.bot_token:
            self.running = True
            t = threading.Thread(target=self._polling_loop, daemon=True)
            t.start()
            
            log_queue = self.context.get("log_queue")
            if log_queue:
                log_queue.put("<span style='color: #ff00ff;'>[GATEWAY]</span> Telegram Remote C&C link established.")
            
    def _polling_loop(self):
        offset = 0
        while self.running:
            try:
                url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates?timeout=30&offset={offset}"
                r = requests.get(url, timeout=35)
                if r.status_code == 200:
                    data = r.json()
                    for item in data.get("result", []):
                        offset = item["update_id"] + 1
                        
                        if "message" in item and "text" in item["message"]:
                            chat_id = item["message"]["chat"]["id"]
                            self.last_chat_id = chat_id
                            text = item["message"]["text"].strip()
                            
                            self._handle_command(chat_id, text)
            except Exception as e:
                # If network drops, wait and retry
                time.sleep(5)
                
    def _send_message(self, chat_id, text):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": text})

    def _handle_command(self, chat_id, text):
        log_queue = self.context.get("log_queue")
        if log_queue:
            log_queue.put(f"<span style='color: #ff00ff;'>[TELEGRAM]</span> {text}")
            
        # Hardcoded Gateway Commands
        if text.startswith("/status"):
            self._send_message(chat_id, "JARVIS V2 Online. Systems Nominal.")
            return
            
        if text.startswith("/ping"):
            self._send_message(chat_id, "Pong. Gateway is active.")
            return

        # Forward the command directly to JARVIS Engine via the queue
        command_queue = self.context.get("command_queue")
        if command_queue:
            command_queue.put(text)
            self._send_message(chat_id, f"Queued: {text}")
            
    def get_functions(self):
        return {
            "send_telegram_message": self.send_telegram_message
        }
        
    def get_tools(self):
        return [{
            "type": "function",
            "function": {
                "name": "send_telegram_message",
                "description": "Send a message via Telegram to the user. Useful for notifying them of events or completion of long tasks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "The message text to send"},
                        "chat_id": {"type": "string", "description": "The Telegram chat ID (if known). If empty, broadcasts to the last known chat ID."}
                    },
                    "required": ["text"]
                }
            }
        }]
        
    def send_telegram_message(self, text: str, chat_id: str = "") -> str:
        """Called by JARVIS Engine as a Tool"""
        target_chat = chat_id if chat_id else self.last_chat_id
        if not target_chat:
            return "Error: No Telegram chat ID known to send message to."
            
        if not self.bot_token:
            return "Error: TELEGRAM_BOT_TOKEN is not configured."
            
        self._send_message(target_chat, text)
        return "Message sent successfully via Telegram."

def get_skill():
    return TelegramGatewaySkill()
