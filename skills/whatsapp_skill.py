from core.skill import Skill
import json
import os
from skills.whatsapp.whatsapp_client import WhatsAppClient

class WhatsappSkill(Skill):
    """
    Skill for sending WhatsApp messages using Selenium.
    """
    
    def __init__(self):
        self.contacts = self._load_contacts()
        self.client = None # Lazy load the client

    @property
    def name(self):
        return "whatsapp_skill"
        
    def _load_contacts(self):
        contacts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "contacts.json")
        if not os.path.exists(contacts_path):
            return {}
        try:
            with open(contacts_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading contacts: {e}")
            return {}

    def _get_client(self):
        if not self.client:
            self.client = WhatsAppClient()
        return self.client

    def get_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "send_whatsapp_message",
                    "description": "Send a WhatsApp message to a specific person by name.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the contact (e.g., 'Dad', 'Mom')."
                            },
                            "message": {
                                "type": "string",
                                "description": "The message to send."
                            }
                        },
                        "required": ["name", "message"],
                    },
                },
            }
        ]

    def get_functions(self):
        return {
            "send_whatsapp_message": self.send_whatsapp_message
        }

    def send_whatsapp_message(self, name, message):
        """
        Sends a WhatsApp message by existing chat name when possible,
        with optional phone-number fallback from contacts.json.
        """
        clean_name = name.lower().strip()
        phone_number = self.contacts.get(clean_name)

        try:
            client = self._get_client()
            result = client.send_message(
                contact_name=name.strip(),
                message=message,
                phone_number=phone_number,
            )
            return result
        except Exception as e:
            return f"Error sending message: {e}"
