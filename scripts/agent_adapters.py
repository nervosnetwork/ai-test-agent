#!/usr/bin/env python3
"""Fresh CLI review calls; bounded transport checks are not permission isolation."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

from workflow_lib import digest, read_json, validate_schema, write_json, run_bounded


def probe(backend: str) -> dict:
    executable = shutil.which(backend)
    if not executable:
        raise ValueError(f"B backend unavailable: {backend}")
    commands = [executable, "exec", "--help"] if backend == "codex" else [executable, "--help"]
    help_result = subprocess.run(commands, text=True, capture_output=True, timeout=15)
    version = subprocess.run([executable, "--version"], text=True, capture_output=True, timeout=15)
    required = {"codex": ["--ephemeral", "--sandbox", "--output-schema", "--output-last-message", "--ignore-user-config"],
                "claude": ["--no-session-persistence", "--json-schema", "--permission-mode", "--tools", "--safe-mode", "--strict-mcp-config"]}[backend]
    if help_result.returncode or version.returncode or any(flag not in help_result.stdout for flag in required):
        raise ValueError(f"{backend}: deployed CLI lacks required options")
    return {"backend": backend, "executable": executable, "version": version.stdout.strip(),
            "help_sha256": digest(help_result.stdout.encode()), "contract_tested": False,
            "isolation": "isolation_unverified", "shared_workspace": True,
            "persistent_memory": "unverified", "project_instructions": "may be injected"}


def command(backend: str, executable: str, root: Path, schema: Path, output: Path) -> list[str]:
    if backend == "codex":
        return [executable, "exec", "--ephemeral", "--ignore-user-config", "--sandbox", "read-only",
                "--skip-git-repo-check", "--cd", str(root), "--output-schema", str(schema),
                "--output-last-message", str(output), "-"]
    if backend == "claude":
        return [executable, "--print", "--safe-mode", "--no-session-persistence", "--permission-mode", "dontAsk",
                "--tools", "Read,Grep,Glob", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
                "--output-format", "json", "--json-schema", schema.read_text(encoding="utf-8")]
    raise ValueError("supported backends: codex, claude")


def invoke(backend: str, root: Path, schema: Path, prompt: str, timeout: int, output: Path) -> tuple[dict, dict]:
    metadata = probe(backend)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Never resume/fork A and never forward its history, environment prompt, or self-evaluation.
    with tempfile.TemporaryDirectory(prefix="ai-test-b-") as folder:
        result_path = Path(folder) / "response.json"
        argv = command(backend, metadata["executable"], root, schema, result_path)
        started = time.monotonic()
        try:
            run = run_bounded(argv, cwd=root, input=prompt, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            output.with_suffix('.log').write_text((error.output or '') + '\n' + (error.stderr or '') + '\nTIMEOUT', encoding='utf-8')
            raise
        metadata.update({"command": argv, "duration_seconds": round(time.monotonic() - started, 3),
                         "exit_code": run.returncode, "session": "fresh-" + uuid.uuid4().hex,
                         "model": "unavailable", "tokens": "unavailable", "cost": "unavailable"})
        output.with_suffix(".log").write_text(run.stdout + "\n" + run.stderr, encoding="utf-8")
        if run.returncode:
            raise ValueError(f"{backend} review failed: exit {run.returncode}; see {output.with_suffix('.log')}")
        if backend == "codex":
            value = read_json(result_path)
        else:
            outer = json.loads(run.stdout)
            if outer.get("is_error"):
                raise ValueError("Claude returned is_error")
            value = outer.get("structured_output")
            if value is None:
                value = json.loads(outer["result"])
            metadata["tokens"] = outer.get("usage", "unavailable")
            metadata["cost"] = outer.get("total_cost_usd", "unavailable")
        validate_schema(value, read_json(schema))
        write_json(output, value)
        return value, metadata


def contract(backend: str, output: Path, timeout=120):
    """A private canary is never put in the fresh B packet. Check the tested launch path."""
    with tempfile.TemporaryDirectory(prefix="ai-test-contract-") as folder:
        root = Path(folder)
        visible, private = uuid.uuid4().hex, uuid.uuid4().hex
        schema = {"type": "object", "properties": {"visible": {"type": "string"}, "private": {"type": "string"}},
                  "required": ["visible", "private"], "additionalProperties": False}
        write_json(root / "schema.json", schema)
        value, metadata = invoke(backend, root, root / "schema.json",
            f"Transport contract test. Return visible={visible!r}, private='unavailable'. No tools or extra context needed.",
            timeout, output.with_name(output.stem + '-response.json'))
        if value != {"visible": visible, "private": "unavailable"} or private in json.dumps(value):
            raise ValueError("fresh-session canary contract failed")
        metadata.update({"contract_tested": True, "isolation": "contract_tested",
                         "limits": "Tests explicit packet and fresh CLI launch only; hidden host state and same-user writes remain unverified."})
        write_json(output, metadata)
        return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["probe", "contract"])
    parser.add_argument("--backend", choices=["codex", "claude"], required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    try:
        if args.operation == "contract" and not args.output:
            raise ValueError("contract requires --output")
        result = contract(args.backend, args.output, args.timeout) if args.operation == "contract" else probe(args.backend)
        if args.output:
            write_json(args.output, result)
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        parser.exit(1, f"{error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
