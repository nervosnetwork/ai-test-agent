#!/usr/bin/env python3
"""Validate B evidence and render all selected Cases, including absent implementations."""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

from check_test_map import build_report
from check_test_design import check_design
from evidence_annotations import symbols
from workflow_lib import inside, read_json, scope_paths, validate_schema, fresh_inputs, digest, fingerprint

SCHEMA_ROOT = Path(__file__).resolve().parent.parent / "schemas"


def validate_coverage(root: Path, state: dict, coverage: dict) -> list[str]:
    validate_schema(coverage, read_json(SCHEMA_ROOT / "coverage.schema.json"))
    errors = []
    expected = set(state["cases"])
    records = {item["case_id"]: item for item in coverage["cases"]}
    if len(records) != len(coverage["cases"]):
        errors.append("duplicate evidence Case")
    if set(records) != expected:
        errors.append(f"evidence Case set mismatch: missing={sorted(expected - set(records))}, extra={sorted(set(records) - expected)}")
    if coverage["scope"] != state["scope"] or coverage["input_fingerprint"] != state["coverage_input"]["fingerprint"]:
        errors.append("evidence scope/input fingerprint mismatch")
    mapping = build_report(root, state["reviews"])
    for case, item in records.items():
        if set(item["spec_refs"]) != set(state["spec_refs"].get(case, [])):
            errors.append(f"{case}: Spec references differ from selected design")
        if item["coverage"] == "covered" and not item["bindings"]:
            errors.append(f"{case}: covered requires implementation bindings")
        if item["coverage"] == "missing" and item["bindings"]:
            errors.append(f"{case}: missing must have no bindings")
        for binding in item["bindings"]:
            filename = binding["file"]
            path = inside(root, filename)
            if filename not in state["coverage_input"]["files"]:
                errors.append(f"{case}: binding not included in B input: {filename}")
            locations = mapping["mapping_locations"].get(case, [])
            if not any(place.rsplit(":", 1)[0] == filename for place in locations):
                errors.append(f"{case}: binding has no TEST-MAP in {filename}")
            code = path.read_text(encoding="utf-8")
            if path.suffix == ".py":
                node = symbols(code).get(binding["symbol"])
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    errors.append(f"{case}: binding symbol missing: {binding['symbol']}")
            elif binding["symbol"] not in code:
                errors.append(f"{case}: binding symbol anchor missing")
            if item["coverage"] == "covered" and (not binding["assertions"] or binding["missing"]):
                errors.append(f"{case}: covered requires located assertions and no binding gaps")
            for assertion in binding["assertions"]:
                apath = inside(root, assertion["file"])
                if assertion["file"] not in state["coverage_input"]["files"]:
                    errors.append(f"{case}: assertion dependency not in B input")
                text = apath.read_text(encoding="utf-8")
                if apath.suffix == ".py":
                    node = symbols(text).get(assertion["symbol"])
                    fragment = ast.get_source_segment(text, node) if node is not None else ""
                else:
                    fragment = text if assertion["symbol"] in text else ""
                if not fragment or assertion["text"] not in fragment:
                    errors.append(f"{case}: assertion location does not match code: {assertion['file']}::{assertion['symbol']}")
    return errors


def execution_for(item: dict, execution: dict | None, fingerprint: str):
    if not execution or execution.get("collected", 0) <= 0:
        return "not_run", False
    if execution.get("input_fingerprint") != fingerprint:
        return "not_run", False
    if execution.get("status") == "blocked":
        return "blocked", False
    results = execution.get("results", [])
    wanted = {selector for b in item.get("bindings", []) for selector in (b["parameters"] or [b["runner_selector"]])}
    if not wanted:
        return "not_run", False
    matched = [row for row in results if row.get("selector") in wanted]
    if {row["selector"] for row in matched} != wanted:
        return "not_run", False
    statuses = {row["status"] for row in matched}
    unstable = any(row.get("unstable", False) for row in matched) or len(matched) != len(wanted)
    for status in ("failed", "blocked", "skipped", "not_run"):
        if status in statuses:
            return status, unstable
    return ("passed" if statuses == {"passed"} else "not_run"), unstable


def build_evidence_report(root: Path, state: dict, coverage=None, execution=None) -> dict:
    errors = []
    mapping = build_report(root, state["reviews"])
    for key in ("duplicate_review_ids", "orphan_mappings", "missing_automation_markers", "automation_marker_mismatches"):
        if mapping[key]:
            errors.append(f"{key}: {mapping[key]}")
    records = {}
    valid = False
    if coverage is not None:
        try:
            if state.get("coverage_evidence_hash") and fingerprint(coverage) != state["coverage_evidence_hash"]:
                raise ValueError("coverage artifact changed after validation")
            problems = validate_coverage(root, state, coverage)
            errors.extend(problems)
            valid = not problems
            records = {item["case_id"]: item for item in coverage["cases"]}
        except (ValueError, KeyError, TypeError, OSError, SyntaxError) as error:
            errors.append(f"invalid coverage: {error}")
    frozen = state.get("final_input") or state.get("coverage_input")
    try:
        current = frozen is not None and fresh_inputs(root, state, frozen)
    except (ValueError, OSError):
        current = False
    if frozen and not current:
        errors.append("scope inputs changed; evidence/execution is stale")
    if execution and execution.get("status") in {"failed", "blocked"}:
        errors.append("runner " + execution["status"] + ": " + str(execution.get("error", execution.get("failure_kind", "unclassified"))))
    if execution:
        log = execution.get("output_file")
        try:
            if not log or digest(inside(root, log).read_bytes()) != execution.get("output_sha256"):
                raise ValueError("execution output changed")
        except (OSError, ValueError) as error:
            errors.append(str(error))
            execution = None
    rows = []
    for case, definition in sorted(state["cases"].items()):
        item = records.get(case)
        mapped = case in mapping["mapping_locations"]
        version = "not_reviewed" if item is None or not valid else "current" if current else "stale"
        status, unstable = execution_for(item or {}, execution, frozen["fingerprint"] if frozen else "")
        if not current:
            status = "not_run"
        issues = []
        if item:
            issues.extend(item["limitations"])
            issues.extend(gap for binding in item["bindings"] for gap in binding["missing"])
        coverage_status = item["coverage"] if item else "uncertain" if mapped else "missing"
        if version != "current":
            issues.append(version)
        if coverage_status != "covered":
            issues.append(coverage_status)
        if status != "passed":
            issues.append(status)
        if unstable:
            issues.append("unstable")
        rows.append({"case_id": case, "mapped": mapped, "coverage": coverage_status, "validity": version,
                     "execution": status, "unstable": unstable, "priority": definition["priority"], "issues": issues})
    independent = bool(coverage and coverage.get("reviewer", {}).get("isolation") == "contract_tested" and state.get("coverage_adapter", {}).get("contract_tested") and state.get("design_adapter", {}).get("contract_tested"))
    required = set(state["required_cases"]) | {case for case, d in state["cases"].items() if d["priority"] == "P0"}
    required_gap = any(row["case_id"] in required and (row["coverage"] != "covered" or row["validity"] != "current" or row["execution"] != "passed" or row["unstable"]) for row in rows)
    any_gap = any(row["coverage"] != "covered" or row["validity"] != "current" or row["execution"] != "passed" or row["unstable"] for row in rows)
    gates_complete = bool(state.get("approval")) and state.get("stage") in {"EXECUTED", "READY_FOR_ACCEPTANCE"}
    decision = "blocked" if errors or required_gap else "needs_decision" if any_gap or not independent or state.get("design_decisions") or not gates_complete else "ready_for_acceptance"
    return {"schema_version": "2.0", "scope": state["scope"], "result": decision, "independent_review": independent,
            "errors": errors, "cases": rows, "scope_boundary": state["scope_boundary"],
            "execution_level": execution.get("level", "none") if execution else "none"}


def render_report(report: dict, coverage=None) -> str:
    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    lines = [f"# Coverage: {report['scope']}", "", f"Result: **{report['result']}**", "",
             f"Scope boundary: {report['scope_boundary']}",
             f"Independent review contract tested: {report['independent_review']}",
             f"Execution association: {report['execution_level']}", "",
             "| Case | Mapping | B coverage | Evidence | Execution | Action / limitations |", "| --- | --- | --- | --- | --- | --- |"]
    for row in sorted(report["cases"], key=lambda x: (not bool(x["issues"]), x["case_id"])):
        lines.append("| " + " | ".join(cell(x) for x in [row['case_id'], row['mapped'], row['coverage'], row['validity'], row['execution'] + (" (unstable)" if row['unstable'] else ""), "; ".join(row['issues']) or "none"]) + " |")
    lines += ["", *[f"- {cell(e)}" for e in report["errors"]]]
    if coverage:
        lines += ["", "## Code evidence", ""]
        for item in coverage.get("cases", []):
            lines += [f"### {cell(item['case_id'])}", ""]
            for b in item['bindings']:
                lines += [f"- `{cell(b['file'])}::{cell(b['symbol'])}`; selector `{cell(b['runner_selector'])}`",
                          f"  - Setup: {cell(b['setup'])}", f"  - Trigger: {cell(b['trigger'])}",
                          f"  - Observation: {cell(b['observation'])}"]
                lines += [f"  - Assertion: `{cell(a['file'])}::{cell(a['symbol'])}`: {cell(a['text'])}" for a in b['assertions']]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--require-reviewed", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        root = args.root.resolve()
        state_path, reports = scope_paths(root, args.scope)
        state = read_json(state_path)
        coverage = read_json(reports / "coverage.json") if (reports / "coverage.json").exists() else None
        execution = read_json(reports / "execution.json") if (reports / "execution.json").exists() else None
        report = build_evidence_report(root, state, coverage, execution)
        (reports / "coverage.md").parent.mkdir(parents=True, exist_ok=True)
        (reports / "coverage.md").write_text(render_report(report, coverage), encoding="utf-8")
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f"{error}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render_report(report))
    return int(bool(report["errors"]) or args.require_reviewed and (not report["independent_review"] or any(row["validity"] != "current" for row in report["cases"])))


if __name__ == "__main__":
    raise SystemExit(main())
