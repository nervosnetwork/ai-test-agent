from __future__ import annotations

import os
import json
import shutil
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
    def test_single_suite_uses_central_reviews_and_suite_automation(self) -> None:
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
            self.assertIn("layout: centralized-reviews-with-suites", first.stdout)
            for relative in [
                "AGENTS.md",
                "README.md",
                "reviews/README.md",
                "suites/api/AGENTS.md",
                "suites/api/README.md",
                "suites/api/tests/README.md",
                "suites/api/fixtures/README.md",
                "scripts/check_test_map.py",
                "templates/test-review.md",
            ]:
                self.assertTrue((output / relative).is_file(), relative)
            self.assertFalse((output / "tests").exists())
            self.assertFalse((output / "fixtures").exists())
            self.assertFalse((output / "suites" / "api" / "reviews").exists())
            self.assertNotIn("MOD -> FUNC -> COV -> TP", (output / "README.md").read_text())
            self.assertIn(
                "centralized under root `reviews/`",
                (output / "README.md").read_text(),
            )
            self.assertIn(
                "| `[AREA-01]` | - [ ] ",
                (output / "templates" / "test-review.md").read_text(),
            )
            # Generated projects must receive the depth guidance, not just the installed Skill.
            design = (output / "docs/ai-test-agent/test-design.md").read_text()
            self.assertEqual(design, (ROOT / "references/test-design.md").read_text())
            self.assertIn("## Recursive decomposition", design)
            decomposition = (output / "docs/ai-test-agent/decomposition.md").read_text()
            self.assertIn("Stop only when a leaf", decomposition)
            # Gate guidance and every other reference must propagate to generated projects.
            for reference in (ROOT / "references").glob("*.md"):
                self.assertEqual(
                    (output / "docs/ai-test-agent" / reference.name).read_text(),
                    reference.read_text(),
                )
            self.assertIn("### Depth review before G1", design)
            self.assertIn("Scope limits breadth, not test-tree depth", (output / "AGENTS.md").read_text())
            template = (output / "templates/test-review.md").read_text()
            self.assertEqual(template, (ROOT / "templates/test-review.md").read_text())
            # Both output modes require a linked Spec → tree → Case design.
            for name in ("test-review.md", "test-review-full.md", "security-review.md"):
                content = (output / "templates" / name).read_text().replace("[AREA-01]", "AREA-01")
                review = output / "reviews" / "sample.md"
                review.write_text(content)
                result = run(str(output / "scripts/check_test_design.py"),
                             "--review", "reviews/sample.md", cwd=output)
                self.assertEqual(result.returncode, 0, result.stdout)
                result = run(str(output / "scripts/check_test_map.py"),
                             "--review", "reviews/sample.md", cwd=output)
                self.assertEqual(result.returncode, 0, result.stdout)
            review.unlink()

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

    def test_multiple_suites_share_root_reviews(self) -> None:
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
            self.assertIn("layout: centralized-reviews-with-suites", result.stdout)
            for relative in [
                "reviews/README.md",
                "suites/integration/tests/README.md",
                "suites/integration/config/README.md",
                "suites/performance/benchmarks/README.md",
                "suites/performance/workloads/README.md",
            ]:
                self.assertTrue((output / relative).is_file(), relative)
            self.assertFalse((output / "tests").exists())
            self.assertFalse((output / "suites" / "integration" / "reviews").exists())
            self.assertFalse((output / "suites" / "performance" / "reviews").exists())

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
            self.assertIn("case mappings: 1/2", partial.stdout)
            self.assertIn("unmapped: RPC-02", partial.stdout)
            self.assertIn("execution / behavior verification: not checked", partial.stdout)

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
            self.assertIn("case mappings: 2/2", complete.stdout)
            self.assertIn("unmapped: none", complete.stdout)

    def test_orphan_mapping_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            with (root / "tests" / "rpc" / "test_submit.py").open("a", encoding="utf-8") as handle:
                handle.write("\n# TEST-MAP: RPC-99\ndef test_orphan():\n    assert True\n")
            result = run(str(CHECKER), "--root", str(root))
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("orphan mappings: RPC-99", result.stdout)

    def test_mapping_is_not_execution_and_legacy_json_aliases_remain(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_project(root)
            # A mapping remains an association even when the body would fail if run.
            code = root / "tests/rpc/test_submit.py"
            code.write_text(code.read_text().replace("assert True", "assert False"))
            result = run(str(CHECKER), "--root", str(root), "--json")
            self.assertEqual(result.returncode, 0, result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual(report["mapped"], ["RPC-01"])
            self.assertEqual(report["unmapped"], ["RPC-02"])
            self.assertEqual(report["mapped_case_count"], report["automated_case_count"])
            self.assertEqual(report["mapping_ratio"], report["automation_coverage"])
            self.assertEqual(report["execution"], "not_checked")
            self.assertEqual(report["behavior_verification"], "not_checked")

    def test_browser_module_extensions_are_associated(self) -> None:
        for suffix in (".mjs", ".cjs"):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.write_project(root)
                (root / "tests/rpc/test_browser").with_suffix(suffix).write_text("// TEST-MAP: RPC-02\n")
                review = root / "reviews/rpc/submit_transaction.md"
                review.write_text(review.read_text().replace("- [ ] missing input", "- [x] missing input"))
                result = run(str(CHECKER), "--root", str(root), "--require-complete", "--json")
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertEqual(json.loads(result.stdout)["mapped"], ["RPC-01", "RPC-02"])

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

    def test_default_root_and_suite_case_directory_are_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "demo-tests"
            scripts = root / "scripts"
            scripts.mkdir(parents=True)
            shutil.copy2(CHECKER, scripts / "check_test_map.py")

            review = root / "reviews" / "p2p" / "ping.md"
            review.parent.mkdir(parents=True)
            review.write_text(
                """# P2P Review

| 用例 | 场景 | 预期结果 | 防止的问题 | 优先级 |
| --- | --- | --- | --- | --- |
| `P2P-PING-01` | - [x] valid ping | pong | liveness failure | P0 |
""",
                encoding="utf-8",
            )
            case = root / "suites" / "p2p" / "runner" / "src" / "case" / "ping.rs"
            case.parent.mkdir(parents=True)
            case.write_text("// TEST-MAP: P2P-PING-01\n", encoding="utf-8")
            unrelated = Path(temporary) / "elsewhere"
            unrelated.mkdir()

            result = run(str(scripts / "check_test_map.py"), cwd=unrelated)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("case mappings: 1/1", result.stdout)
            self.assertIn("orphan mappings: none", result.stdout)


class SkillContractTests(unittest.TestCase):
    def read_contract(self) -> str:
        paths = [ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]
        return "\n".join(path.read_text(encoding="utf-8") for path in paths)

    def test_approved_automation_uses_native_runner_without_full_workflow_state(self) -> None:
        # Conversational G1/G2 approvals do not require full PR-v2 state or reports.
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "demo-tests"
            created = run(str(INIT), "--project", "Demo", "--source-repo", "../demo",
                          "--suites", "api", "--output", str(output))
            self.assertEqual(created.returncode, 0, created.stdout)
            review = output / "reviews" / "sample.md"
            template = (output / "templates" / "test-review.md").read_text()
            review.write_text(template.replace("[AREA-01]", "AREA-01").replace("- [ ]", "- [x]"))
            test = output / "suites" / "api" / "tests" / "test_sample.py"
            test.write_text("import unittest\n\nclass Sample(unittest.TestCase):\n"
                            "    # TEST-MAP: AREA-01\n"
                            "    def test_addition(self):\n"
                            "        self.assertEqual(1 + 1, 2)\n")
            for script in ("check_test_design.py", "check_test_map.py"):
                checked = run(str(output / "scripts" / script),
                              "--review", "reviews/sample.md", cwd=output)
                self.assertEqual(checked.returncode, 0, checked.stdout)
            executed = run("-m", "unittest", "discover", "-s", "suites/api/tests", cwd=output)
            self.assertEqual(executed.returncode, 0, executed.stdout)
            self.assertIn("Ran 1 test", executed.stdout)
            for directory in (output / ".ai-test-agent", output / "reports"):
                self.assertFalse(directory.exists() and any(directory.rglob("*.json")))

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
        self.assertLess(template.index("## Spec"), template.index("## 测试树"))
        self.assertLess(template.index("## 测试树"), template.index("## 用例"))
        self.assertIn("<!-- TEST-TREE-BEGIN -->", template)
        self.assertIn("<!-- TEST-CASES-BEGIN -->", template)
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

        self.assertLessEqual(len(skill.split()), 650)
        self.assertLessEqual(len(agents.split()), 500)
        self.assertLessEqual(len(suite_agents.split()), 140)
        self.assertIn("Do not automatically continue to the next interface", skill)
        self.assertIn("Do not repeatedly poll", skill)
        # Follow-up edits inside an existing scope must not re-enter the full PR-v2 pipeline.
        for content in (skill, agents):
            self.assertIn("need", content)
            self.assertIn("no G1", content.replace("\n", " "))
            self.assertIn("is not a request", content)
        for reference in [
            "help.md",
            "initialize.md",
            "review-cases.md",
            "automation-maintenance.md",
        ]:
            self.assertTrue((ROOT / "references" / reference).is_file(), reference)
            self.assertIn(f"references/{reference}", skill)

    def test_reviews_are_central_and_automation_is_suite_owned(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        initialize = (ROOT / "references" / "initialize.md").read_text(encoding="utf-8")
        suite_agents = (ROOT / "assets" / "repo-tests" / "suite" / "AGENTS.md").read_text(
            encoding="utf-8"
        )
        checker = (ROOT / "scripts" / "check_test_map.py").read_text(encoding="utf-8")

        self.assertIn("Root `reviews/` centrally", skill)
        self.assertIn("under `suites/<suite>/`", skill)
        self.assertIn("Do not create suite-local `reviews/` copies", initialize)
        self.assertIn("root `../../reviews/`", suite_agents)
        self.assertFalse((ROOT / "assets" / "repo-tests" / "suite" / "reviews").exists())
        self.assertIn('CODE_DIR_NAMES = {"case", "tests", "benchmarks", "targets"}', checker)
        self.assertIn("default=PROJECT_ROOT", checker)


if __name__ == "__main__":
    unittest.main()
