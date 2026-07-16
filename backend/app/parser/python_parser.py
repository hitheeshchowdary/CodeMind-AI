import ast
from pathlib import Path


def parse_python_file(file_path: Path):

    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    tree = ast.parse(source_code)

    functions = []
    classes = []
    imports = []

    for node in ast.walk(tree):

        # Normal functions
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)

        # Async functions (FastAPI endpoints)
        elif isinstance(node, ast.AsyncFunctionDef):
            functions.append(node.name)

        # Classes
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

        # import os
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        # from pathlib import Path
        elif isinstance(node, ast.ImportFrom):

            module = node.module or ""

            for alias in node.names:

                imports.append(f"{module}.{alias.name}")

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports
    }