"""Idempotent Python-only managed comments with token and AST verification."""
from __future__ import annotations

import ast
import io
import re
import tokenize
from pathlib import Path

MARKER = re.compile(r"^(?P<indent>\s*)# TEST-EVIDENCE-(?P<kind>BEGIN|END): (?P<case>[A-Z][A-Z0-9-]*-\d{2,})\s*$")


def symbols(text: str):
    result = {}
    def walk(node, prefix=""):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = prefix + child.name
                result[name] = child
                walk(child, name + ".")
    walk(ast.parse(text))
    return result


def managed_ranges(text: str):
    lines = text.splitlines(keepends=True)
    comments = {t.start[0] for t in tokenize.generate_tokens(io.StringIO(text).readline) if t.type == tokenize.COMMENT}
    found, start, case = [], None, None
    for number, line in enumerate(lines, 1):
        match = MARKER.match(line)
        if not match or number not in comments:
            continue
        if match["kind"] == "BEGIN":
            if start is not None:
                raise ValueError("nested evidence block")
            start, case = number, match["case"]
        else:
            if start is None or case != match["case"]:
                raise ValueError("unmatched evidence block")
            for n in range(start, number + 1):
                if n not in comments or not lines[n - 1].lstrip().startswith("#"):
                    raise ValueError("managed block contains executable or blank lines")
                if n not in {start, number} and not lines[n - 1].lstrip().startswith("# Evidence | "):
                    raise ValueError("unmanaged/tool directive inside evidence block")
            found.append((start, number, case))
            start, case = None, None
    if start is not None:
        raise ValueError("unterminated evidence block")
    return found


def strip_managed(text: str) -> str:
    removed = {n for start, end, _ in managed_ranges(text) for n in range(start, end + 1)}
    return "".join(line for n, line in enumerate(text.splitlines(keepends=True), 1) if n not in removed)


def verify_comments_only(before: str, after: str):
    if strip_managed(before) != strip_managed(after):
        raise ValueError("change extends outside managed evidence comments")
    if ast.dump(ast.parse(before), include_attributes=False) != ast.dump(ast.parse(after), include_attributes=False):
        raise ValueError("Python AST changed")
    def tokens(value):
        return [(t.type, t.string) for t in tokenize.generate_tokens(io.StringIO(value).readline)
                if t.type not in {tokenize.COMMENT, tokenize.NL}]
    if tokens(before) != tokens(after):
        raise ValueError("Python token stream changed")


def annotation_lines(case: dict, binding: dict, indent: str) -> str:
    facts = [f"Case: {case['case_id']} ({case['coverage']})", f"Setup: {binding['setup']}",
             f"Trigger: {binding['trigger']}", f"Observe: {binding['observation']}",
             *[f"Assert: {a['text']}" for a in binding['assertions']],
             *[f"Gap: {m}" for m in binding['missing']], *[f"Limit: {m}" for m in case['limitations']]]
    lines = [f"# TEST-EVIDENCE-BEGIN: {case['case_id']}"]
    # The fixed prefix prevents suggested text becoming a tool directive or code.
    for fact in facts:
        lines.extend("# Evidence | " + line for line in fact.splitlines())
    lines.append(f"# TEST-EVIDENCE-END: {case['case_id']}")
    return "".join(indent + line + "\n" for line in lines)


def render_python(before: str, entries: list[tuple[dict, dict]]) -> str:
    selected = {case['case_id'] for case, _ in entries}
    ranges = managed_ranges(before)
    removed = {n for start, end, case in ranges if case in selected for n in range(start, end + 1)}
    clean = "".join(line for n, line in enumerate(before.splitlines(keepends=True), 1) if n not in removed)
    nodes, inserts = symbols(clean), {}
    lines = clean.splitlines(keepends=True)
    seen = set()
    for case, binding in entries:
        symbol = binding['symbol']
        if (case['case_id'], symbol) in seen:
            continue
        seen.add((case['case_id'], symbol))
        node = nodes.get(symbol)
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            raise ValueError(f"Python test function not found: {symbol}")
        number = min([node.lineno, *[d.lineno for d in node.decorator_list]])
        indent = re.match(r"\s*", lines[number - 1])[0]
        inserts.setdefault(number, []).append(annotation_lines(case, binding, indent))
    after = "".join("".join(inserts.get(n, [])) + line for n, line in enumerate(lines, 1))
    verify_comments_only(before, after)
    return after
