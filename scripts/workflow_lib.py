"""Small shared v2 primitives; no model judgments or external dependencies."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

from check_test_map import review_rows

VERSION = "2.0"


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def fingerprint(value) -> str:
    return digest(json.dumps(value, sort_keys=True, ensure_ascii=False).encode())


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def inside(root: Path, name: str, *, exists=True) -> Path:
    path = root / name
    if Path(name).is_absolute() or ".." in Path(name).parts:
        raise ValueError(f"expected relative project path: {name}")
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"path escapes project: {name}")
    if exists and not path.is_file():
        raise ValueError(f"missing file: {name}")
    return path


def scope_paths(root: Path, scope: str):
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}", scope):
        raise ValueError("scope must be a portable 1-80 character slug")
    state = inside(root, f".ai-test-agent/current/{scope}/state.json", exists=False)
    report = inside(root, f"reports/{scope}/coverage.json", exists=False).parent
    return state, report


def design_text(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    for number, _, _ in review_rows(path):
        # Ignore only the mapping checkbox in actual case scenario cells.
        lines[number - 1] = re.sub(r"(\|\s*`?[A-Z][A-Z0-9-]*-\d{2,}`?\s*\|\s*-\s+)\[[ xX]\]", r"\1[ ]", lines[number - 1], count=1)
    return "".join(lines)


def design_hash(root: Path, reviews: list[str]) -> str:
    return fingerprint({name: design_text(inside(root, name)) for name in sorted(reviews)})


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if result.returncode:
        raise ValueError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def revision(root: Path) -> str:
    try:
        return git(root, "rev-parse", "HEAD")
    except ValueError:
        return "unavailable"


def snapshot(root: Path, files: list[str]) -> dict[str, str]:
    return {name: digest(inside(root, name).read_bytes()) for name in sorted(set(files))}


def validate_schema(value, schema: dict, at="$", document=None):
    """Validate the deliberately small JSON Schema subset used by bundled schemas."""
    document = document or schema
    if "$ref" in schema:
        target = document
        for segment in schema["$ref"].removeprefix("#/").split("/"):
            target = target[segment]
        return validate_schema(value, target, at, document)
    kinds = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool}
    kind = schema.get("type")
    if kind and (not isinstance(value, kinds[kind]) or kind == "integer" and isinstance(value, bool)):
        raise ValueError(f"{at}: expected {kind}")
    if "const" in schema and value != schema["const"]:
        raise ValueError(f"{at}: expected {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{at}: invalid value {value!r}")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                raise ValueError(f"{at}: missing {key}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False and set(value) - set(props):
            raise ValueError(f"{at}: unknown fields {sorted(set(value) - set(props))}")
        for key, item in value.items():
            child = props.get(key, schema.get("additionalProperties", {}))
            if isinstance(child, dict):
                validate_schema(item, child, f"{at}.{key}", document)
    elif isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            raise ValueError(f"{at}: too few items")
        if schema.get("uniqueItems") and len({fingerprint(v) for v in value}) != len(value):
            raise ValueError(f"{at}: duplicate items")
        for index, item in enumerate(value):
            validate_schema(item, schema.get("items", {}), f"{at}[{index}]", document)
    elif isinstance(value, str):
        if len(value.strip()) < schema.get("minLength", 0):
            raise ValueError(f"{at}: empty string")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            raise ValueError(f"{at}: invalid string")
    elif isinstance(value, int) and value < schema.get("minimum", value):
        raise ValueError(f"{at}: below minimum")


def product_state(root: Path, config: dict) -> dict:
    product = Path(config["root"])
    head = git(product, "rev-parse", "HEAD")
    # Bind tracked edits and nonignored untracked files, not only a branch label.
    dirty = subprocess.check_output(["git", "-C", str(product), "diff", "--binary", "HEAD"])
    names = subprocess.check_output(["git", "-C", str(product), "ls-files", "--others", "--exclude-standard", "-z"]).decode().split("\0")
    untracked = snapshot(product, [name for name in names if name])
    return {"head": head, "dirty": digest(dirty), "untracked": untracked,
            "base_tip": config["base_tip"], "diff_base": config["diff_base"]}


def implementation_files(root: Path, reviews: list[str], dependencies: list[str]) -> list[str]:
    """Conservative closure: all suite inputs plus explicitly declared root inputs."""
    files = set(reviews + dependencies)
    for folder in ("suites", "tests"):
        directory = root / folder
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if any(part in {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache"} for part in path.parts):
                continue
            if path.is_file():
                files.add(path.relative_to(root).as_posix())
    return sorted(files)


def freeze_inputs(root: Path, state: dict) -> dict:
    files = implementation_files(root, state["reviews"], state["dependencies"])
    result = {"files": snapshot(root, files), "product": product_state(root, state["product"]),
              "design": design_hash(root, state["reviews"]), "test_revision": revision(root),
              "command": state["command"], "cwd": state["cwd"], "required_cases": state["required_cases"],
              "scope": state["scope"], "schema_version": VERSION}
    result["fingerprint"] = fingerprint(result)
    return result


def fresh_inputs(root: Path, state: dict, frozen: dict) -> bool:
    return freeze_inputs(root, state) == frozen


def run_bounded(argv, *, timeout, input=None, capture_output=False, **kwargs):
    """Bound subprocess groups so timeout does not leave a child runner behind."""
    import os
    import signal
    if capture_output:
        kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if input is not None:
        kwargs['stdin'] = subprocess.PIPE
    process = subprocess.Popen(argv, start_new_session=os.name == 'posix', **kwargs)
    try:
        stdout, stderr = process.communicate(input, timeout=timeout)
    except subprocess.TimeoutExpired as error:
        if os.name == 'posix':
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        stdout, stderr = process.communicate()
        error.output, error.stderr = stdout, stderr
        raise
    return subprocess.CompletedProcess(argv, process.returncode, stdout, stderr)
