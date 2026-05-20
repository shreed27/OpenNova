import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from skills.memory_ops import MemorySkill


class MemorySkillDurabilityTests(unittest.TestCase):
    def test_uses_configurable_memory_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "memory.json"
            with patch.dict(os.environ, {"JARVIS_MEMORY_FILE": str(path)}):
                skill = MemorySkill()

            self.assertEqual(skill.memory_file, str(path))
            self.assertTrue(path.exists())

    def test_recovers_from_corrupt_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "memory.json"
            path.write_text("{broken", encoding="utf-8")
            with patch.dict(os.environ, {"JARVIS_MEMORY_FILE": str(path)}):
                skill = MemorySkill()

            result = json.loads(skill.list_all_memories())

            self.assertEqual(result["status"], "success")
            self.assertEqual(result["memories"], {})

    def test_save_uses_atomic_replace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "memory.json"
            with patch.dict(os.environ, {"JARVIS_MEMORY_FILE": str(path)}):
                skill = MemorySkill()
                skill.remember_fact("name", "Nova")

            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["name"], "Nova")
            self.assertFalse(path.with_suffix(".json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
