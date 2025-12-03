"""
Phase 1: Concept Validators
Content-based validation for 20 programming concepts
NO hard-coded filenames - validates actual code implementation
"""
import re
from typing import Dict, List, Optional


class ConceptValidator:
    """Validates if code content actually implements a concept"""
    
    def __init__(self, 
                 must_contain_any: List[str],
                 must_not_contain: List[str],
                 min_occurrences: int = 1,
                 regex_pattern: Optional[str] = None):
        self.must_contain_any = must_contain_any
        self.must_not_contain = must_not_contain
        self.min_occurrences = min_occurrences
        self.regex_pattern = regex_pattern
    
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
        if any(anti in content for anti in self.must_not_contain):
            return False
        
        # Optional: regex pattern validation
        if self.regex_pattern:
            if not re.search(self.regex_pattern, content, re.MULTILINE | re.DOTALL):
                return False
        
        return True


# ============================================================================
# PYTHON CONCEPTS (10)
# ============================================================================

PYTHON_VALIDATORS = {
    "context managers python": ConceptValidator(
        must_contain_any=["__enter__", "__exit__", "with ", "@contextmanager"],
        must_not_contain=["function(", "const ", "=>", "function*"],
        min_occurrences=1
    ),
    
    "async await python": ConceptValidator(
        must_contain_any=["async def", "await ", "asyncio"],
        must_not_contain=["Promise", "async function", "function async"],
        min_occurrences=2
    ),
    
    "decorators python": ConceptValidator(
        must_contain_any=["@", "def decorator", "functools.wraps", "@property"],
        must_not_contain=["@interface", "@component", "@Injectable"],
        min_occurrences=2
    ),
    
    "list comprehensions python": ConceptValidator(
        must_contain_any=["[", "for ", " in "],
        must_not_contain=[".map(", ".filter(", "=>"],
        min_occurrences=1,
        regex_pattern=r"\[.+\s+for\s+.+\s+in\s+.+\]"
    ),
    
    "exception handling python": ConceptValidator(
        must_contain_any=["try:", "except ", "finally:", "raise "],
        must_not_contain=["catch", "throw new", "} catch"],
        min_occurrences=2
    ),
    
    "generators python": ConceptValidator(
        must_contain_any=["yield ", "def ", "next("],
        must_not_contain=["function*", "yield*", "function yield"],
        min_occurrences=1
    ),
    
    "class inheritance python": ConceptValidator(
        must_contain_any=["class ", "super(", "__init__"],
        must_not_contain=["extends ", "class {", "constructor("],
        min_occurrences=2
    ),
    
    "file handling python": ConceptValidator(
        must_contain_any=["open(", "with open", ".read(", ".write(", "file"],
        must_not_contain=["fs.readFile", "require('fs')", "fs.writeFile"],
        min_occurrences=1
    ),
    
    "lambda functions python": ConceptValidator(
        must_contain_any=["lambda ", "map(", "filter("],
        must_not_contain=["=>", "function(", "const "],
        min_occurrences=1
    ),
    
    "dataclasses python": ConceptValidator(
        must_contain_any=["@dataclass", "from dataclasses", "dataclass"],
        must_not_contain=["interface ", "type ", "class {"],
        min_occurrences=1
    )
}

# ============================================================================
# JAVASCRIPT CONCEPTS (10)
# ============================================================================

JAVASCRIPT_VALIDATORS = {
    "promises javascript": ConceptValidator(
        must_contain_any=["new Promise(", ".then(", ".catch(", "Promise.all", "Promise."],
        must_not_contain=["async def", "await asyncio", "asyncio."],
        min_occurrences=2
    ),
    
    "async await javascript": ConceptValidator(
        must_contain_any=["async function", "async (", "await ", "async "],
        must_not_contain=["async def", "asyncio", "import asyncio"],
        min_occurrences=2
    ),
    
    "react hooks": ConceptValidator(
        must_contain_any=["useState", "useEffect", "useContext", "useReducer", "useMemo", "useCallback"],
        must_not_contain=["@hook", "def use", "class Component"],
        min_occurrences=1
    ),
    
    "closures javascript": ConceptValidator(
        must_contain_any=["function", "return function", "() =>", "return ("],
        must_not_contain=["def ", "lambda", "yield"],
        min_occurrences=2,
        regex_pattern=r"(function.*\{.*return\s+function|const.*=.*\(.*\).*=>.*\(.*\).*=>)"
    ),
    
    "arrow functions javascript": ConceptValidator(
        must_contain_any=["=>", "const ", "let "],
        must_not_contain=["lambda", "def ", "yield"],
        min_occurrences=2
    ),
    
    "destructuring javascript": ConceptValidator(
        must_contain_any=["const {", "let {", "const [", "let [", "..."],
        must_not_contain=["def ", "import ", "from dataclasses"],
        min_occurrences=1
    ),
    
    "event handling javascript": ConceptValidator(
        must_contain_any=["addEventListener", "onClick", "onSubmit", ".on(", "onChange"],
        must_not_contain=["def on_", "@event", "def handle"],
        min_occurrences=1
    ),
    
    "callbacks javascript": ConceptValidator(
        must_contain_any=["function(", "callback", "(err, ", "=>", "(error,"],
        must_not_contain=["def callback", "lambda", "yield"],
        min_occurrences=1
    ),
    
    "array methods javascript": ConceptValidator(
        must_contain_any=[".map(", ".filter(", ".reduce(", ".forEach(", ".find("],
        must_not_contain=["[x for x in", "list(map", "[", "for ", "]"],
        min_occurrences=2
    ),
    
    "classes javascript": ConceptValidator(
        must_contain_any=["class ", "constructor(", "extends ", "super("],
        must_not_contain=["class :", "def __init__", "__init__(self"],
        min_occurrences=1
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
"""
    
    # JavaScript promise sample
    js_promise_code = """
function fetchData() {
    return new Promise((resolve, reject) => {
        setTimeout(() => resolve('data'), 1000);
    });
}
"""
    
    # Test Python validator
    is_python_async = validate_file_for_concept(
        "test.py", 
        python_async_code, 
        "async await python"
    )
    print(f"Python async detected: {is_python_async} (expected: True)")
    
    # Should NOT match JavaScript validator
    is_js_async = validate_file_for_concept(
        "test.py",
        python_async_code,
        "async await javascript"
    )
    print(f"JS async detected in Python code: {is_js_async} (expected: False)")
    
    # Test JavaScript validator
    is_js_promise = validate_file_for_concept(
        "test.js",
        js_promise_code,
        "promises javascript"
    )
    print(f"JS promise detected: {is_js_promise} (expected: True)")
    
    # Should NOT match Python validator
    is_python_promise = validate_file_for_concept(
        "test.js",
        js_promise_code,
        "async await python"
    )
    print(f"Python async detected in JS code: {is_python_promise} (expected: False)")


if __name__ == "__main__":
    print("Testing concept validators...")
    test_validator_on_sample()
    print(f"\nTotal concepts available: {len(ALL_VALIDATORS)}")
    print(f"Python concepts: {len(PYTHON_VALIDATORS)}")
    print(f"JavaScript concepts: {len(JAVASCRIPT_VALIDATORS)}")
