import argparse
import queue
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch


voice_module = SimpleNamespace(speak=Mock(), listen=Mock(return_value="none"))
gui_app_module = SimpleNamespace(run_gui=Mock())

with patch.dict(
    sys.modules,
    {
        "core.voice": voice_module,
        "gui.app": gui_app_module,
        "groq": SimpleNamespace(Groq=Mock()),
    },
):
    import main


class MainModeTests(unittest.TestCase):
    def test_gui_mode_starts_background_loop_and_gui(self):
        registry = Mock()
        thread = Mock()

        with patch.object(main, "SkillRegistry", return_value=registry), \
            patch.object(main.threading, "Thread", return_value=thread), \
            patch.object(main, "run_gui") as run_gui:
            main.run_app(argparse.Namespace(text=False))

        registry.load_skills.assert_called_once()
        thread.start.assert_called_once()
        run_gui.assert_called_once()

    def test_text_mode_runs_without_gui(self):
        registry = Mock()
        thread = Mock()

        with patch.object(main, "SkillRegistry", return_value=registry), \
            patch.object(main.threading, "Thread", return_value=thread), \
            patch.object(main, "run_gui") as run_gui, \
            patch.object(main, "run_text_loop") as run_text_loop:
            main.run_app(argparse.Namespace(text=True))

        registry.load_skills.assert_called_once()
        thread.start.assert_called_once()
        thread.join.assert_called_once_with(timeout=2)
        run_gui.assert_not_called()
        run_text_loop.assert_called_once()

    def test_text_loop_queues_commands_until_quit(self):
        command_queue = queue.Queue()

        with patch("builtins.input", side_effect=["hello", "QUIT"]):
            main.run_text_loop({"command_queue": command_queue})

        first = command_queue.get_nowait()
        second = command_queue.get_nowait()
        self.assertEqual(first, "hello")
        self.assertEqual(second, "QUIT")

    def test_strip_wake_word_preserves_command_casing(self):
        self.assertEqual(
            main._strip_wake_word("JARVIS send WhatsApp to Shree"),
            "send WhatsApp to Shree",
        )

    def test_load_registry_logs_skipped_skills(self):
        registry = Mock()
        registry.skipped_modules = {"broken_skill": "missing optional package"}
        context = {"log_queue": queue.Queue()}

        with patch.object(main, "SkillRegistry", return_value=registry):
            result = main.load_registry(context)

        self.assertIs(result, registry)
        log_line = context["log_queue"].get_nowait()
        self.assertIn("broken_skill", log_line)
        self.assertIn("missing optional package", log_line)


if __name__ == "__main__":
    unittest.main()
