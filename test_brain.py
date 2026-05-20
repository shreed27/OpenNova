import os
import unittest
from unittest.mock import Mock, patch

import requests

from core.brain import BrainManager


class BrainManagerProviderTests(unittest.TestCase):
    def test_parse_openai_style_response_centralizes_tool_calls(self):
        data = {
            "choices": [
                {
                    "message": {
                        "content": "",
                        "tool_calls": [
                            {
                                "id": "call_1",
                                "type": "function",
                                "function": {"name": "get_weather", "arguments": '{"city":"Mumbai"}'},
                            }
                        ],
                    }
                }
            ]
        }

        response = BrainManager.response_from_openai_payload(data)

        message = response.choices[0].message
        self.assertEqual(message.tool_calls[0].function.name, "get_weather")
        self.assertEqual(message.tool_calls[0].function.arguments, '{"city":"Mumbai"}')

    @patch.dict(os.environ, {"JARVIS_BRAIN": "openai", "OPENAI_API_KEY": "key"}, clear=True)
    @patch("core.brain.requests.post")
    def test_openai_call_uses_timeout(self, post):
        post.return_value = Mock(
            json=Mock(return_value={"choices": [{"message": {"content": "ok"}}]}),
            raise_for_status=Mock(),
        )

        BrainManager()._call_openai([{"role": "user", "content": "hi"}], None)

        self.assertEqual(post.call_args.kwargs["timeout"], 30)

    @patch.dict(os.environ, {"JARVIS_BRAIN": "gemini", "GEMINI_API_KEY": "key"}, clear=True)
    @patch("core.brain.requests.post")
    def test_gemini_rest_call_uses_timeout(self, post):
        post.return_value = Mock(
            json=Mock(return_value={"choices": [{"message": {"content": "ok"}}]}),
            raise_for_status=Mock(),
        )

        BrainManager()._call_gemini_rest([{"role": "user", "content": "hi"}], None)

        self.assertEqual(post.call_args.kwargs["timeout"], 30)

    @patch.dict(os.environ, {"JARVIS_BRAIN": "ollama"}, clear=True)
    @patch("core.brain.requests.post", side_effect=requests.Timeout("slow"))
    def test_ollama_unavailable_returns_mock_response(self, _post):
        response = BrainManager()._call_ollama([], None)

        self.assertIn("Could not connect", response.choices[0].message.content)


if __name__ == "__main__":
    unittest.main()
