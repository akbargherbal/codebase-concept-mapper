"""
Phase 1: Improved Concept Validators
Content-based validation for 20 programming concepts with stricter checks
"""
import re
from typing import Dict, List, Optional


class ConceptValidator:
    """Validates if code content actually implements a concept"""
    
    def __init__(self, 
                 must_contain_any: List[str],
                 must_not_contain: List[str],
                 min_occurrences: int = 1,
                 regex_pattern: Optional[str] = None,
                 context_check: Optional[callable] = None):
        self.must_contain_any = must_contain_any
        self.must_not_contain = must_not_contain
        self.min_occurrences = min_occurrences
        self.regex_pattern = regex_pattern
        self.context_check = context_check
    
    def validate(self, content: str) -> bool:
        """Check if content implements the concept"""
        content_lower = content.lower()
        
        # Check must_contain_any (at least min_occurrences matches)
        matches = sum(
            1 for keyword in self.must_contain_any
            if keyword.lower() in content_lower
        )
        
        if matches < self.min_occurrences:
            return False
        
        # Check must_not_contain (language/syntax detection)
        for anti in self.must_not_contain:
            if anti in content:
                return False
        
        # Optional: regex pattern validation
        if self.regex_pattern:
            if not re.search(self.regex_pattern, content, re.MULTILINE | re.DOTALL):
                return False
        
        # Optional: custom context check
        if self.context_check:
            if not self.context_check(content):
                return False
        
        return True


def check_closure_structure(content: str) -> bool:
    """Check for actual closure pattern (nested function returning function)"""
    # Look for function definitions that return other functions
    patterns = [
        r'function\s+\w+\([^)]*\)\s*{[^}]*return\s+function',
        r'const\s+\w+\s*=\s*\([^)]*\)\s*=>\s*{[^}]*return\s+\(',
        r'function\s+\w+\([^)]*\)\s*{[^}]*return\s*\(',
    ]
    return any(re.search(p, content, re.DOTALL) for p in patterns)


def check_list_comprehension(content: str) -> bool:
    """Check for actual list comprehension syntax"""
    # Python list comprehension: [x for x in iterable]
    pattern = r'\[[^\]]+\s+for\s+\w+\s+in\s+[^\]]+\]'
    return bool(re.search(pattern, content))


# ============================================================================
# PYTHON CONCEPTS (10)
# ============================================================================

PYTHON_VALIDATORS = {
    "context managers python": ConceptValidator(
        must_contain_any=["__enter__", "__exit__", "with ", "@contextmanager"],
        must_not_contain=["function(", "const ", "=>", "function*", "async function"],
        min_occurrences=2  # Need both __enter__ and __exit__, or with statement
    ),
    
    "async await python": ConceptValidator(
        must_contain_any=["async def", "await ", "asyncio"],
        must_not_contain=["Promise", "async function", "function async", ".then("],
        min_occurrences=2  # Need both async def and await
    ),
    
    "decorators python": ConceptValidator(
        must_contain_any=["@", "functools.wraps", "@property", "@staticmethod", "@classmethod"],
        must_not_contain=["@interface", "@component", "@Injectable", "@Decorator("],
        min_occurrences=1,
        regex_pattern=r'@\w+\s*\n\s*def\s+\w+'  # @ followed by function def
    ),
    
    "list comprehensions python": ConceptValidator(
        must_contain_any=["[", "for ", " in ", "]"],
        must_not_contain=[".map(", ".filter(", "=>", "Array.from"],
        min_occurrences=3,  # Need [, for, in
        context_check=check_list_comprehension
    ),
    
    "exception handling python": ConceptValidator(
        must_contain_any=["try:", "except ", "finally:", "raise ", "Exception"],
        must_not_contain=["catch", "throw new", "} catch", "catch("],
        min_occurrences=2  # Need try + except/finally/raise
    ),
    
    "generators python": ConceptValidator(
        must_contain_any=["yield ", "def ", "next(", "__next__"],
        must_not_contain=["function*", "yield*", "function yield", "async function*"],
        min_occurrences=2,  # Need def and yield
        regex_pattern=r'def\s+\w+[^:]*:[^}]*yield\s+'
    ),
    
    "class inheritance python": ConceptValidator(
        must_contain_any=["class ", "super(", "__init__", "self"],
        must_not_contain=["extends ", "class {", "constructor(", "this."],
        min_occurrences=2  # Need class and super/init
    ),
    
    "file handling python": ConceptValidator(
        must_contain_any=["open(", "with open", ".read(", ".write(", ".close("],
        must_not_contain=["fs.readFile", "require('fs')", "fs.writeFile", "readFileSync"],
        min_occurrences=1
    ),
    
    "lambda functions python": ConceptValidator(
        must_contain_any=["lambda ", "lambda:", "map(", "filter("],
        must_not_contain=["=>", "function(", "const ", "var "],
        min_occurrences=1,
        regex_pattern=r'lambda\s+\w+\s*:'
    ),
    
    "dataclasses python": ConceptValidator(
        must_contain_any=["@dataclass", "from dataclasses", "dataclass("],
        must_not_contain=["interface ", "type ", "class {", "@Entity"],
        min_occurrences=1,
        regex_pattern=r'@dataclass\s*\n\s*class\s+\w+'
    )
}

# ============================================================================
# JAVASCRIPT CONCEPTS (10)
# ============================================================================

JAVASCRIPT_VALIDATORS = {
    "promises javascript": ConceptValidator(
        must_contain_any=["new Promise(", ".then(", ".catch(", "Promise.all", "resolve(", "reject("],
        must_not_contain=["async def", "await asyncio", "asyncio.", "import asyncio"],
        min_occurrences=2  # Need Promise and then/catch/all
    ),
    
    "async await javascript": ConceptValidator(
        must_contain_any=["async function", "async (", "await ", "async "],
        must_not_contain=["async def", "asyncio", "import asyncio", "asyncio."],
        min_occurrences=2,  # Need async and await
        regex_pattern=r'async\s+(function|\(|[\w]+\s*=>)'
    ),
    
    "react hooks": ConceptValidator(
        must_contain_any=["useState", "useEffect", "useContext", "useReducer", "useMemo", "useCallback", "useRef"],
        must_not_contain=["@hook", "def use", "class Component", "import { Component }"],
        min_occurrences=1,
        regex_pattern=r'(const|let|var)\s*\[[^\]]+\]\s*=\s*useState|useEffect\s*\('
    ),
    
    "closures javascript": ConceptValidator(
        must_contain_any=["function", "return function", "=>", "return ("],
        must_not_contain=["def ", "lambda", "yield"],
        min_occurrences=2,
        context_check=check_closure_structure
    ),
    
    "arrow functions javascript": ConceptValidator(
        must_contain_any=["=>"],
        must_not_contain=["lambda", "def ", "yield", "=>:"],
        min_occurrences=1,
        regex_pattern=r'\([^)]*\)\s*=>'
    ),
    
    "destructuring javascript": ConceptValidator(
        must_contain_any=["const {", "let {", "const [", "let [", "..."],
        must_not_contain=["def ", "import ", "from dataclasses"],
        min_occurrences=1,
        regex_pattern=r'(const|let|var)\s*(\{[^}]+\}|\[[^\]]+\])\s*='
    ),
    
    "event handling javascript": ConceptValidator(
        must_contain_any=["addEventListener", "onClick", "onSubmit", ".on(", "onChange", "onLoad"],
        must_not_contain=["def on_", "@event", "def handle", "self.on_"],
        min_occurrences=1
    ),
    
    "callbacks javascript": ConceptValidator(
        must_contain_any=["callback", "(err, ", "(error,", "function("],
        must_not_contain=["def callback", "lambda", "yield"],
        min_occurrences=1,
        regex_pattern=r'function\s*\([^)]*callback[^)]*\)|callback\s*\('
    ),
    
    "array methods javascript": ConceptValidator(
        must_contain_any=[".map(", ".filter(", ".reduce(", ".forEach(", ".find(", ".some("],
        must_not_contain=["[x for x in", "list(map", "map(lambda"],
        min_occurrences=1,
        regex_pattern=r'\.(map|filter|reduce|forEach|find|some)\s*\('
    ),
    
    "classes javascript": ConceptValidator(
        must_contain_any=["class ", "constructor(", "extends ", "super("],
        must_not_contain=["class :", "def __init__", "__init__(self", "self."],
        min_occurrences=2,  # Need class and constructor/extends
        regex_pattern=r'class\s+\w+\s*(extends\s+\w+)?\s*\{'
    )
}

# ============================================================================
# COMBINED VALIDATORS
# ============================================================================

ALL_VALIDATORS = {
    **PYTHON_VALIDATORS,
    **JAVASCRIPT_VALIDATORS
}


def validate_file_for_concept(filepath: str, content: str, concept: str) -> bool:
    """
    Validate if a file implements a given concept
    
    Args:
        filepath: Path to file (for debugging/logging)
        content: File content as string
        concept: Concept query string (must match validator key)
    
    Returns:
        bool: True if file implements the concept
    """
    if concept not in ALL_VALIDATORS:
        raise ValueError(f"Unknown concept: {concept}. Available: {list(ALL_VALIDATORS.keys())}")
    
    validator = ALL_VALIDATORS[concept]
    return validator.validate(content)


def get_all_concepts() -> List[str]:
    """Get list of all testable concepts"""
    return list(ALL_VALIDATORS.keys())


def get_concepts_by_language(language: str) -> List[str]:
    """Get concepts for a specific language"""
    if language.lower() == "python":
        return list(PYTHON_VALIDATORS.keys())
    elif language.lower() in ["javascript", "js"]:
        return list(JAVASCRIPT_VALIDATORS.keys())
    else:
        raise ValueError(f"Unknown language: {language}")


# ============================================================================
# TESTING UTILITIES
# ============================================================================

def test_validator_on_sample():
    """Quick test to ensure validators work correctly"""
    
    # Python async sample
    python_async_code = """
import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    return "data"

async def main():
    result = await fetch_data()
    print(result)
"""
    
    # JavaScript promise sample
    js_promise_code = """
function fetchData() {
    return new Promise((resolve, reject) => {
        setTimeout(() => resolve('data'), 1000);
    }).then(data => {
        console.log(data);
    }).catch(error => {
        console.error(error);
    });
}
"""
    
    # Python list comprehension
    python_list_comp = """
numbers = [1, 2, 3, 4, 5]
squares = [x**2 for x in numbers if x % 2 == 0]
"""
    
    tests = [
        ("async await python", python_async_code, True),
        ("async await javascript", python_async_code, False),
        ("promises javascript", js_promise_code, True),
        ("async await python", js_promise_code, False),
        ("list comprehensions python", python_list_comp, True),
    ]
    
    print("Testing concept validators...")
    all_passed = True
    
    for concept, code, expected in tests:
        result = validate_file_for_concept("test.py", code, concept)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_passed = False
        print(f"{status} {concept}: {result} (expected: {expected})")
    
    if all_passed:
        print("\n✓ All validator tests passed!")
    else:
        print("\n✗ Some validator tests failed!")
    
    return all_passed


if __name__ == "__main__":
    test_validator_on_sample()
    print(f"\nTotal concepts available: {len(ALL_VALIDATORS)}")
    print(f"Python concepts: {len(PYTHON_VALIDATORS)}")
    print(f"JavaScript concepts: {len(JAVASCRIPT_VALIDATORS)}")