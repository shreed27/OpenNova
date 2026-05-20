import json
import unittest
from unittest.mock import Mock, patch

import requests

from skills.email_ops import EmailSkill
from skills.telegram_ops import TelegramGatewaySkill


class EmailLifecycleTests(unittest.TestCase):
    @patch("skills.email_ops.imaplib.IMAP4_SSL")
    def test_check_unread_logs_out_on_search_failure(self, imap_class):
        mail = Mock()
        mail.search.return_value = ("NO", [])
        imap_class.return_value = mail
        skill = EmailSkill()
        skill.email_address = "a@example.com"
        skill.email_password = "secret"

        result = json.loads(skill.check_unread_emails())

        self.assertEqual(result["status"], "error")
        mail.logout.assert_called_once()


class TelegramLifecycleTests(unittest.TestCase):
    @patch("skills.telegram_ops.requests.post", side_effect=requests.Timeout("slow"))
    def test_send_message_reports_request_failure(self, _post):
        skill = TelegramGatewaySkill()
        skill.bot_token = "token"

        result = skill.send_telegram_message("hello", chat_id="123", confirm=True)

        self.assertIn("Error sending Telegram message", result)

    @patch("skills.telegram_ops.requests.post")
    def test_send_message_uses_timeout(self, post):
        post.return_value = Mock(raise_for_status=Mock())
        skill = TelegramGatewaySkill()
        skill.bot_token = "token"

        result = skill.send_telegram_message("hello", chat_id="123", confirm=True)

        self.assertIn("successfully", result)
        self.assertEqual(post.call_args.kwargs["timeout"], 10)


if __name__ == "__main__":
    unittest.main()
