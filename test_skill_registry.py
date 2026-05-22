import os
import tempfile
import textwrap
import unittest

from core.registry import SkillRegistry


class SkillRegistryTests(unittest.TestCase):
    def test_load_skills_skips_modules_that_fail_to_import(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            broken_skill = textwrap.dedent(
                '''
                raise ImportError("missing optional dependency")
                '''
            )
            working_skill = textwrap.dedent(
                '''
                from core.skill import Skill

                class WorkingSkill(Skill):
                    @property
                    def name(self):
                        return "working"

                    def get_tools(self):
                        return []

                    def get_functions(self):
                        return {}
                '''
            )

            with open(os.path.join(tmpdir, "broken.py"), "w", encoding="utf-8") as handle:
                handle.write(broken_skill)
            with open(os.path.join(tmpdir, "working.py"), "w", encoding="utf-8") as handle:
                handle.write(working_skill)

            registry = SkillRegistry()
            registry.load_skills(tmpdir)

            self.assertIn("working", registry.skills)


if __name__ == "__main__":
    unittest.main()
