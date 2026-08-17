from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "scripts" / "init_repo_tests.py"
CHECKER = ROOT / "scripts" / "check_test_map.py"


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd or ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


class ProjectGeneratorTests(unittest.TestCase):
    def test_single_suite_uses_flat_review_and_test_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "demo-tests"
            first = run(
                str(INIT),
                "--project",
                "Demo",
                "--source-repo",
                "../demo",
                "--suites",
                "api",
                "--output",
                str(output),
            )
            self.assertEqual(first.returncode, 0, first.stdout)
            self.assertIn("layout: single-suite", first.stdout)
            for relative in [
                "AGENTS.md",
                "README.md",
                "reviews/README.md",
                "tests/README.md",
                "fixtures/README.md",
                "scripts/check_test_map.py",
                "templates/test-review.md",
            ]:
                self.assertTrue((output / relative).is_file(), relative)
            self.assertFalse((output / "suites").exists())
            self.assertNotIn("MOD -> FUNC -> COV -> TP", (output / "README.md").read_text())

            with (output / "README.md").open("a", encoding="utf-8") as handle:
                handle.write("\nsentinel\n")
            second = run(
                str(INIT),
                "--project",
                "Demo",
                "--source-repo",
                "../demo",
                "--suites",
                "api",
                "--output",
                str(output),
            )
            self.assertEqual(second.returncode, 0, second.stdout)
            self.assertIn("sentinel", (output / "README.md").read_text())
            self.assertIn("created: 0", second.stdout)

    def test_multiple_suites_are_isolated_only_when_needed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "demo-tests"
            result = run(
                str(INIT),
                "--project",
                "Demo",
                "--source-repo",
                "../demo",
                "--suites",
                "integration",
                "performance",
                "--output",
                str(output),
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("layout: multi-suite", result.stdout)
            for relative in [
                "suites/integration/reviews/README.md",
                "suites/integration/tests/README.md",
                "suites/integration/config/README.md",
                "suites/performance/reviews/README.md",
                "suites/performance/benchmarks/README.md",
                "suites/performance/workloads/README.md",
            ]:
                self.assertTrue((output / relative).is_file(), relative)
            self.assertFalse((output / "tests").exists())

    def test_source_repository_is_required(self) -> None:
        result = run(
            str(INIT),
            "--project",
            "Demo",
            "--suites",
            "api",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--source-repo", result.stdout)


class MappingCheckerTests(unittest.TestCase):
    def write_project(self, root: Path) -> None:
        review = root / "reviews" / "rpc" / "submit_transaction.md"
        review.parent.mkdir(parents=True)
        review.write_text(
            """# RPC Review

| 用例 | 场景 | 预期结果 | 防止的问题 | 优先级 |
| --- | --- | --- | --- | --- |
| `RPC-01` | valid request | success | normal calls fail | P0 |
| `RPC-02` | missing input | reject | invalid input reaches core | P1 |
""",
            encoding="utf-8",
        )
        tests = root / "tests" / "rpc" / "test_submit.py"
        tests.parent.mkdir(parents=True)
        tests.write_text(
            "# TEST-MAP: RPC-01\ndef test_valid():\n    assert True\n",
            encoding="utf-8",
        )

    def test_dynamic_coverage_and_require_complete(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            partial = run(str(CHECKER), "--root", str(root))
            self.assertEqual(partial.returncode, 0, partial.stdout)
            self.assertIn("automation coverage: 1/2", partial.stdout)
            self.assertIn("unautomated: RPC-02", partial.stdout)

            required = run(str(CHECKER), "--root", str(root), "--require-complete")
            self.assertEqual(required.returncode, 1, required.stdout)

            with (root / "tests" / "rpc" / "test_submit.py").open("a", encoding="utf-8") as handle:
                handle.write("\n# TEST-MAP: RPC-02\ndef test_missing():\n    assert True\n")
            complete = run(str(CHECKER), "--root", str(root), "--require-complete")
            self.assertEqual(complete.returncode, 0, complete.stdout)
            self.assertIn("automation coverage: 2/2", complete.stdout)
            self.assertIn("unautomated: none", complete.stdout)

    def test_orphan_mapping_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            with (root / "tests" / "rpc" / "test_submit.py").open("a", encoding="utf-8") as handle:
                handle.write("\n# TEST-MAP: RPC-99\ndef test_orphan():\n    assert True\n")
            result = run(str(CHECKER), "--root", str(root))
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("orphan mappings: RPC-99", result.stdout)


class SkillContractTests(unittest.TestCase):
    def test_review_gate_precedes_automation(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        agents = (ROOT / "assets" / "repo-tests" / "root" / "AGENTS.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Do not collapse review and implementation into one handoff", skill)
        self.assertIn("Generate or update automated tests only after", skill)
        self.assertIn("stop before changing automated tests", agents)

    def test_corrective_feedback_is_persisted_without_case_status(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        agents = (ROOT / "assets" / "repo-tests" / "root" / "AGENTS.md").read_text(
            encoding="utf-8"
        )
        feedback_format = (
            "- model: <model-id-or-unavailable> | cases: <case IDs or review scope> | "
            "feedback: <human feedback verbatim>"
        )
        self.assertIn("## Review Feedback Collection", skill)
        self.assertIn(feedback_format, skill)
        self.assertIn("Do not record approval without a correction", skill)
        self.assertIn("reviews/review-feedback.md", agents)
        self.assertIn("not a case status", agents)

    def test_review_template_has_no_case_status_or_automation_column(self) -> None:
        template = (ROOT / "templates" / "test-review.md").read_text(encoding="utf-8")
        self.assertIn("| 用例 | 场景 | 预期结果 | 防止的问题 | 优先级 |", template)
        self.assertNotIn("| 状态 |", template)
        self.assertNotIn("| 自动化 |", template)
        self.assertNotIn("TP-[", template)


if __name__ == "__main__":
    unittest.main()
