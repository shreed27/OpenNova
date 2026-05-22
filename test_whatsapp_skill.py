import sys
import types
import unittest
from unittest.mock import Mock, patch

fake_client_module = types.ModuleType("skills.whatsapp.whatsapp_client")


class FakeWhatsAppClient:
    def send_message(self, **kwargs):
        raise NotImplementedError


fake_client_module.WhatsAppClient = FakeWhatsAppClient
sys.modules.setdefault("skills.whatsapp.whatsapp_client", fake_client_module)

from skills.whatsapp_skill import WhatsappSkill


class WhatsappSkillTests(unittest.TestCase):
    @patch.object(WhatsappSkill, "_load_contacts", return_value={})
    def test_send_message_uses_chat_name_when_contacts_missing(self, _load_contacts):
        skill = WhatsappSkill()
        client = Mock()
        client.send_message.return_value = "Message sent to chat 'Dad'"
        skill.client = client

        result = skill.send_whatsapp_message("Dad", "Hello")

        self.assertEqual(result, "Message sent to chat 'Dad'")
        client.send_message.assert_called_once_with(
            contact_name="Dad",
            message="Hello",
            phone_number=None,
        )

    @patch.object(WhatsappSkill, "_load_contacts", return_value={"dad": "+15551234567"})
    def test_send_message_passes_phone_number_as_fallback(self, _load_contacts):
        skill = WhatsappSkill()
        client = Mock()
        client.send_message.return_value = "Message sent to +15551234567"
        skill.client = client

        result = skill.send_whatsapp_message("Dad", "Hello")

        self.assertEqual(result, "Message sent to +15551234567")
        client.send_message.assert_called_once_with(
            contact_name="Dad",
            message="Hello",
            phone_number="+15551234567",
        )


if __name__ == "__main__":
    unittest.main()
