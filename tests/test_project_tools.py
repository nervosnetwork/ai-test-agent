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
            self.assertIn(
                "| `[AREA-01]` | - [ ] ",
                (output / "templates" / "test-review.md").read_text(),
            )

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
| `RPC-01` | - [x] valid request | success | normal calls fail | P0 |
| `RPC-02` | - [ ] missing input | reject | invalid input reaches core | P1 |
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
            review = root / "reviews" / "rpc" / "submit_transaction.md"
            review.write_text(
                review.read_text(encoding="utf-8").replace(
                    "| `RPC-02` | - [ ] missing input",
                    "| `RPC-02` | - [x] missing input",
                ),
                encoding="utf-8",
            )
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

    def test_missing_or_stale_scenario_checkbox_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            review = root / "reviews" / "rpc" / "submit_transaction.md"
            original = review.read_text(encoding="utf-8")

            review.write_text(original.replace("- [x] valid request", "valid request"), encoding="utf-8")
            missing = run(str(CHECKER), "--root", str(root))
            self.assertEqual(missing.returncode, 1, missing.stdout)
            self.assertIn("missing automation markers: RPC-01", missing.stdout)

            review.write_text(original.replace("- [x] valid request", "- [ ] valid request"), encoding="utf-8")
            stale = run(str(CHECKER), "--root", str(root))
            self.assertEqual(stale.returncode, 1, stale.stdout)
            self.assertIn("automation marker mismatches: RPC-01 (expected - [x])", stale.stdout)


class SkillContractTests(unittest.TestCase):
    def read_contract(self) -> str:
        paths = [ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]
        return "\n".join(path.read_text(encoding="utf-8") for path in paths)

    def test_review_gate_precedes_automation(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        agents = (ROOT / "assets" / "repo-tests" / "root" / "AGENTS.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Do not combine review and implementation in one handoff", skill)
        self.assertIn("Generate or update mapped tests only after", skill)
        self.assertIn("stop before changing automated tests", agents)

    def test_corrective_feedback_is_persisted_without_case_status(self) -> None:
        skill = self.read_contract()
        agents = (ROOT / "assets" / "repo-tests" / "root" / "AGENTS.md").read_text(
            encoding="utf-8"
        )
        feedback_format = (
            "- model: <model-id-or-unavailable> | cases: <case IDs or review scope> | "
            "feedback: <human feedback verbatim>"
        )
        self.assertIn("## Corrective feedback", skill)
        self.assertIn(feedback_format, skill)
        self.assertIn("Do not record approval without a correction", skill)
        self.assertIn("reviews/review-feedback.md", agents)
        self.assertIn("not a case status", agents)

    def test_review_template_uses_scenario_checkbox_without_automation_column(self) -> None:
        template = (ROOT / "templates" / "test-review.md").read_text(encoding="utf-8")
        self.assertIn("| 用例 | 场景 | 预期结果 | 防止的问题 | 优先级 |", template)
        self.assertIn("| `[AREA-01]` | - [ ] ", template)
        self.assertNotIn("| 状态 |", template)
        self.assertNotIn("| 自动化 |", template)
        self.assertNotIn("TP-[", template)

    def test_automation_guidance_requires_simple_tests_and_explained_assertions(self) -> None:
        skill = self.read_contract()
        agents = (ROOT / "assets" / "repo-tests" / "root" / "AGENTS.md").read_text(
            encoding="utf-8"
        )
        suite_agents = (
            ROOT / "assets" / "repo-tests" / "suite" / "AGENTS.md"
        ).read_text(encoding="utf-8")
        agent_prompt = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

        for content in (skill, agents, suite_agents):
            self.assertIn("direct", content)
            self.assertIn("readable", content)
            self.assertIn("abstraction", content)
            self.assertIn("assertions", content)
            self.assertIn("prove the expected behavior", content)

        self.assertIn("Added automation:", skill)
        self.assertIn("direct TEST-MAP tests", agent_prompt)

    def test_token_budget_rules_and_progressive_disclosure(self) -> None:
        skill_path = ROOT / "SKILL.md"
        skill = skill_path.read_text(encoding="utf-8")
        agents = (ROOT / "assets" / "repo-tests" / "root" / "AGENTS.md").read_text(
            encoding="utf-8"
        )
        suite_agents = (
            ROOT / "assets" / "repo-tests" / "suite" / "AGENTS.md"
        ).read_text(encoding="utf-8")

        self.assertLessEqual(len(skill.split()), 1200)
        self.assertLessEqual(len(agents.split()), 500)
        self.assertLessEqual(len(suite_agents.split()), 140)
        self.assertIn("Do not automatically continue to the next interface", skill)
        self.assertIn("Do not repeatedly poll", skill)
        for reference in [
            "help.md",
            "initialize.md",
            "review-cases.md",
            "automation-maintenance.md",
        ]:
            self.assertTrue((ROOT / "references" / reference).is_file(), reference)
            self.assertIn(f"references/{reference}", skill)


if __name__ == "__main__":
    unittest.main()
