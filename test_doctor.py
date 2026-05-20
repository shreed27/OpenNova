import argparse
import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from core.doctor import OPTIONAL_GROUPS, SKILL_OPTIONAL_GROUPS, run_doctor


class DoctorTests(unittest.TestCase):
    def test_optional_groups_explain_skipped_skills(self):
        self.assertEqual(SKILL_OPTIONAL_GROUPS["whatsapp_skill"], "whatsapp")
        self.assertEqual(SKILL_OPTIONAL_GROUPS["detection_skill"], "detection")

    @patch.dict(os.environ, {"GROQ_API_KEY": "key"}, clear=True)
    @patch("core.doctor.importlib.util.find_spec", return_value=None)
    def test_doctor_returns_structured_status(self, _find_spec):
        report = run_doctor()

        self.assertEqual(report["python"]["major"], sys.version_info.major)
        self.assertEqual(report["env"]["GROQ_API_KEY"], "set")
        self.assertEqual(report["env"]["JARVIS_BRAIN"], "missing")
        self.assertIn("gui", report["optional_groups"])

    @patch("main.run_doctor")
    def test_main_doctor_mode_prints_report(self, run_doctor_mock):
        import main

        run_doctor_mock.return_value = {"ok": True}
        with patch("main.print") as print_mock:
            main.run_app(argparse.Namespace(text=False, doctor=True))

        print_mock.assert_called()


if __name__ == "__main__":
    unittest.main()
