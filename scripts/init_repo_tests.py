#!/usr/bin/env python3
"""Create an additive standalone test project with reviewer-first case documents."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SUITE_PRESETS = {
    "integration": {
        "label": "Integration",
        "focus": "service lifecycle, cross-component flows, external interfaces, and end-to-end outcomes",
        "code_dirs": {
            "tests": "Integration tests containing TEST-MAP comments.",
            "config": "Suite-owned configuration templates and environment examples.",
        },
    },
    "p2p": {
        "label": "P2P",
        "focus": "node topology, peer lifecycle, protocol interaction, network faults, and peer-visible outcomes",
        "code_dirs": {
            "tests": "P2P tests containing TEST-MAP comments.",
            "topologies": "Reusable topology descriptions owned by this suite.",
        },
    },
    "performance": {
        "label": "Performance",
        "focus": "repeatable workloads, explicit metrics, thresholds, resource limits, and comparable conditions",
        "code_dirs": {
            "benchmarks": "Performance benchmarks containing TEST-MAP comments.",
            "workloads": "Versioned workload definitions used by benchmarks.",
        },
    },
    "fuzz": {
        "label": "Fuzz",
        "focus": "clear fuzz targets, input boundaries, crash detection, and deterministic reproduction",
        "code_dirs": {
            "targets": "Fuzz targets containing TEST-MAP comments.",
            "corpus": "Seed inputs required by the selected fuzz runner.",
        },
    },
}


def project_slug(value: str) -> str:
    """Return a portable directory name while retaining Unicode letters."""
    slug = re.sub(r"[\s/\\]+", "-", value.strip().lower())
    slug = re.sub(r"[^\w.-]+", "-", slug, flags=re.UNICODE)
    slug = re.sub(r"-+", "-", slug).strip("-.")
    if not slug or slug in {".", ".."}:
        raise ValueError("name must contain a usable directory name")
    return slug


def suite_spec(value: str) -> tuple[str, dict[str, object]]:
    suite = project_slug(value)
    preset = SUITE_PRESETS.get(suite)
    if preset is not None:
        return suite, preset
    label = " ".join(part.capitalize() for part in re.split(r"[-_.]+", suite) if part)
    return suite, {
        "label": label,
        "focus": f"target-specific {label} behavior selected during target analysis",
        "code_dirs": {"tests": f"{label} tests containing TEST-MAP comments."},
    }


def render(value: str, replacements: dict[str, str]) -> str:
    for key, replacement in replacements.items():
        value = value.replace("{{" + key + "}}", replacement)
    return value


def write_file(
    path: Path,
    content: str,
    *,
    force: bool,
    created: list[Path],
    replaced: list[Path],
    skipped: list[Path],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        skipped.append(path)
        return
    existed = path.exists()
    path.write_text(content, encoding="utf-8")
    (replaced if existed else created).append(path)


def render_tree(
    source_root: Path,
    output_root: Path,
    replacements: dict[str, str],
    *,
    force: bool,
    created: list[Path],
    replaced: list[Path],
    skipped: list[Path],
) -> None:
    for source in sorted(source_root.rglob("*")):
        if not source.is_file():
            continue
        relative = Path(render(source.relative_to(source_root).as_posix(), replacements))
        content = render(source.read_text(encoding="utf-8"), replacements)
        write_file(
            output_root / relative,
            content,
            force=force,
            created=created,
            replaced=replaced,
            skipped=skipped,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a standalone test project with reviewer-first cases and TEST-MAP automation."
    )
    parser.add_argument("--project", required=True, help="Project display name")
    parser.add_argument(
        "--source-repo",
        required=True,
        help="Product source repository URL or stable relative path",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Destination directory (default: ./<project-slug>-tests)",
    )
    parser.add_argument(
        "--suites",
        nargs="+",
        required=True,
        metavar="SUITE",
        help="Analyzed runner or assurance approaches; accepts preset or custom names",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace generated files that already exist",
    )
    return parser.parse_args()


def readme_for_directory(label: str, directory: str, purpose: str) -> str:
    return (
        f"# {label} {directory}\n\n"
        f"{purpose}\n\n"
        "Map automated behavior with a nearby `TEST-MAP: <CASE-ID>` comment.\n"
    )


def fixtures_readme(label: str) -> str:
    return (
        f"# {label} Fixtures\n\n"
        "Keep only reusable inputs shared by multiple tests. Prefer inline setup for one-off data.\n"
    )


def main() -> int:
    args = parse_args()
    try:
        project_id = project_slug(args.project)
    except ValueError as error:
        raise SystemExit(f"invalid --project: {error}") from error
    source_repo = args.source_repo.strip()
    if not source_repo:
        raise SystemExit("invalid --source-repo: value must not be empty")

    suite_specs: list[tuple[str, dict[str, object]]] = []
    selected: set[str] = set()
    for value in args.suites:
        try:
            suite, metadata = suite_spec(value)
        except ValueError as error:
            raise SystemExit(f"invalid --suites value {value!r}: {error}") from error
        if suite not in selected:
            selected.add(suite)
            suite_specs.append((suite, metadata))

    output = args.output.expanduser() if args.output is not None else Path(f"{project_id}-tests")
    if output.exists() and not output.is_dir():
        raise SystemExit(f"output exists and is not a directory: {output}")

    skill_root = Path(__file__).resolve().parent.parent
    asset_root = skill_root / "assets" / "repo-tests"
    root_template = asset_root / "root"
    suite_template = asset_root / "suite"
    review_template = skill_root / "templates" / "test-review.md"
    mapping_checker = skill_root / "scripts" / "check_test_map.py"
    required = [root_template, suite_template, review_template, mapping_checker]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"required skill assets are missing: {', '.join(missing)}")

    single_suite = len(suite_specs) == 1
    if single_suite:
        suite, metadata = suite_specs[0]
        code_dirs = metadata["code_dirs"]
        layout = (
            f"A single {metadata['label']} approach uses root `reviews/`, "
            f"{', '.join(f'`{name}/`' for name in code_dirs)}, and `fixtures/`."
        )
        suite_list = (
            f"- Root review and execution scope: {metadata['label']} — {metadata['focus']}."
        )
        review_locations = "- `reviews/<area>/<interface-or-behavior>.md`"
        commands = (
            "Replace after target integration:\n\n"
            "```text\nSetup: pending target integration\nRun: pending target integration\n"
            "Focused run: pending target integration\n```"
        )
    else:
        layout = "Independent runners and assurance approaches live under `suites/<suite>/`."
        suite_list = "\n".join(
            f"- `suites/{suite}/`: {metadata['label']} — {metadata['focus']}."
            for suite, metadata in suite_specs
        )
        review_locations = "\n".join(
            f"- `suites/{suite}/reviews/<area>/<interface-or-behavior>.md`"
            for suite, _ in suite_specs
        )
        commands = "Setup and run commands live in each suite README."

    common = {
        "PROJECT_NAME": args.project.strip(),
        "PROJECT_SLUG": project_id,
        "SOURCE_REPOSITORY": source_repo,
        "SUITE_TYPES": ", ".join(f"`{suite}`" for suite, _ in suite_specs),
        "SUITE_LIST": suite_list,
        "TEST_LAYOUT_DESCRIPTION": layout,
        "REVIEW_LOCATIONS": review_locations,
        "COMMANDS_BLOCK": commands,
    }
    created: list[Path] = []
    replaced: list[Path] = []
    skipped: list[Path] = []

    render_tree(
        root_template,
        output,
        common,
        force=args.force,
        created=created,
        replaced=replaced,
        skipped=skipped,
    )
    write_file(
        output / "templates" / "test-review.md",
        review_template.read_text(encoding="utf-8"),
        force=args.force,
        created=created,
        replaced=replaced,
        skipped=skipped,
    )
    checker_output = output / "scripts" / "check_test_map.py"
    write_file(
        checker_output,
        mapping_checker.read_text(encoding="utf-8"),
        force=args.force,
        created=created,
        replaced=replaced,
        skipped=skipped,
    )
    checker_output.chmod(0o755)

    if single_suite:
        _, metadata = suite_specs[0]
        write_file(
            output / "fixtures" / "README.md",
            fixtures_readme(metadata["label"]),
            force=args.force,
            created=created,
            replaced=replaced,
            skipped=skipped,
        )
        for directory, purpose in metadata["code_dirs"].items():
            write_file(
                output / directory / "README.md",
                readme_for_directory(metadata["label"], directory, purpose),
                force=args.force,
                created=created,
                replaced=replaced,
                skipped=skipped,
            )
    else:
        for suite, metadata in suite_specs:
            code_dirs = metadata["code_dirs"]
            replacements = {
                **common,
                "SUITE_TYPE": suite,
                "SUITE_LABEL": metadata["label"],
                "SUITE_FOCUS": metadata["focus"],
                "CODE_DIRS": ", ".join(f"`{name}/`" for name in code_dirs),
            }
            suite_output = output / "suites" / suite
            render_tree(
                suite_template,
                suite_output,
                replacements,
                force=args.force,
                created=created,
                replaced=replaced,
                skipped=skipped,
            )
            write_file(
                suite_output / "fixtures" / "README.md",
                fixtures_readme(metadata["label"]),
                force=args.force,
                created=created,
                replaced=replaced,
                skipped=skipped,
            )
            for directory, purpose in code_dirs.items():
                write_file(
                    suite_output / directory / "README.md",
                    readme_for_directory(metadata["label"], directory, purpose),
                    force=args.force,
                    created=created,
                    replaced=replaced,
                    skipped=skipped,
                )

    print(f"test-project: {output.resolve()}")
    print(f"layout: {'single-suite' if single_suite else 'multi-suite'}")
    print(f"created: {len(created)}")
    print(f"replaced: {len(replaced)}")
    print(f"preserved: {len(skipped)}")
    for path in created:
        print(f"+ {path}")
    for path in replaced:
        print(f"~ {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
