#!/usr/bin/env python3
"""Record a native command and optional fresh JUnit outcomes without PR-v2 gates."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

from workflow_lib import digest, git, inside, product_state, run_bounded, scope_paths, snapshot, write_json


def junit_outcomes(path: Path) -> dict:
    tree = ET.parse(path).getroot()
    def local(tag):
        return tag.rsplit("}", 1)[-1]
    if local(tree.tag) not in {"testsuite", "testsuites"}:
        raise ValueError("expected a JUnit testsuite/testsuites report")
    rows = []
    for node in tree.iter():
        if local(node.tag) != "testcase":
            continue
        children = {local(child.tag) for child in node}
        status = next((s for s in ("error", "failure", "skipped") if s in children), "passed")
        rows.append({"classname": node.get("classname", ""), "name": node.get("name", ""),
                     "status": status})
    counts = Counter(row["status"] for row in rows)
    # Honor suite-level failures too; inconsistent summaries must never hide a failure.
    for suite in tree.iter():
        if local(suite.tag) not in {"testsuite", "testsuites"}:
            continue
        children = [node for node in suite.iter() if local(node.tag) == "testcase"]
        expected = Counter()
        for node in children:
            tags = {local(child.tag) for child in node}
            expected[next((s for s in ("error", "failure", "skipped") if s in tags), "passed")] += 1
        for key, count in (("tests", len(children)), ("failures", expected["failure"]),
                           ("errors", expected["error"]), ("skipped", expected["skipped"])):
            if key in suite.attrib and int(suite.attrib[key]) != count:
                raise ValueError(f"JUnit {key} summary disagrees with testcase records")
    selectors = Counter((row["classname"], row["name"]) for row in rows)
    return {"reported": len(rows), "passed": counts["passed"], "failed": counts["failure"],
            "errors": counts["error"], "skipped": counts["skipped"], "results": rows,
            "ambiguous_selectors": [list(key) for key, n in selectors.items() if n > 1]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--product", type=Path, required=True, help="Git checkout being tested")
    parser.add_argument("--scope", required=True)
    parser.add_argument("--input", action="append", default=[], help="Declared test/helper/config file relative to root")
    parser.add_argument("--junit", action="store_true", help="Import a fresh native report at argv placeholder {junit}")
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command or not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("a native command and positive timeout are required")
    root = args.root.resolve()
    product = (root / args.product).resolve()
    try:
        state, reports = scope_paths(root, args.scope)
        if state.exists():
            raise ValueError("active PR-v2 scope; use pr_workflow.py run instead")
        output = inside(root, str((reports / "execution.log").relative_to(root)), exists=False)
        receipt = inside(root, str((reports / "execution.json").relative_to(root)), exists=False)
        native = inside(root, str((reports / "native-results.xml").relative_to(root)), exists=False)
        # Validate inputs before clearing this scope's owned previous native report.
        files = snapshot(root, args.input)
        head = git(product, "rev-parse", "HEAD")
        config = {"root": str(product), "base_tip": head, "diff_base": head}
        before = product_state(root, config)
        reports.mkdir(parents=True, exist_ok=True)
        native.unlink(missing_ok=True)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    command = [arg.replace("{junit}", str(native)) for arg in command]
    env = {k: os.environ[k] for k in ("PATH", "LANG", "LC_ALL", "TMPDIR", "SYSTEMROOT") if k in os.environ}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    record = {"schema_version": "compact-execution-1", "scope": args.scope, "command": command,
              "cwd": str(root), "started_at": datetime.now(timezone.utc).isoformat(),
              "environment": {"system": platform.system(), "release": platform.release(),
                              "machine": platform.machine(), "python": platform.python_version(),
                              "keys": sorted(env)},
              "product_root": str(product), "product": before,
              "test_inputs": files, "test_inputs_scope": "declared files only",
              "level": "suite", "outcomes": None, "status": "not_run", "exit_code": None,
              "independent_review": False, "behavior_verification": "not_checked",
              "output_file": output.relative_to(root).as_posix(), "errors": []}
    started = time.monotonic()
    try:
        with output.open("w", encoding="utf-8") as log:
            result = run_bounded(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT,
                                 timeout=args.timeout)
        record["exit_code"] = result.returncode
        record["status"] = "failed" if result.returncode else "completed"
        if args.junit:
            outcomes = junit_outcomes(native)
            record.update(outcomes=outcomes, level="native_testcase",
                          native_report_file=native.relative_to(root).as_posix(),
                          native_report_sha256=digest(native.read_bytes()))
            if outcomes["reported"] == 0 or outcomes["skipped"] == outcomes["reported"]:
                raise ValueError("no executed native testcases (zero tests or all skipped)")
            if outcomes["failed"] or outcomes["errors"]:
                record["status"] = "failed"
                if not result.returncode:
                    record["errors"].append("native report contains failures despite command exit 0")
        else:
            record["note"] = "No supported native report requested; exit status is suite-level only."
    except (OSError, ValueError, ET.ParseError, subprocess.TimeoutExpired) as error:
        record["errors"].append(str(error))
        record["status"] = "blocked"
    try:
        record["product_after"] = product_state(root, config)
        record["inputs_unchanged"] = record["product_after"] == before and snapshot(root, args.input) == files
        if not record["inputs_unchanged"]:
            record["errors"].append("product or declared test inputs changed during execution")
    except (OSError, ValueError) as error:
        record["inputs_unchanged"] = False
        record["errors"].append(str(error))
    if record["errors"]:
        record["status"] = "blocked"
    record["duration_seconds"] = round(time.monotonic() - started, 3)
    record["finished_at"] = datetime.now(timezone.utc).isoformat()
    record["output_sha256"] = digest(output.read_bytes())
    code = record["exit_code"]
    record["wrapper_exit_code"] = (code if code >= 0 else 128 - code) if code else 2 if record["errors"] else 0
    write_json(receipt, record)
    print(json.dumps({"receipt": str(receipt), "status": record["status"],
                      "exit_code": code, "wrapper_exit_code": record["wrapper_exit_code"]}))
    return record["wrapper_exit_code"]


if __name__ == "__main__":
    sys.exit(main())
