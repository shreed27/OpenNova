import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from skills.gemini_live_skill import GeminiLiveSkill


class DummyEvent:
    def __init__(self):
        self._set = False

    def set(self):
        self._set = True

    def clear(self):
        self._set = False

    def is_set(self):
        return self._set


class GeminiLiveSkillTests(unittest.TestCase):
    def setUp(self):
        self.skill = GeminiLiveSkill()
        self.pause_event = DummyEvent()
        self.skill.initialize({"pause_event": self.pause_event})

    @patch("skills.gemini_live_skill.os.path.exists", return_value=True)
    @patch("skills.gemini_live_skill.subprocess.run")
    def test_preflight_failure_is_user_facing_and_does_not_pause(self, mock_run, _exists):
        mock_run.return_value = SimpleNamespace(
            returncode=1,
            stdout="Gemini Live is unavailable: missing dependency google-genai.",
            stderr="",
        )

        result = self.skill.start_live_vision()

        self.assertEqual(result, "Gemini Live is unavailable: missing dependency google-genai.")
        self.assertFalse(self.pause_event.is_set())
        mock_run.assert_called_once()

    @patch("skills.gemini_live_skill.os.path.exists", return_value=True)
    @patch("skills.gemini_live_skill.threading.Thread")
    @patch("skills.gemini_live_skill.subprocess.Popen")
    @patch("skills.gemini_live_skill.subprocess.run")
    def test_successful_launch_pauses_and_spawns_monitor(self, mock_run, mock_popen, mock_thread, _exists):
        mock_run.return_value = SimpleNamespace(returncode=0, stdout="", stderr="")
        process = Mock()
        mock_popen.return_value = process
        monitor_thread = Mock()
        mock_thread.return_value = monitor_thread

        result = self.skill.start_live_vision()

        self.assertIn("Live Vision System started", result)
        self.assertTrue(self.pause_event.is_set())
        mock_run.assert_called_once()
        mock_popen.assert_called_once()
        mock_thread.assert_called_once()
        monitor_thread.start.assert_called_once()


if __name__ == "__main__":
    unittest.main()
