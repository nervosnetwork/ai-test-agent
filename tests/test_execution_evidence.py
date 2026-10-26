from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/run_with_evidence.py"
INIT = ROOT / "scripts/init_repo_tests.py"


class ExecutionEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.product = self.root / "product"
        self.product.mkdir()
        self.tracked = self.product / "policy.txt"
        self.tracked.write_text("approved\n")
        for args in (["init", "-q"], ["add", "policy.txt"],
                     ["-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                      "commit", "-qm", "fixture"]):
            subprocess.run(["git", "-C", str(self.product), *args], check=True, capture_output=True)
        self.test_input = self.root / "test-input.txt"
        self.test_input.write_text("fixture and expected values\n")

    def invoke(self, code, *options, scope="focused", runner=RUNNER, env=None):
        return subprocess.run(
            [sys.executable, str(runner), "--root", str(self.root), "--product", "product",
             "--scope", scope, "--input", "test-input.txt", *options,
             "--", sys.executable, "-c", code, "{junit}"],
            text=True, capture_output=True, env={**os.environ, **(env or {})},
        )

    def receipt(self, scope="focused"):
        return json.loads((self.root / f"reports/{scope}/execution.json").read_text())

    def reported(self, xml, *options, **kwargs):
        # Controlled native-report fixture tests transport/parsing, not semantic coverage.
        code = "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text(" + repr(xml) + "); print('native output')"
        return self.invoke(code, "--junit", *options, **kwargs)

    def test_native_junit_counts_and_reproducible_inputs(self):
        xml = ('<testsuites><testsuite tests="3" failures="0" errors="0" skipped="1">'
               '<testcase classname="Payments" name="limit[1]"/>'
               '<testcase classname="Payments" name="limit[2]"/>'
               '<testcase classname="Payments" name="extension"><skipped/></testcase>'
               '</testsuite></testsuites>')
        result = self.reported(xml)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = self.receipt()
        self.assertEqual(record["outcomes"]["reported"], 3)
        self.assertEqual(record["outcomes"]["passed"], 2)
        self.assertEqual(record["outcomes"]["skipped"], 1)
        self.assertEqual(record["outcomes"]["ambiguous_selectors"], [])
        head = subprocess.check_output(["git", "-C", str(self.product), "rev-parse", "HEAD"], text=True).strip()
        self.assertEqual(record["product"]["head"], head)
        self.assertEqual(record["test_inputs"]["test-input.txt"], hashlib.sha256(self.test_input.read_bytes()).hexdigest())
        self.assertTrue(record["inputs_unchanged"])
        self.assertFalse(record["independent_review"])
        self.assertEqual(record["behavior_verification"], "not_checked")
        folder = self.root / "reports/focused"
        self.assertEqual(record["output_sha256"], hashlib.sha256((folder / "execution.log").read_bytes()).hexdigest())
        self.assertEqual(record["native_report_sha256"], hashlib.sha256((folder / "native-results.xml").read_bytes()).hexdigest())
        self.assertEqual(record["command"][-1], str(folder / "native-results.xml"))

    def test_real_unittest_exit_zero_does_not_fabricate_test_counts(self):
        code = ("import unittest; "
                "suite=unittest.TestSuite([unittest.FunctionTestCase(lambda: None)]); "
                "result=unittest.TextTestRunner().run(suite); raise SystemExit(not result.wasSuccessful())")
        result = self.invoke(code)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = self.receipt()
        self.assertIsNone(record["outcomes"])
        self.assertEqual(record["level"], "suite")
        self.assertEqual(record["status"], "completed")
        self.assertIn("Ran 1 test", (self.root / "reports/focused/execution.log").read_text())

    def test_missing_report_cannot_reuse_previous_success(self):
        first = self.reported('<testsuite><testcase name="ok"/></testsuite>')
        self.assertEqual(first.returncode, 0, first.stderr)
        second = self.invoke("print('no native report this time')", "--junit")
        self.assertNotEqual(second.returncode, 0)
        record = self.receipt()
        self.assertEqual(record["exit_code"], 0)
        self.assertEqual(record["status"], "blocked")
        self.assertIsNone(record["outcomes"])

    def test_reported_failure_cannot_be_hidden_by_successful_process(self):
        for child in ("failure", "error"):
            with self.subTest(child=child):
                result = self.reported(f'<testsuite><testcase name="bad"><{child}/></testcase></testsuite>')
                self.assertNotEqual(result.returncode, 0)
                record = self.receipt()
                self.assertEqual(record["exit_code"], 0)
                self.assertEqual(record["outcomes"]["failed" if child == "failure" else "errors"], 1)

    def test_empty_skipped_malformed_or_inconsistent_reports_fail_closed(self):
        reports = ["<testsuite/>", '<testsuite><testcase name="skip"><skipped/></testcase></testsuite>',
                   "<broken", '<testsuite failures="1"><testcase name="apparently_ok"/></testsuite>',
                   '<testsuite tests="not-a-number"><testcase name="ok"/></testsuite>']
        for xml in reports:
            with self.subTest(xml=xml):
                result = self.reported(xml)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.receipt()["status"], "blocked")

    def test_duplicate_native_selectors_are_visible_without_case_credit(self):
        result = self.reported('<testsuite><testcase classname="A" name="x"/><testcase classname="A" name="x"/></testsuite>')
        self.assertEqual(result.returncode, 0, result.stderr)
        record = self.receipt()
        self.assertEqual(record["outcomes"]["ambiguous_selectors"], [["A", "x"]])
        self.assertEqual(record["behavior_verification"], "not_checked")

    def test_native_nonzero_exit_is_preserved(self):
        result = self.invoke("print('failure detail'); raise SystemExit(3)")
        self.assertEqual(result.returncode, 3)
        self.assertEqual(self.receipt()["exit_code"], 3)
        self.assertEqual(self.receipt()["status"], "failed")

    def test_source_or_declared_input_changes_invalidate_receipt(self):
        for name in ("product/policy.txt", "test-input.txt"):
            with self.subTest(name=name):
                code = f"from pathlib import Path; Path({name!r}).write_text('changed')"
                result = self.invoke(code)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.receipt()["exit_code"], 0)
                self.assertFalse(self.receipt()["inputs_unchanged"])
                self.assertIn("changed during execution", " ".join(self.receipt()["errors"]))

    def test_timeout_retains_output_and_blocks_evidence(self):
        result = self.invoke("import time; print('started', flush=True); time.sleep(10)", "--timeout", "0.2")
        self.assertNotEqual(result.returncode, 0)
        self.assertIsNone(self.receipt()["exit_code"])
        self.assertEqual(self.receipt()["status"], "blocked")
        self.assertTrue((self.root / "reports/focused/execution.log").is_file())

    def test_environment_does_not_forward_model_credentials(self):
        result = self.invoke("import os; assert 'OPENAI_API_KEY' not in os.environ; print('isolated')",
                             env={"OPENAI_API_KEY": "fixture-secret-never-forward"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("OPENAI_API_KEY", self.receipt()["environment"]["keys"])
        self.assertNotIn("fixture-secret-never-forward", json.dumps(self.receipt()))

    def test_active_full_workflow_cannot_be_overwritten(self):
        state = self.root / ".ai-test-agent/current/focused/state.json"
        state.parent.mkdir(parents=True)
        state.write_text('{"stage":"DESIGN_REVIEWED"}')
        result = self.invoke("from pathlib import Path; Path('should-not-run').touch()")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("active PR-v2 scope", result.stderr)
        self.assertFalse((self.root / "should-not-run").exists())
        self.assertFalse((self.root / "reports/focused/execution.json").exists())

    def test_generated_security_project_has_working_self_contained_runtime(self):
        generated = self.root / "security-tests"
        result = subprocess.run([sys.executable, str(INIT), "--project", "Demo", "--source-repo", str(self.product),
                                 "--suites", "security-review", "--output", str(generated)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((generated / "suites/security-review/tests").is_dir())
        for name in ("workflow", "verification-quality", "security-review", "execution-evidence"):
            self.assertEqual((generated / f"docs/ai-test-agent/{name}.md").read_bytes(),
                             (ROOT / f"references/{name}.md").read_bytes())
        run = subprocess.run([sys.executable, str(generated / "scripts/run_with_evidence.py"),
                              "--root", str(generated), "--product", str(self.product), "--scope", "smoke",
                              "--", sys.executable, "-c", "print('native smoke')"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIsNone(json.loads((generated / "reports/smoke/execution.json").read_text())["outcomes"])


if __name__ == "__main__":
    unittest.main()
