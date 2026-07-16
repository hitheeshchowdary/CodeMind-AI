from pathlib import Path

from app.parser.python_parser import parse_python_file

functions = parse_python_file(Path("test.py"))

print(functions)