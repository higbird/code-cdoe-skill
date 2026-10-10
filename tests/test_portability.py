"""Run the copied four-piece example independently of its installed Skill."""
import csv
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

SOURCE = Path(__file__).resolve().parents[1]


class PortabilityTests(unittest.TestCase):
    def exercise_layout(self, host, omit_metadata=False, remove_skill=False):
        with tempfile.TemporaryDirectory(prefix="skill-portability-") as temporary:
            base = Path(temporary).resolve()
            skill = base / "user Ω home" / host / "skills" / SOURCE.name
            shutil.copytree(SOURCE, skill, ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", ".git", ".analysis-state"))
            if omit_metadata:
                (skill / "agents/openai.yaml").unlink()
            original = {p.relative_to(skill): p.read_bytes()
                        for p in skill.rglob("*") if p.is_file()}
            project = base / "research Ω project"
            shutil.copytree(skill / "assets/minimal", project)
            caller = base / "unrelated cwd"
            caller.mkdir()
            environment = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
            environment.pop("CODE_CDOE_SKILL_ROOT", None)
            if remove_skill:
                shutil.rmtree(skill)
            before_input = (project / "input/data.tsv").read_bytes()

            def assert_module_root():
                self.assertEqual({path.name for path in project.iterdir()},
                                 {"input", "output", "code.txt", "readme.md"})
                self.assertEqual({path.name for path in (project / "input").iterdir()},
                                 {"data.tsv"})
                self.assertEqual({path.name for path in (project / "output").iterdir()},
                                 {"summary.tsv", "means.svg"})
                self.assertTrue(all(path.is_file() for path in (project / "output").iterdir()))

            def invoke(*extra):
                command = [sys.executable, "-B", str(project / "code.txt"), *extra]
                result = subprocess.run(
                    command, cwd=caller, env=environment,
                    capture_output=True, text=True, encoding="utf-8", timeout=60)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                assert_module_root()
                return result.stdout

            self.assertEqual({path.name for path in project.iterdir()},
                             {"input", "code.txt", "readme.md"})
            invoke()  # The script creates output/; no empty-directory placeholder is needed.
            with (project / "output/summary.tsv").open(encoding="utf-8", newline="") as table:
                rows = list(csv.DictReader(table, delimiter="\t"))
            self.assertEqual([(r["group"], int(r["n"]), float(r["mean"])) for r in rows],
                             [("A", 2, 3.0), ("B", 2, 7.0)])
            tree = ET.parse(project / "output/means.svg")
            labels = [node.text for node in tree.findall(".//{http://www.w3.org/2000/svg}text")]
            self.assertEqual(labels, ["Synthetic group means", "A", "3", "B", "7"])
            before_output = {p.name: p.read_bytes() for p in (project / "output").iterdir()}
            invoke()
            self.assertEqual(before_output,
                             {p.name: p.read_bytes() for p in (project / "output").iterdir()})
            invoke("--scale", "2", "--title", "Relocated Ω <plot> & results", "--color", "#6a4c93")
            with (project / "output/summary.tsv").open(encoding="utf-8", newline="") as table:
                rows = list(csv.DictReader(table, delimiter="\t"))
            self.assertEqual([(r["group"], int(r["n"]), float(r["mean"])) for r in rows],
                             [("A", 2, 6.0), ("B", 2, 14.0)])
            tree = ET.parse(project / "output/means.svg")
            labels = [node.text for node in tree.findall(".//{http://www.w3.org/2000/svg}text")]
            self.assertEqual(labels, ["Relocated Ω <plot> & results", "A", "6", "B", "14"])
            bars = tree.findall("{http://www.w3.org/2000/svg}rect")[1:]
            self.assertEqual([bar.get("fill") for bar in bars], ["#6a4c93", "#6a4c93"])
            self.assertEqual((project / "input/data.tsv").read_bytes(), before_input)
            if not remove_skill:
                self.assertEqual(original, {p.relative_to(skill): p.read_bytes()
                                            for p in skill.rglob("*") if p.is_file()})
            self.assertEqual(list(caller.iterdir()), [])

    def test_claude_layout(self):
        self.exercise_layout(".claude")

    def test_codex_layout(self):
        self.exercise_layout(".agents")

    def test_hermes_layout(self):
        self.exercise_layout(".hermes")

    def test_no_codex_metadata_dependency(self):
        self.exercise_layout(".hermes", omit_metadata=True)

    def test_copied_example_needs_no_skill_directory(self):
        self.exercise_layout(".agents", remove_skill=True)

    def test_invalid_input_preserves_existing_results(self):
        with tempfile.TemporaryDirectory(prefix="example-input-") as temporary:
            project = Path(temporary) / "analysis project"
            shutil.copytree(SOURCE / "assets/minimal", project)
            command = [sys.executable, "-B", str(project / "code.txt")]
            first = subprocess.run(command, capture_output=True, timeout=60)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = {p.name: p.read_bytes() for p in (project / "output").iterdir()}
            (project / "input/data.tsv").write_text(
                "id\tgroup\tvalue\ns1\tA\t2\ns1\tB\t4\n", encoding="utf-8")
            invalid = subprocess.run(command, capture_output=True, timeout=60)
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn(b"id must be unique", invalid.stderr)
            self.assertEqual(before, {p.name: p.read_bytes() for p in (project / "output").iterdir()})


if __name__ == "__main__":
    unittest.main()
