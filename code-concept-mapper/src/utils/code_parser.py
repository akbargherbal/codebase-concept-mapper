import ast
import sys
from typing import Optional, Tuple

# Version check
if sys.version_info < (3, 8):
    print("❌ ERROR: This tool requires Python 3.8+ (for AST end_lineno support)", file=sys.stderr)
    sys.exit(1)

class ASTLocator(ast.NodeVisitor):
    """A node visitor to find a specific class or function definition."""
    def __init__(self, target_name: str):
        self.target_name = target_name
        self.found_node: Optional[ast.AST] = None

    def visit_ClassDef(self, node: ast.ClassDef):
        if node.name == self.target_name:
            self.found_node = node
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name == self.target_name:
            self.found_node = node
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        if node.name == self.target_name:
            self.found_node = node
        self.generic_visit(node)

def find_lines_by_identifier(file_path: str, identifier: str) -> Tuple[Optional[int], Optional[int]]:
    """Parses a Python file to find the start and end lines of a class or function."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=file_path)
        locator = ASTLocator(identifier)
        locator.visit(tree)

        if locator.found_node:
            start = locator.found_node.lineno
            end = getattr(locator.found_node, "end_lineno", None)
            return start, end
        return None, None
    except SyntaxError as e:
        print(f"❌ Syntax Error in {file_path}:{e.lineno}: {e.msg}", file=sys.stderr)
        return None, None
    except Exception as e:
        print(f"⚠️  AST Parse Error in {file_path}: {e}", file=sys.stderr)
        return None, None

def extract_snippet(file_path: str, start_line: int, end_line: Optional[int]) -> Optional[str]:
    """Reads specific lines from a file to create a code snippet."""
    if end_line is None:
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)
        return "".join(lines[start_idx:end_idx])
    except Exception as e:
        print(f"❌ Failed to read {file_path}: {e}", file=sys.stderr)
        return None