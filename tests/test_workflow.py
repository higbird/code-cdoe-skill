"""Behavior tests use synthetic data in isolated directories; no external tools required."""
import contextlib
import copy
import csv
import shutil
import xml.etree.ElementTree as ET
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "analysis_workflow.py"
spec = importlib.util.spec_from_file_location("workflow", SCRIPT)
workflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="workflow-test-")
        self.root = Path(self.temporary.name).resolve()
        (self.root / "input").mkdir()
        (self.root / "input/data.tsv").write_text("id\tvalue\na\t1\nb\t2\n", encoding="utf-8")
        (self.root / "analysis.py").write_text(
            "import os,json,csv\n"
            "from pathlib import Path\n"
            "p=json.loads(os.environ['ANALYSIS_PARAMS'])\n"
            "rows=list(csv.DictReader(open('input/data.tsv'),delimiter='\\t'))\n"
            "value=sum(float(r['value']) for r in rows)*p.get('scale',1)\n"
            "Path(os.environ['ANALYSIS_OUTPUT_DIR'],'stats.tsv').write_text('value\\n'+str(value)+'\\n')\n",
            encoding="utf-8")
        (self.root / "plot.py").write_text(
            "import os,json\nfrom pathlib import Path\n"
            "p=json.loads(os.environ['ANALYSIS_PARAMS'])\n"
            "Path(os.environ['ANALYSIS_OUTPUT_DIR'],'plot.svg').write_text("
            "'<svg xmlns=\"http://www.w3.org/2000/svg\"><text>'+p['label']+"
            "Path('output/stats.tsv').read_text()+'</text></svg>')\n", encoding="utf-8")
        self.cfg = {"version": 1, "stages": [
            {"id": "analysis", "code": ["analysis.py"], "inputs": [
                {"path": "input/data.tsv", "columns": ["id", "value"], "unique": ["id"],
                 "numeric": {"value": {"min": 0}}, "min_rows": 1}],
             "params": {"scale": 1}, "versions": {"python": ["{python}", "--version"]},
             "command": ["{python}", "{root}/analysis.py"],
             "outputs": [{"path": "stats.tsv", "columns": ["value"],
                          "numeric": {"value": {"min": 0}}, "min_rows": 1}]},
            {"id": "plot", "depends": ["analysis"], "code": ["plot.py"],
             "inputs": [{"path": "output/stats.tsv", "columns": ["value"]}],
             "params": {"label": "Total"}, "command": ["{python}", "{root}/plot.py"],
             "outputs": [{"path": "plot.svg"}]}]}
        self.manifest = self.root / "workflow.json"
        self.save()

    def tearDown(self):
        self.temporary.cleanup()

    def save(self):
        self.manifest.write_text(json.dumps(self.cfg), encoding="utf-8")

    def call(self, action="run", *flags):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return workflow.main([action, str(self.manifest), *flags])

    def decisions(self):
        root, stages, order, ancestors = workflow.load_manifest(self.manifest)
        return workflow.plan(root, stages, order, {})

    def current(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in
                [self.root / "output/stats.tsv", self.root / "output/plot.svg",
                 self.root / "output/.analysis-state/receipts/analysis.json",
                 self.root / "output/.analysis-state/receipts/plot.json"] if p.exists()}

    def test_run_skip_and_receipt(self):
        self.assertEqual(self.call(), 0)
        self.assertEqual([x["action"] for x in self.decisions()], ["skip", "skip"])
        record = workflow.receipt(self.root, "analysis")
        self.assertEqual(record["exit_code"], 0)
        self.assertTrue(record["basis"]["files"]["input/data.tsv"]["sha256"])
        self.assertIn("Python", record["basis"]["versions"]["python"]["version"])
        self.assertIn("3.0", (self.root / "output/stats.tsv").read_text())
        before = self.current()
        self.assertEqual(self.call(), 0)
        self.assertEqual(before, self.current())
        self.assertFalse((self.root / "output/.analysis-state/lock.json").exists())

    def test_explicit_root_keeps_four_top_level_entries_and_plan_read_only(self):
        self.manifest.unlink()
        self.manifest = self.root / "input/workflow.json"
        (self.root / "analysis.py").rename(self.root / "code.txt")
        (self.root / "plot.py").rename(self.root / "input/plot.py")
        (self.root / "readme.md").write_text("Synthetic test project")
        for stage, source in zip(self.cfg["stages"], ("code.txt", "input/plot.py")):
            stage["code"] = [source]
            stage["command"] = ["{python}", "{root}/" + source]
        self.save()
        before = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*"))
        self.assertEqual(self.call("plan", "--root", str(self.root)), 0)
        self.assertEqual(before, sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*")))
        self.assertEqual(self.call("run", "--root", str(self.root)), 0)
        self.assertEqual({p.name for p in self.root.iterdir()}, {"input", "output", "code.txt", "readme.md"})
        self.assertTrue((self.root / "output/.analysis-state/receipts/analysis.json").is_file())
        self.assertFalse((self.root / "input/output").exists())
        root, stages, order, _ = workflow.load_manifest(self.manifest, self.root)
        self.assertEqual([x["action"] for x in workflow.plan(root, stages, order, {})], ["skip", "skip"])
        workflow.lock(self.root)
        self.manifest.write_text("broken manifest")
        self.assertEqual(self.call("recover", "--root", str(self.root), "--confirm-stopped"), 0)
        self.assertFalse((self.root / "output/.analysis-state/lock.json").exists())

    def test_manifest_parent_root_default_remains_compatible(self):
        self.assertEqual(workflow.load_manifest(self.manifest)[0], self.root)
        self.assertEqual(self.call(), 0)
        self.assertFalse((self.root / ".analysis-state").exists())
        self.assertTrue((self.root / "output/.analysis-state/receipts/analysis.json").exists())
        self.assertEqual(self.call("plan", "--root", str(self.root / "missing")), 1)

    def test_output_state_namespace_is_protected(self):
        for name in (".analysis-state", ".analysis-state/lock.json",
                     ".analysis-state/receipts/analysis.json", ".ANALYSIS-STATE/transactions/test"):
            with self.subTest(name=name):
                self.cfg["stages"][0]["outputs"] = [{"path": name}]
                self.save()
                self.assertEqual(self.call("plan"), 1)
                self.assertEqual(self.call("run"), 1)
                self.assertFalse((self.root / "output").exists())

    def test_legacy_state_blocks_default_actions_without_changes(self):
        legacy = self.root / ".analysis-state"
        legacy.mkdir()
        (legacy / "lock.json").write_text('{"pid": 123}')
        (legacy / "evidence.txt").write_text("retain")
        before = {p.relative_to(self.root).as_posix(): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        for action, flags in (("plan", ()), ("run", ()), ("recover", ("--confirm-stopped",))):
            with self.subTest(action=action):
                errors = io.StringIO()
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errors):
                    self.assertEqual(workflow.main([action, str(self.manifest), *flags]), 1)
                self.assertIn("Legacy .analysis-state exists", errors.getvalue())
        self.assertEqual(before, {p.relative_to(self.root).as_posix(): p.read_bytes()
                                 for p in self.root.rglob("*") if p.is_file()})
        self.assertFalse((self.root / "output").exists())
        self.assertEqual(self.call("recover", "--legacy-state"), 1)
        self.assertEqual(self.call("recover", "--legacy-state", "--confirm-stopped"), 0)
        self.assertFalse((legacy / "lock.json").exists())
        self.assertEqual((legacy / "evidence.txt").read_text(), "retain")
        self.assertEqual(self.call("plan"), 1)  # Recovery never silently migrates the old layout.

    def test_legacy_recovery_restores_old_output_and_receipt(self):
        self.manifest.unlink()
        self.manifest = self.root / "input/workflow.json"
        self.save()
        output = self.root / "output/stats.tsv"
        output.parent.mkdir()
        output.write_text("old output")
        record = self.root / ".analysis-state/receipts/analysis.json"
        record.parent.mkdir(parents=True)
        record.write_text("old receipt")
        transaction = self.root / ".analysis-state/transactions" / ("d" * 32)
        (transaction / "backup").mkdir(parents=True)
        entries = []
        for index, target in enumerate((output, record)):
            entries.append({"target": target.relative_to(self.root).as_posix(), "existed": True,
                            "original": workflow.snapshot(target)})
            os.replace(target, transaction / "backup" / str(index))
            target.write_text("partial publication")
        workflow.write_json(transaction / "journal.json", {"status": "prepared", "entries": entries})
        flags = ("--root", str(self.root), "--legacy-state", "--confirm-stopped")
        self.assertEqual(self.call("run", "--root", str(self.root)), 1)  # Also blocks when no old lock remains.
        self.assertEqual(self.call("recover", *flags), 0)
        self.assertEqual(output.read_text(), "old output")
        self.assertEqual(record.read_text(), "old receipt")
        self.assertTrue((transaction / "journal.json").exists())
        self.assertEqual(self.call("recover", *flags), 0)
        self.assertFalse((self.root / "output/.analysis-state").exists())

    def test_legacy_recovery_refuses_coexisting_state_layouts(self):
        old = self.root / ".analysis-state/lock.json"
        new = self.root / "output/.analysis-state/lock.json"
        for marker in (old, new):
            marker.parent.mkdir(parents=True)
            marker.write_text("retain lock")
        self.assertEqual(self.call("recover", "--legacy-state", "--confirm-stopped"), 1)
        self.assertEqual(self.call("recover", "--confirm-stopped"), 1)
        self.assertEqual(self.call("plan"), 1)
        for marker in (old, new):
            self.assertEqual(marker.read_text(), "retain lock")

    def test_recovery_journal_cannot_overwrite_internal_state(self):
        transaction = self.root / "output/.analysis-state/transactions" / ("e" * 32)
        transaction.mkdir(parents=True)
        marker = workflow.lock(self.root)
        for target in ("output/.analysis-state/lock.json", "output/.ANALYSIS-STATE/transactions/x"):
            with self.subTest(target=target):
                workflow.write_json(transaction / "journal.json", {"status": "prepared", "entries": [
                    {"target": target, "existed": False}]})
                self.assertEqual(self.call("recover", "--confirm-stopped"), 1)
                self.assertTrue(marker.exists())

    def test_plot_parameter_does_not_rerun_analysis(self):
        self.assertEqual(self.call(), 0)
        analysis = workflow.receipt(self.root, "analysis")["run_id"]
        self.cfg["stages"][1]["params"]["label"] = "Updated"
        self.save()
        self.assertEqual([x["action"] for x in self.decisions()], ["skip", "run"])
        self.assertEqual(self.call(), 0)
        self.assertEqual(workflow.receipt(self.root, "analysis")["run_id"], analysis)
        self.assertIn("Updated", (self.root / "output/plot.svg").read_text())

    def test_code_parameter_and_input_changes_propagate(self):
        self.assertEqual(self.call(), 0)
        for mutate in [
            lambda: (self.root / "input/data.tsv").write_text("id\tvalue\na\t4\n"),
            lambda: self.cfg["stages"][0]["params"].update(scale=2),
            lambda: (self.root / "analysis.py").write_text((self.root / "analysis.py").read_text() + "\n# changed\n")]:
            mutate()
            self.save()
            self.assertEqual([x["action"] for x in self.decisions()], ["run", "run"])
            self.assertEqual(self.call(), 0)

    def test_output_tampering_and_target_ancestors(self):
        self.assertEqual(self.call(), 0)
        (self.root / "output/plot.svg").write_text("tampered")
        self.assertEqual([x["action"] for x in self.decisions()], ["skip", "run"])
        self.assertEqual(self.call("run", "--target", "plot"), 0)
        (self.root / "output/stats.tsv").unlink()
        self.assertEqual([x["action"] for x in self.decisions()], ["run", "run"])
        self.assertEqual(self.call("run", "--target", "analysis"), 0)
        self.assertEqual([x["action"] for x in self.decisions()], ["skip", "run"])

    def test_process_failure_preserves_old_outputs_and_receipts(self):
        self.assertEqual(self.call(), 0)
        before = self.current()
        (self.root / "analysis.py").write_text(
            "import os\nfrom pathlib import Path\n"
            "Path(os.environ['ANALYSIS_OUTPUT_DIR'],'stats.tsv').write_text('value\\n99\\n')\n"
            "raise SystemExit(7)\n")
        self.assertEqual(self.call(), 1)
        self.assertEqual(before, self.current())
        self.assertTrue(list((self.root / "output/.analysis-state/transactions").glob("*/failure.json")))

    def test_missing_output_not_satisfied_by_old_file(self):
        self.assertEqual(self.call(), 0)
        before = self.current()
        (self.root / "analysis.py").write_text("pass\n")
        self.assertEqual(self.call(), 1)
        self.assertEqual(before, self.current())

    def test_bad_input_prevents_command(self):
        (self.root / "input/data.tsv").write_text("id\tvalue\na\t1\na\t2\n")
        self.assertEqual(self.call(), 1)
        self.assertFalse((self.root / "output/stats.tsv").exists())

    def test_contract_failure_preserves_old_outputs(self):
        self.assertEqual(self.call(), 0)
        before = self.current()
        self.cfg["stages"][0]["outputs"][0]["numeric"]["value"]["max"] = 1
        self.save()
        self.assertEqual(self.call(), 1)
        self.assertEqual(before, self.current())

    def test_input_mutated_during_run_rejected(self):
        (self.root / "analysis.py").write_text((self.root / "analysis.py").read_text() +
            "\nPath('input/data.tsv').write_text('id\\tvalue\\na\\t9\\n')\n")
        self.assertEqual(self.call(), 1)
        self.assertFalse((self.root / "output/stats.tsv").exists())

    def test_publication_error_rolls_back_all_files_and_receipt(self):
        self.assertEqual(self.call(), 0)
        before = self.current()
        self.cfg["stages"][0]["params"]["scale"] = 2
        self.save()
        original = os.replace
        fired = False
        def fail_once(source, destination):
            nonlocal fired
            if not fired and str(source).endswith("receipt.json"):
                fired = True
                raise OSError("simulated receipt replacement failure")
            return original(source, destination)
        with mock.patch.object(workflow.os, "replace", side_effect=fail_once):
            self.assertEqual(self.call(), 1)
        self.assertTrue(fired)
        self.assertEqual(before, self.current())

    def test_recover_interrupted_partial_publication_is_idempotent(self):
        output = self.root / "output"
        output.mkdir()
        (output / "stats.tsv").write_text("old")
        transaction = self.root / "output/.analysis-state/transactions" / ("a" * 32)
        (transaction / "backup").mkdir(parents=True)
        journal = {"status": "prepared", "entries": [
            {"target": "output/stats.tsv", "existed": True, "original": workflow.snapshot(output / "stats.tsv")},
            {"target": "output/new.tsv", "existed": False}]}
        workflow.write_json(transaction / "journal.json", journal)
        os.replace(output / "stats.tsv", transaction / "backup/0")
        (output / "stats.tsv").write_text("new")
        (output / "new.tsv").write_text("partly published")
        workflow.lock(self.root)
        self.assertEqual(self.call("run"), 1)
        self.assertEqual(self.call("recover"), 1)
        self.assertEqual(self.call("recover", "--confirm-stopped"), 0)
        self.assertEqual((output / "stats.tsv").read_text(), "old")
        self.assertFalse((output / "new.tsv").exists())
        self.assertEqual(self.call("recover", "--confirm-stopped"), 0)
        self.assertEqual((output / "stats.tsv").read_text(), "old")

    def test_read_only_plan_and_no_automatic_lock_breaking(self):
        before = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*"))
        self.assertEqual(self.call("plan"), 0)
        self.assertEqual(before, sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*")))
        workflow.lock(self.root)
        self.assertEqual(self.call(), 1)
        self.assertTrue((self.root / "output/.analysis-state/lock.json").exists())

    def test_invalid_graph_and_ownership_rejected(self):
        original = copy.deepcopy(self.cfg)
        for mutation in [
            lambda: self.cfg["stages"][0].update(depends=["plot"]),
            lambda: self.cfg["stages"][1].update(depends=[]),
            lambda: self.cfg["stages"][1].update(outputs=[{"path": "stats.tsv"}]),
            lambda: self.cfg["stages"][1].update(outputs=[{"path": "../input/data.tsv"}]),
            lambda: self.cfg["stages"][1].update(outputs=[{"path": "STATS.tsv"}]),
            lambda: self.cfg["stages"][1].update(unrecognized=True)]:
            self.cfg = copy.deepcopy(original)
            mutation()
            self.save()
            self.assertEqual(self.call("plan"), 1)

    def test_symlink_output_refused(self):
        external = self.root / "external"
        external.mkdir()
        try:
            (self.root / "output").symlink_to(external, target_is_directory=True)
        except OSError:
            self.skipTest("OS does not permit symlink creation")
        self.assertEqual(self.call(), 1)
        self.assertEqual(list(external.iterdir()), [])

    def test_header_only_numeric_nonfinite_and_composite_id(self):
        path = self.root / "input/empty.tsv"
        path.write_text("id\tgroup\tp\n")
        rule = {"path": "input/empty.tsv", "columns": ["id", "group", "p"],
                "unique": ["id", "group"], "numeric": {"p": {"min": 0, "max": 1}}}
        self.assertTrue(workflow.check_files(self.root, [rule])[0]["ok"])
        for data in ["a\tx\tNaN\n", "a\tx\tinf\n", "a\tx\t1.5\n", "a\tx\t0.2\na\tx\t0.4\n"]:
            path.write_text("id\tgroup\tp\n" + data)
            self.assertFalse(workflow.check_files(self.root, [rule])[0]["ok"])
        path.write_text("id\tgroup\tp\na\tx\t0.2\na\ty\t0.4\n")
        self.assertTrue(workflow.check_files(self.root, [rule])[0]["ok"])

    def test_missing_zero_byte_and_malformed_table(self):
        rule = {"path": "input/check.tsv"}
        self.assertFalse(workflow.check_files(self.root, [rule])[0]["ok"])
        (self.root / rule["path"]).touch()
        self.assertFalse(workflow.check_files(self.root, [rule])[0]["ok"])
        self.assertTrue(workflow.check_files(self.root, [{**rule, "allow_empty": True}])[0]["ok"])
        for data in ["id\tid\na\tb\n", "id\tvalue\na\t2\textra\n", "  \tvalue\na\t2\n"]:
            (self.root / rule["path"]).write_text(data)
            self.assertFalse(workflow.check_files(self.root, [rule])[0]["ok"])

    def test_standalone_check_cli(self):
        contract = self.root / "checks.json"
        contract.write_text(json.dumps({"files": self.cfg["stages"][0]["inputs"]}))
        result = subprocess.run([sys.executable, str(SCRIPT), "check", str(contract)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)[0]["rows"], 2)

    def test_success_preserves_unrelated_output(self):
        (self.root / "output").mkdir()
        (self.root / "output/user.txt").write_text("keep")
        self.assertEqual(self.call(), 0)
        self.assertEqual((self.root / "output/user.txt").read_text(), "keep")
        self.assertEqual(list((self.root / "output/.analysis-state/transactions").iterdir()), [])

    def test_force_propagates_even_if_output_content_unchanged(self):
        self.assertEqual(self.call(), 0)
        self.assertEqual(self.call("run", "--force", "--target", "analysis"), 0)
        self.assertEqual([x["action"] for x in self.decisions()], ["skip", "run"])



    def test_multi_file_rollback_removes_new_and_restores_existing(self):
        self.assertEqual(self.call(), 0)
        before = self.current()
        self.cfg["stages"][0]["outputs"].append({"path": "extra.txt"})
        self.save()
        (self.root / "analysis.py").write_text((self.root / "analysis.py").read_text() +
            "\nPath(os.environ['ANALYSIS_OUTPUT_DIR'],'extra.txt').write_text('new')\n")
        original = os.replace
        fired = False
        def fail_once(source, destination):
            nonlocal fired
            if not fired and str(source).endswith("receipt.json"):
                fired = True
                raise OSError("interrupted after multiple replacements")
            return original(source, destination)
        with mock.patch.object(workflow.os, "replace", side_effect=fail_once):
            self.assertEqual(self.call(), 1)
        self.assertEqual(before, self.current())
        self.assertFalse((self.root / "output/extra.txt").exists())

    def test_failed_rollback_keeps_lock_and_recovers_later(self):
        self.assertEqual(self.call(), 0)
        before = self.current()
        self.cfg["stages"][0]["params"]["scale"] = 5
        self.save()
        original = os.replace
        def fail_publication_and_restore(source, destination):
            if str(source).endswith("receipt.json") or "backup" in Path(source).parts:
                raise OSError("temporary filesystem failure")
            return original(source, destination)
        with mock.patch.object(workflow.os, "replace", side_effect=fail_publication_and_restore):
            self.assertEqual(self.call(), 1)
        self.assertTrue((self.root / "output/.analysis-state/lock.json").exists())
        self.manifest.write_text("broken manifest")
        self.assertEqual(self.call("recover", "--confirm-stopped"), 0)
        self.assertEqual(before, self.current())

    def test_timeout_keeps_lock_and_formal_output(self):
        self.assertEqual(self.call(), 0)
        before = self.current()
        (self.root / "analysis.py").write_text("import time\ntime.sleep(10)\n")
        self.cfg["stages"][0]["timeout"] = 0.1
        self.save()
        self.assertEqual(self.call(), 1)
        self.assertEqual(before, self.current())
        self.assertTrue((self.root / "output/.analysis-state/lock.json").exists())
        self.assertEqual(self.call("recover", "--confirm-stopped"), 0)

    def test_environment_probe_change_triggers_rerun(self):
        (self.root / "tool-version.txt").write_text("tool v1")
        self.cfg["stages"][0]["versions"]["tool"] = [
            "{python}", "-c", "from pathlib import Path;print(Path('tool-version.txt').read_text())"]
        self.save()
        self.assertEqual(self.call(), 0)
        (self.root / "tool-version.txt").write_text("tool v2")
        self.assertEqual([x["action"] for x in self.decisions()], ["run", "run"])

    def test_windows_junction_output_refused(self):
        if os.name != "nt":
            self.skipTest("Windows junction test")
        external = self.root / "junction-target"
        external.mkdir()
        link = self.root / "output"
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(external)],
                                capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        self.assertEqual(result.returncode, 0, result.stderr)
        try:
            self.assertEqual(self.call(), 1)
            self.assertEqual(list(external.iterdir()), [])
        finally:
            os.rmdir(link)  # Removes only this tested junction, never its target directory.

    def test_recovery_refuses_corrupt_backup(self):
        self.assertEqual(self.call(), 0)
        target = self.root / "output/stats.tsv"
        transaction = self.root / "output/.analysis-state/transactions" / ("b" * 32)
        (transaction / "backup").mkdir(parents=True)
        workflow.write_json(transaction / "journal.json", {"status": "prepared", "entries": [
            {"target": "output/stats.tsv", "existed": True, "original": workflow.snapshot(target)}]})
        os.replace(target, transaction / "backup/0")
        target.write_text("new")
        (transaction / "backup/0").write_text("corrupted")
        workflow.lock(self.root)
        self.assertEqual(self.call("recover", "--confirm-stopped"), 1)
        self.assertTrue((self.root / "output/.analysis-state/lock.json").exists())

    def test_repeat_recovery_after_interrupted_recovery(self):
        output = self.root / "output"
        output.mkdir()
        (output / "a.txt").write_text("old a")
        (output / "b.txt").write_text("old b")
        transaction = self.root / "output/.analysis-state/transactions" / ("c" * 32)
        (transaction / "backup").mkdir(parents=True)
        entries = [{"target": "output/" + name, "existed": True,
                    "original": workflow.snapshot(output / name)} for name in ("a.txt", "b.txt")]
        for index, name in enumerate(("a.txt", "b.txt")):
            os.replace(output / name, transaction / "backup" / str(index))
            (output / name).write_text("new")
        workflow.write_json(transaction / "journal.json", {"status": "prepared", "entries": entries})
        workflow.lock(self.root)
        original = os.replace
        def interrupt_second_restore(source, destination):
            if str(source).endswith(str(Path("backup") / "0")):
                raise OSError("interrupted recovery")
            return original(source, destination)
        with mock.patch.object(workflow.os, "replace", side_effect=interrupt_second_restore):
            self.assertEqual(self.call("recover", "--confirm-stopped"), 1)
        self.assertEqual(self.call("recover", "--confirm-stopped"), 0)
        self.assertEqual((output / "a.txt").read_text(), "old a")
        self.assertEqual((output / "b.txt").read_text(), "old b")



    def test_bundled_example_cli_from_other_directory_and_unicode_path(self):
        project = self.root / "Unicode Ω project"
        shutil.copytree(SCRIPT.parents[1] / "assets/minimal", project)
        def cli(*parameters):
            return subprocess.run([sys.executable, "-X", "utf8", "-B", str(project / "code.txt"), *parameters],
                                  cwd=self.root, capture_output=True, encoding="utf-8")
        first = cli()
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        with (project / "output/summary.tsv").open() as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual([float(row["mean"]) for row in rows], [3, 7])
        self.assertEqual([int(row["n"]) for row in rows], [2, 2])
        tree = ET.parse(project / "output/means.svg")
        labels = [node.text for node in tree.findall(".//{http://www.w3.org/2000/svg}text")]
        self.assertEqual(labels, ["Synthetic group means", "A", "3", "B", "7"])
        original = (project / "output/summary.tsv").read_bytes()
        self.assertEqual(cli("--title", "Unicode Ω title").returncode, 0)
        self.assertEqual((project / "output/summary.tsv").read_bytes(), original)
        self.assertIn("Unicode Ω title", (project / "output/means.svg").read_text(encoding="utf-8"))
        self.assertEqual({path.name for path in project.iterdir()},
                         {"input", "output", "code.txt", "readme.md"})
        self.assertEqual({path.name for path in (project / "input").iterdir()}, {"data.tsv"})
        self.assertEqual({path.name for path in (project / "output").iterdir()},
                         {"summary.tsv", "means.svg"})
        self.assertTrue(all(path.is_file() for path in (project / "output").iterdir()))



    def test_stat_does_not_read_data_and_reports_weak_evidence(self):
        path = self.root / "input/data.tsv"
        original = Path.open
        def guard(target, *args, **kwargs):
            if target == path:
                self.fail("stat mode read file content")
            return original(target, *args, **kwargs)
        with mock.patch.object(Path, "open", guard):
            result = workflow.file_fingerprint(self.root, {"path": "input/data.tsv", "fingerprint": "stat"}, {})
        self.assertEqual(result["mode"], "stat")
        self.assertFalse(result["content_verified"])
        self.assertIn("mtime_ns", result)
        self.assertNotIn("sha256", result)

    def test_stat_explicitly_cannot_detect_preserved_size_and_mtime(self):
        path = self.root / "input/data.tsv"
        rule = {"path": "input/data.tsv", "fingerprint": "stat"}
        old_stat = path.stat()
        old = workflow.file_fingerprint(self.root, rule, {})
        old_hash = workflow.snapshot(path)
        path.write_bytes(path.read_bytes().replace(b"a\t1", b"a\t9"))
        os.utime(path, ns=(old_stat.st_atime_ns, old_stat.st_mtime_ns))
        self.assertEqual(old, workflow.file_fingerprint(self.root, rule, {}))
        self.assertNotEqual(old_hash, workflow.snapshot(path))

    def test_external_reference_and_verification_are_distinct(self):
        path = self.root / "input/data.tsv"
        checksum = self.root / "input/data.sha256"
        checksum.write_text(workflow.snapshot(path)["sha256"] + "  data.tsv\n")
        rule = {"path": "input/data.tsv", "fingerprint": "external", "checksum": "input/data.sha256"}
        original = Path.open
        def guard(target, *args, **kwargs):
            if target == path:
                self.fail("external reference mode read data content")
            return original(target, *args, **kwargs)
        with mock.patch.object(Path, "open", guard):
            result = workflow.file_fingerprint(self.root, rule, {})
        self.assertFalse(result["content_verified"])
        self.assertTrue(workflow.file_fingerprint(self.root, {**rule, "verify_checksum": True}, {})["content_verified"])
        path.write_text("id\tvalue\na\t9\n")
        with self.assertRaises(workflow.WorkflowError):
            workflow.file_fingerprint(self.root, {**rule, "verify_checksum": True}, {})
        self.assertFalse(workflow.file_fingerprint(self.root, rule, {})["content_verified"])

    def test_external_md5_and_wrong_or_ambiguous_sidecars(self):
        import hashlib
        path = self.root / "input/data.tsv"
        checksum = self.root / "input/data.md5"
        rule = {"path": "input/data.tsv", "fingerprint": "external",
                "checksum": "input/data.md5", "verify_checksum": True}
        checksum.write_text(hashlib.md5(path.read_bytes()).hexdigest() + " *data.tsv\n")
        self.assertTrue(workflow.file_fingerprint(self.root, rule, {})["content_verified"])
        for content in ["0" * 32 + "  wrong.tsv\n", "0" * 32 + "\n",
                        "0" * 32 + "  data.tsv\n" + "1" * 32 + "  data.tsv\n"]:
            checksum.write_text(content)
            with self.assertRaises(workflow.WorkflowError):
                workflow.file_fingerprint(self.root, rule, {})

    def test_exists_and_header_do_not_scan_rows(self):
        path = self.root / "input/data.tsv"
        path.write_text("id\tvalue\na\tbad\textra\n")
        original = Path.open
        def no_content(target, *args, **kwargs):
            if target == path:
                self.fail("exists read content")
            return original(target, *args, **kwargs)
        with mock.patch.object(Path, "open", no_content):
            exists = workflow.check_files(self.root, [{"path": "input/data.tsv", "validation": "exists"}])[0]
        self.assertTrue(exists["ok"])
        self.assertIsNone(exists["rows"])
        real_reader = csv.reader
        def header_only_reader(*args, **kwargs):
            reader = real_reader(*args, **kwargs)
            yield next(reader)
            self.fail("header mode requested a data record")
        with mock.patch.object(workflow.csv, "reader", header_only_reader):
            header = workflow.check_files(self.root, [{"path": "input/data.tsv", "validation": "header",
                                                       "columns": ["id", "value"]}])[0]
        self.assertTrue(header["ok"])
        self.assertIsNone(header["rows"])
        self.assertIn("numeric", header["not_performed"])
        self.assertFalse(workflow.check_files(self.root, [{"path": "input/data.tsv"}])[0]["ok"])

    def test_lower_validation_rejects_unfulfilled_constraints(self):
        for rule in [
            {"validation": "exists", "columns": ["id"]},
            {"validation": "header", "unique": ["id"]},
            {"validation": "header", "numeric": {"value": {}}},
            {"validation": "header", "min_rows": 0},
            {"validation": "exists", "max_rows": 10},
            {"validation": "bogus"},
            {"fingerprint": "bogus"},
            {"fingerprint": "stat", "verify_checksum": True}]:
            with self.assertRaises(workflow.WorkflowError):
                workflow.validate_rule({"path": "input/data.tsv", **rule})

    def test_receipt_v2_migration_keeps_old_output_until_success(self):
        self.assertEqual(self.call(), 0)
        path = workflow.receipt_path(self.root, "analysis")
        record = workflow.read_json(path)
        self.assertEqual(record["version"], 2)
        self.assertEqual(record["input_checks"][0]["validation"], "full")
        record["version"] = 1
        workflow.write_json(path, record)
        self.assertEqual([x["action"] for x in self.decisions()], ["run", "run"])
        before = self.current()
        (self.root / "analysis.py").write_text("raise SystemExit(2)\n")
        self.assertEqual(self.call(), 1)
        self.assertEqual(before, self.current())

    def test_phase_cache_reduces_reads_but_never_crosses_execution(self):
        original = workflow.snapshot
        source = self.root / "input/data.tsv"
        counts = {}
        def counted(path):
            name = str(path.resolve())
            counts[name] = counts.get(name, 0) + 1
            return original(path)
        with mock.patch.object(workflow, "snapshot", side_effect=counted):
            self.assertEqual(self.call(), 0)
        self.assertEqual(counts[str(source)], 2)  # Before and after, not 3 preplan/before/after.
        counts.clear()
        with mock.patch.object(workflow, "snapshot", side_effect=counted):
            self.assertEqual(self.call("plan"), 0)
        self.assertEqual(counts[str(self.root / "output/stats.tsv")], 1)

    def test_phase_cache_invalidates_on_file_change(self):
        path = self.root / "input/data.tsv"
        cache = {}
        old = workflow.phase_snapshot(path, cache)
        path.write_text("changed-size\n")
        self.assertNotEqual(old, workflow.phase_snapshot(path, cache))

    def test_weak_output_mode_does_not_weaken_backup_integrity(self):
        self.cfg["stages"][0]["outputs"][0]["fingerprint"] = "stat"
        self.save()
        self.assertEqual(self.call(), 0)
        self.assertEqual([x["action"] for x in self.decisions()], ["skip", "skip"])
        self.assertFalse(workflow.receipt(self.root, "analysis")["outputs"]["stats.tsv"]["content_verified"])
        before = self.current()
        self.cfg["stages"][0]["params"]["scale"] = 3
        self.save()
        original = os.replace
        def failure(source, destination):
            if str(source).endswith("receipt.json"):
                raise OSError("publication failed")
            return original(source, destination)
        with mock.patch.object(workflow.os, "replace", side_effect=failure):
            self.assertEqual(self.call(), 1)
        self.assertEqual(before, self.current())
        journals = list((self.root / "output/.analysis-state/transactions").glob("*/journal.json"))
        self.assertTrue(journals)
        original_record = workflow.read_json(journals[0])["entries"][0]["original"]
        self.assertIn("sha256", original_record)
        self.assertNotIn("mtime_ns", original_record)

    def test_external_outputs_publish_with_sidecar_and_skip(self):
        (self.root / "analysis.py").write_text((self.root / "analysis.py").read_text() +
            "\nimport hashlib\n"
            "out=Path(os.environ['ANALYSIS_OUTPUT_DIR'])\n"
            "(out/'stats.sha256').write_text(hashlib.sha256((out/'stats.tsv').read_bytes()).hexdigest()+'  stats.tsv\\n')\n")
        self.cfg["stages"][0]["outputs"][0].update(
            fingerprint="external", checksum="stats.sha256", verify_checksum=True)
        self.cfg["stages"][0]["outputs"].append({"path": "stats.sha256"})
        self.save()
        self.assertEqual(self.call(), 0)
        self.assertEqual([x["action"] for x in self.decisions()], ["skip", "skip"])
        self.assertTrue(workflow.receipt(self.root, "analysis")["outputs"]["stats.tsv"]["content_verified"])

    def test_external_checksum_dependency_and_code_strength_enforced(self):
        original = copy.deepcopy(self.cfg)
        self.cfg["stages"][0]["inputs"][0].update(fingerprint="external", checksum="output/plot.svg")
        self.save()
        self.assertEqual(self.call("plan"), 1)
        self.cfg = copy.deepcopy(original)
        self.cfg["stages"][0]["inputs"].append({"path": "analysis.py", "fingerprint": "stat"})
        self.save()
        self.assertEqual(self.call("plan"), 1)
        self.cfg = copy.deepcopy(original)
        self.cfg["stages"][0]["outputs"][0].update(fingerprint="external", checksum="missing.sha256")
        self.save()
        self.assertEqual(self.call("plan"), 1)

    def test_validation_change_invalidates_receipt_and_records_limits(self):
        self.cfg["stages"][0]["inputs"] = [{"path": "input/data.tsv", "validation": "header",
                                          "columns": ["id", "value"], "fingerprint": "stat"}]
        self.save()
        self.assertEqual(self.call(), 0)
        record = workflow.receipt(self.root, "analysis")
        self.assertIsNone(record["input_checks"][0]["rows"])
        self.assertIn("row_count", record["input_checks"][0]["not_performed"])
        self.assertFalse(record["basis"]["files"]["input/data.tsv"]["content_verified"])
        self.assertIn("input/data.tsv", self.decisions()[0]["weaker_fingerprints"])
        self.cfg["stages"][0]["inputs"][0]["validation"] = "full"
        self.save()
        self.assertEqual([x["action"] for x in self.decisions()], ["run", "run"])

    def test_zero_rows_distinguished_from_unknown_or_partial_rows(self):
        path = self.root / "input/data.tsv"
        path.write_text("id\tvalue\n")
        record = workflow.check_files(self.root, [{"path": "input/data.tsv"}])[0]
        self.assertEqual(record["rows"], 0)
        self.assertIn("row_count", record["completed_checks"])
        path.write_text('id\tvalue\na\t1\nb\t"unterminated\n')
        record = workflow.check_files(self.root, [{"path": "input/data.tsv"}])[0]
        self.assertFalse(record["ok"])
        self.assertIsNone(record["rows"])
        self.assertEqual(record["rows_scanned"], 1)

    def test_simulated_hundred_gb_metadata_mode_is_constant_io(self):
        target = self.root / "input/data.tsv"
        identity = workflow.file_identity(target)
        simulated = (*identity[:2], 100 * 1024**3, *identity[3:])
        with mock.patch.object(workflow, "file_identity", return_value=simulated),              mock.patch.object(Path, "open", side_effect=AssertionError("Unexpected data read")):
            record = workflow.file_fingerprint(self.root, {"path": "input/data.tsv", "fingerprint": "stat"}, {})
        self.assertEqual(record["size"], 100 * 1024**3)



    def test_invalid_external_output_is_regenerated(self):
        script = self.root / "analysis.py"
        script.write_text(script.read_text() +
            "\nimport hashlib\nout=Path(os.environ['ANALYSIS_OUTPUT_DIR'])\n"
            "(out/'stats.sha256').write_text(hashlib.sha256((out/'stats.tsv').read_bytes()).hexdigest()+'  stats.tsv\\n')\n")
        self.cfg["stages"][0]["outputs"][0].update(
            fingerprint="external", checksum="stats.sha256", verify_checksum=True)
        self.cfg["stages"][0]["outputs"].append({"path": "stats.sha256"})
        self.save()
        self.assertEqual(self.call(), 0)
        (self.root / "output/stats.tsv").write_text("value\n999\n")
        self.assertEqual([x["action"] for x in self.decisions()], ["run", "run"])
        self.assertEqual(self.call(), 0)
        self.assertIn("3.0", (self.root / "output/stats.tsv").read_text())

    def test_standalone_check_explicit_fingerprint_and_checksum(self):
        contract = self.root / "checks.json"
        workflow.write_json(contract, {"files": [
            {"path": "input/data.tsv", "fingerprint": "stat", "validation": "exists"}]})
        command = [sys.executable, "-B", str(SCRIPT), "check", str(contract)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)[0]
        self.assertIsNone(record["rows"])
        self.assertFalse(record["fingerprint"]["content_verified"])
        (self.root / "input/data.sha256").write_text("0" * 64 + "  data.tsv\n")
        workflow.write_json(contract, {"files": [
            {"path": "input/data.tsv", "fingerprint": "external", "validation": "exists",
             "checksum": "input/data.sha256", "verify_checksum": True}]})
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Checksum mismatch", result.stderr)

    def test_changed_checksum_reference_marks_stage_stale(self):
        path = self.root / "input/data.tsv"
        sidecar = self.root / "input/data.sha256"
        sidecar.write_text(workflow.snapshot(path)["sha256"] + "  data.tsv\n")
        self.cfg["stages"][0]["inputs"][0].update(
            fingerprint="external", checksum="input/data.sha256")
        self.save()
        self.assertEqual(self.call(), 0)
        sidecar.write_text("0" * 64 + "  data.tsv\n")
        self.assertEqual([x["action"] for x in self.decisions()], ["run", "run"])


if __name__ == "__main__":
    unittest.main()
