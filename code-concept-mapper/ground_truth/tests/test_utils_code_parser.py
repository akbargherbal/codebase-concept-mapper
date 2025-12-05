from src.utils.code_parser import find_lines_by_identifier, extract_snippet

def test_find_lines_class(tmp_path):
    """Test finding lines for a simple class."""
    source_file = tmp_path / "source.py"
    source_file.write_text("\n\nclass MyClass:\n    def method(self):\n        pass\n")
    
    start, end = find_lines_by_identifier(str(source_file), "MyClass")
    assert start == 3
    assert end == 5

def test_find_lines_function(tmp_path):
    """Test finding lines for a function."""
    source_file = tmp_path / "source.py"
    source_file.write_text("def my_function():\n    # A comment\n    return True\n")

    start, end = find_lines_by_identifier(str(source_file), "my_function")
    assert start == 1
    assert end == 3

def test_identifier_not_found(tmp_path):
    """Test that it returns None, None when the identifier is not found."""
    source_file = tmp_path / "source.py"
    source_file.write_text("class AnotherClass:\n    pass\n")
    
    start, end = find_lines_by_identifier(str(source_file), "MyClass")
    assert start is None
    assert end is None

def test_extract_snippet(tmp_path):
    """Test extracting a code snippet."""
    source_file = tmp_path / "source.py"
    content = "line1\nline2\nline3\nline4\nline5\n"
    source_file.write_text(content)

    snippet = extract_snippet(str(source_file), 2, 4)
    assert snippet == "line2\nline3\nline4\n"


def test_find_lines_syntax_error(tmp_path, capsys):
    """Test parsing a file with a Python syntax error."""
    source_file = tmp_path / "source.py"
    source_file.write_text("class MyClass:\n  def method(self)\n    pass\n") # Missing colon

    start, end = find_lines_by_identifier(str(source_file), "MyClass")
    assert start is None
    assert end is None
    
    captured = capsys.readouterr()
    assert "Syntax Error" in captured.err
 