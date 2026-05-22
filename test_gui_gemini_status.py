import unittest

from gui.gemini_status import build_gemini_live_status


class GeminiLiveStatusFormattingTests(unittest.TestCase):
    def test_ready_status_uses_ready_label_and_message(self):
        status = build_gemini_live_status(None)

        self.assertEqual(status["label"], "GEMINI LIVE: READY")
        self.assertEqual(status["color"], "#00FFFF")
        self.assertIn("ready to launch", status["detail"].lower())

    def test_unavailable_status_keeps_reason_visible(self):
        error_message = "Gemini Live is unavailable: `GEMINI_API_KEY` is not set in the environment."

        status = build_gemini_live_status(error_message)

        self.assertEqual(status["label"], "GEMINI LIVE: UNAVAILABLE")
        self.assertEqual(status["color"], "#FFA500")
        self.assertEqual(status["detail"], error_message)


if __name__ == "__main__":
    unittest.main()
