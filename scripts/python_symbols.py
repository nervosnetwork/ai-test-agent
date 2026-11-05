"""Locate named Python classes and functions for coverage evidence validation."""
from __future__ import annotations

import ast


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
