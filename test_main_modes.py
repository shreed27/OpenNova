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
            patch.object(main, "run_gui_app") as run_gui_app:
            main.run_app(argparse.Namespace(text=False))

        registry.load_skills.assert_called_once()
        thread.start.assert_called_once()
        run_gui_app.assert_called_once()

    def test_text_mode_runs_without_gui(self):
        registry = Mock()
        thread = Mock()

        with patch.object(main, "SkillRegistry", return_value=registry), \
            patch.object(main.threading, "Thread", return_value=thread), \
            patch.object(main, "run_gui_app") as run_gui_app, \
            patch.object(main, "run_text_loop") as run_text_loop:
            main.run_app(argparse.Namespace(text=True))

        registry.load_skills.assert_called_once()
        thread.start.assert_called_once()
        run_gui_app.assert_not_called()
        run_text_loop.assert_called_once()

    def test_text_loop_queues_commands_until_quit(self):
        command_queue = queue.Queue()

        with patch("builtins.input", side_effect=["hello", "quit"]):
            main.run_text_loop({"command_queue": command_queue})

        first = command_queue.get_nowait()
        second = command_queue.get_nowait()
        self.assertEqual(first, "hello")
        self.assertEqual(second, "quit")


if __name__ == "__main__":
    unittest.main()
