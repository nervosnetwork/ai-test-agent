#!/usr/bin/env python3
"""Report review-case mappings and validate scenario automation checkboxes."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


CASE_TOKEN = r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{2,}"
REVIEW_ROW = re.compile(
    rf"^\|\s*`?(?P<case>{CASE_TOKEN})`?\s*\|\s*(?P<scenario>[^|]*?)\s*\|"
)
TASK_CHECKBOX = re.compile(r"^-\s+\[(?P<state>[ xX])\]\s+")
TEST_MAP = re.compile(rf"\bTEST-MAP:\s*(?P<case>{CASE_TOKEN})\b")
CODE_DIR_NAMES = {"tests", "benchmarks", "targets"}
CODE_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".kts",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".swift",
    ".ts",
    ".tsx",
}
SKIP_DIRS = {".git", ".idea", ".pytest_cache", ".venv", "node_modules", "source", "__pycache__"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute automation coverage from review rows and TEST-MAP comments."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Test-project root (default: current directory)",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Exit non-zero when any review case has no TEST-MAP comment",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a machine-readable JSON report",
    )
    return parser.parse_args()


def is_skipped(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    return any(part in SKIP_DIRS for part in relative.parts)


def location(path: Path, line: int, root: Path) -> str:
    return f"{path.relative_to(root).as_posix()}:{line}"


def review_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        if is_skipped(path, root) or path.name.lower() == "readme.md":
            continue
        if "reviews" in path.relative_to(root).parts:
            files.append(path)
    return sorted(files)


def code_files(root: Path) -> list[Path]:
    files: set[Path] = set()
    for directory in root.rglob("*"):
        if not directory.is_dir() or directory.name not in CODE_DIR_NAMES:
            continue
        if is_skipped(directory, root):
            continue
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix.lower() in CODE_SUFFIXES and not is_skipped(path, root):
                files.add(path)
    return sorted(files)


def collect_review_cases(
    root: Path,
) -> tuple[dict[str, list[str]], dict[str, list[tuple[str, bool | None]]]]:
    found: dict[str, list[str]] = defaultdict(list)
    markers: dict[str, list[tuple[str, bool | None]]] = defaultdict(list)
    for path in review_files(root):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            match = REVIEW_ROW.match(line)
            if match:
                case = match.group("case")
                place = location(path, number, root)
                checkbox = TASK_CHECKBOX.match(match.group("scenario"))
                checked = None if checkbox is None else checkbox.group("state").lower() == "x"
                found[case].append(place)
                markers[case].append((place, checked))
    return dict(found), dict(markers)


def collect_test_maps(root: Path) -> dict[str, list[str]]:
    found: dict[str, list[str]] = defaultdict(list)
    for path in code_files(root):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, start=1):
            for match in TEST_MAP.finditer(line):
                found[match.group("case")].append(location(path, number, root))
    return dict(found)


def build_report(root: Path) -> dict[str, object]:
    reviews, markers = collect_review_cases(root)
    mappings = collect_test_maps(root)
    review_ids = set(reviews)
    mapped_ids = set(mappings)
    automated = sorted(review_ids & mapped_ids)
    unautomated = sorted(review_ids - mapped_ids)
    orphan = sorted(mapped_ids - review_ids)
    duplicate_reviews = {case: places for case, places in sorted(reviews.items()) if len(places) > 1}
    multiple_mappings = {case: places for case, places in sorted(mappings.items()) if len(places) > 1}
    missing_markers = {
        case: [place for place, checked in places if checked is None]
        for case, places in sorted(markers.items())
        if any(checked is None for _, checked in places)
    }
    marker_mismatches = {
        case: {
            "expected": "- [x]" if case in mapped_ids else "- [ ]",
            "locations": [
                place
                for place, checked in places
                if checked is not None and checked != (case in mapped_ids)
            ],
        }
        for case, places in sorted(markers.items())
        if any(
            checked is not None and checked != (case in mapped_ids)
            for _, checked in places
        )
    }
    return {
        "root": str(root),
        "review_case_count": len(review_ids),
        "automated_case_count": len(automated),
        "automation_coverage": f"{len(automated)}/{len(review_ids)}",
        "automated": automated,
        "unautomated": unautomated,
        "orphan_mappings": orphan,
        "duplicate_review_ids": duplicate_reviews,
        "multiple_code_mappings": multiple_mappings,
        "missing_automation_markers": missing_markers,
        "automation_marker_mismatches": marker_mismatches,
        "review_locations": reviews,
        "mapping_locations": mappings,
    }


def print_human(report: dict[str, object]) -> None:
    print(f"review cases: {report['review_case_count']}")
    print(f"automated cases: {report['automated_case_count']}")
    print(f"automation coverage: {report['automation_coverage']}")
    unautomated = report["unautomated"]
    orphan = report["orphan_mappings"]
    duplicate = report["duplicate_review_ids"]
    multiple = report["multiple_code_mappings"]
    missing_markers = report["missing_automation_markers"]
    marker_mismatches = report["automation_marker_mismatches"]
    print(f"unautomated: {', '.join(unautomated) if unautomated else 'none'}")
    print(f"orphan mappings: {', '.join(orphan) if orphan else 'none'}")
    print(f"duplicate review IDs: {', '.join(duplicate) if duplicate else 'none'}")
    print(f"cases with multiple code mappings: {', '.join(multiple) if multiple else 'none'}")
    print(
        "missing automation markers: "
        f"{', '.join(missing_markers) if missing_markers else 'none'}"
    )
    mismatch_text = ", ".join(
        f"{case} (expected {details['expected']})"
        for case, details in marker_mismatches.items()
    )
    print(f"automation marker mismatches: {mismatch_text or 'none'}")


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"test-project root is not a directory: {root}")
    report = build_report(root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_human(report)
    invalid = bool(
        report["orphan_mappings"]
        or report["duplicate_review_ids"]
        or report["missing_automation_markers"]
        or report["automation_marker_mismatches"]
    )
    incomplete = bool(args.require_complete and report["unautomated"])
    return 1 if invalid or incomplete else 0


if __name__ == "__main__":
    raise SystemExit(main())
