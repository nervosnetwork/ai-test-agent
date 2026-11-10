#!/usr/bin/env python3
"""Check explicit Spec/tree/case relationships, not semantic completeness."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from check_test_map import CASE_TOKEN, build_report, review_rows, selected_reviews
from workflow_lib import design_hash

SPEC = r"SPEC-\d{2,}"
# Spec fields may be list items so they render on separate lines.
ITEM = r"(?:[-*]\s+)?"
PENDING = ("待确认",)


def block(text: str, name: str) -> str:
    start, end = f"<!-- TEST-{name}-BEGIN -->", f"<!-- TEST-{name}-END -->"
    if text.count(start) != 1 or text.count(end) != 1 or text.index(start) > text.index(end):
        raise ValueError(f"expected one ordered TEST-{name} block")
    return text.split(start, 1)[1].split(end, 1)[0]


def section(text: str, title: str) -> str | None:
    """Body of a level-two section, or None when the review has no such heading."""
    start = re.search(rf"(?m)^##\s+{re.escape(title)}\s*$", text)
    if not start:
        return None
    rest = text[start.end():]
    end = re.search(r"(?m)^##\s+", rest)
    return rest[:end.start()] if end else rest


def tree_case_ids(line: str, known) -> set[str]:
    """Case references in a tree line; prose tokens such as SHA-256 are labels, not Case IDs."""
    tokens = set(re.findall(rf"\b{CASE_TOKEN}\b", line)) - set(re.findall(SPEC, line))
    return {token for token in tokens if token in known
            or re.search(rf"\b{re.escape(token)}\b\s*\[(?:primary|ref)\]", line)}


def check_design(root: Path, reviews: list[str]) -> dict:
    errors, warnings, decisions, cases, associations = [], [], [], {}, {}
    all_spec_refs = set()
    files = selected_reviews(root, reviews)
    mapping = build_report(root, reviews)
    for key in ("duplicate_review_ids", "orphan_mappings", "missing_automation_markers"):
        if mapping[key]:
            errors.append(f"{key}: {mapping[key]}")
    for path in files:
        name = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        try:
            case_block = block(text, "CASES")
            tree = block(text, "TREE")
        except ValueError as error:
            errors.append(f"{name}: {error}; migrate this selected document to v2")
            continue
        # Sections may appear in reader-first order; links, not position, are validated.
        local, pending = {}, []
        for number, line, match in review_rows(path):
            cells = re.split(r"(?<!\\)\|", line)[1:-1]
            case = match.group("case")
            if len(cells) != 5 or any(not cell.strip() for cell in cells):
                errors.append(f"{name}:{number}: expected five nonempty cells")
                continue
            priority = cells[4].strip()
            if priority not in {"P0", "P1", "P2"}:
                errors.append(f"{case}: invalid priority")
            local[case] = {"review": name, "line": number, "priority": priority, "expected": cells[2].strip()}
            if any(mark in cells[2] for mark in PENDING):
                decisions.append(f"{case}: {cells[2].strip()}")
                pending.append(case)
        if not local:
            errors.append(f"{name}: no case definitions")
        # Reject malformed rows inside the explicit block rather than silently dropping them.
        for line in case_block.splitlines():
            if line.startswith("|") and not re.match(r"^\|\s*(用例|[-: ]+\|)", line) and not re.match(rf"^\|\s*`?{CASE_TOKEN}`?\s*\|", line):
                errors.append(f"{name}: malformed case row: {line}")
        specs = {}
        chunks = re.split(rf"(?m)^###\s+({SPEC})\s*[:：].*\n", text)
        for index in range(1, len(chunks), 2):
            sid, body = chunks[index:index + 2]
            body = re.split(r"(?m)^#{1,3}\s+", body)[0]
            if sid in specs:
                errors.append(f"{name}: duplicate {sid}")
            specs[sid] = body
            for label in ("Condition", "Expected", "Observable", "Basis", "Source", "Testing"):
                if not re.search(rf"(?m)^{ITEM}{label}:\s*\S", body):
                    errors.append(f"{name}#{sid}: missing {label}")
            if not re.search(rf"(?m)^{ITEM}Source: (explicit|observation|inference)\s*$", body):
                errors.append(f"{name}#{sid}: invalid Source")
            if re.search(rf"(?m)^{ITEM}Source: (inference|observation)\s*$", body):
                decisions.append(f"{name}#{sid}: expected behavior requires human decision")
            if not re.search(rf"(?m)^{ITEM}Testing: (required\s*$|not_tested — \S)", body):
                errors.append(f"{name}#{sid}: explain testing disposition")
        if not specs:
            errors.append(f"{name}: no Spec rules")
        all_spec_refs.update(f"{name}#{sid.lower()}" for sid in specs)
        primary = {case: 0 for case in local}
        used = set()
        tree_ids = set()
        for line in tree.splitlines():
            if not line.strip():
                continue
            if not re.match(r"^\s*-\s+\S", line):
                errors.append(f"{name}: tree must use Markdown nested lists")
                continue
            unresolved = re.search(r"\[(unanalysed|pending|not_applicable)\]", line)
            if unresolved:
                if " — " not in line or not line.split(" — ", 1)[1].strip():
                    errors.append(f"{name}: branch disposition needs a reason: {line.strip()}")
                if unresolved[1] != "not_applicable":
                    decisions.append(f"{name}: {line.strip()}")
            ids = tree_case_ids(line, local)
            refs = set(re.findall(SPEC, line))
            for case in ids:
                tree_ids.add(case)
                if case not in local:
                    errors.append(f"{name}: dangling tree case {case}")
                    continue
                # Prefer the marker attached to this ID; fall back to the line for older layouts.
                own = re.search(rf"\b{re.escape(case)}\b\s*\[(primary|ref)\]", line)
                kind = own[1] if own else "primary" if "[primary]" in line else "ref" if "[ref]" in line else None
                if kind == "primary":
                    primary[case] += 1
                elif kind is None:
                    errors.append(f"{case}: tree reference needs [primary] or [ref]")
                if not refs:
                    errors.append(f"{case}: tree reference needs Spec link")
                associations.setdefault(case, set()).update(f"{name}#{sid.lower()}" for sid in refs)
            for sid in refs:
                if sid not in specs:
                    errors.append(f"{name}: dangling Spec {sid}")
                if ids:
                    used.add(sid)
        branches = [line for line in tree.splitlines() if line.strip()]
        for index, line in enumerate(branches):
            depth = len(line) - len(line.lstrip())
            next_depth = len(branches[index + 1]) - len(branches[index + 1].lstrip()) if index + 1 < len(branches) else -1
            if next_depth > depth:
                continue
            if not tree_case_ids(line, local) and not re.search(r"\[(pending|unanalysed|not_applicable)\]", line):
                errors.append(f"{name}: unexplained leaf branch: {line.strip()}")
        for case, count in primary.items():
            if count != 1:
                errors.append(f"{case}: expected one primary tree position, found {count}")
        for sid, body in specs.items():
            if re.search(rf"(?m)^{ITEM}Testing: required\s*$", body) and sid not in used:
                errors.append(f"{name}#{sid}: tested rule has no Case")
        # Reader-first lead: a reviewer must learn the purpose and every open decision up front.
        if section(text, "导读") is None:
            warnings.append(f"{name}: no 导读 section; state purpose, visible change, main risk and "
                            "what is untested before the Cases")
        decide = section(text, "需要你决定")
        if pending and decide is None:
            warnings.append(f"{name}: collect pending Cases under 需要你决定: {', '.join(pending)}")
        for case in pending if decide is not None else []:
            if not re.search(rf"\b{re.escape(case)}\b", decide):
                errors.append(f"{case}: pending decision is missing from 需要你决定")
        cases.update(local)
    return {"schema_version": "2.0", "cases": cases, "spec_refs": {k: sorted(v) for k, v in associations.items()},
            "all_spec_refs": sorted(all_spec_refs),
            "design_fingerprint": design_hash(root, [p.relative_to(root).as_posix() for p in files]),
            "errors": errors, "warnings": warnings, "needs_decision": decisions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--review", action="append", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = check_design(args.root.resolve(), args.review)
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else
          "\n".join([f"cases: {len(result['cases'])}", *result["errors"],
                     *(f"warning: {item}" for item in result["warnings"]), *result["needs_decision"]]) or "ok")
    return int(bool(result["errors"]))


if __name__ == "__main__":
    raise SystemExit(main())
