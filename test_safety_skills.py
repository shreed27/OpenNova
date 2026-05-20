import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from skills.file_ops import FileSkill
from skills.screenshot_ops import ScreenshotSkill
from skills.system_ops import SystemSkill


class SystemSkillSafetyTests(unittest.TestCase):
    def test_set_volume_rejects_out_of_range_values(self):
        result = json.loads(SystemSkill().set_volume(150, confirm=True))

        self.assertEqual(result["status"], "error")
        self.assertIn("0-100", result["message"])

    @patch("skills.system_ops.subprocess.run")
    def test_set_volume_uses_argument_list(self, run):
        run.return_value = Mock(returncode=0)

        result = json.loads(SystemSkill().set_volume(40, confirm=True))

        self.assertEqual(result["status"], "success")
        run.assert_called_once_with(
            ["osascript", "-e", "set volume output volume 40"],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("skills.system_ops.subprocess.run")
    def test_open_app_uses_argument_list(self, run):
        run.return_value = Mock(returncode=0)

        result = json.loads(SystemSkill().open_app("Safari", confirm=True))

        self.assertEqual(result["status"], "success")
        run.assert_called_once_with(["open", "-a", "Safari"], check=True, capture_output=True, text=True)

    def test_open_app_requires_confirmation_by_default(self):
        result = json.loads(SystemSkill().open_app("Safari"))

        self.assertEqual(result["status"], "confirmation_required")


class FileSkillSafetyTests(unittest.TestCase):
    def test_write_blocks_path_traversal(self):
        with tempfile.TemporaryDirectory() as desktop:
            skill = FileSkill(desktop_path=desktop)

            result = json.loads(skill.manage_file("write", "../escape.txt", "nope", confirm=True))

            self.assertEqual(result["status"], "error")
            self.assertIn("Desktop", result["message"])

    def test_read_missing_file_returns_structured_error(self):
        with tempfile.TemporaryDirectory() as desktop:
            skill = FileSkill(desktop_path=desktop)

            result = json.loads(skill.manage_file("read", "missing.txt"))

            self.assertEqual(result["status"], "error")
            self.assertIn("not found", result["message"].lower())

    def test_write_requires_confirmation_by_default(self):
        with tempfile.TemporaryDirectory() as desktop:
            skill = FileSkill(desktop_path=desktop)

            result = json.loads(skill.manage_file("write", "note.txt", "hello"))

            self.assertEqual(result["status"], "confirmation_required")


class ScreenshotSkillSafetyTests(unittest.TestCase):
    @patch("skills.screenshot_ops.subprocess.run")
    def test_screenshot_uses_subprocess_argument_list(self, run):
        with tempfile.TemporaryDirectory() as screenshots:
            expected = Path(screenshots) / "shot.png"
            expected_path = str(expected.resolve())
            run.return_value = Mock(returncode=0)
            expected.touch()
            skill = ScreenshotSkill(screenshot_dir=screenshots)

            result = json.loads(skill.take_screenshot("shot", confirm=True))

            self.assertEqual(result["status"], "success")
            run.assert_called_once_with(["screencapture", "-x", expected_path], check=True)

    def test_screenshot_blocks_path_traversal(self):
        with tempfile.TemporaryDirectory() as screenshots:
            skill = ScreenshotSkill(screenshot_dir=screenshots)

            result = json.loads(skill.take_screenshot("../shot", confirm=True))

            self.assertEqual(result["status"], "error")
            self.assertIn("screenshot directory", result["message"])


if __name__ == "__main__":
    unittest.main()
