import pytest
import json
from unittest.mock import MagicMock, patch
from src.business_logic.concept_mapping_service import ConceptMappingService, normalize_key
from src.domain.models import ConceptMap, Metadata, Concept, Implementation

@pytest.fixture
def mock_state_manager():
    """Fixture for a mocked StateManager."""
    return MagicMock()

@pytest.fixture
def populated_state():
    """Fixture for a ConceptMap with one concept already defined."""
    concept_key = normalize_key("Decorators")
    return ConceptMap(
        metadata=Metadata(project="test", version="1.0"),
        concepts={
            concept_key: Concept(display_name="Decorators", definition="...")
        }
    )

@pytest.fixture
def empty_state():
    """Fixture for a ConceptMap with no concepts."""
    return ConceptMap(
        metadata=Metadata(project="test", version="1.0"),
        concepts={}
    )

# --- NEW TESTS FOR load_concepts_from_file ---

def test_load_concepts_from_file_success(tmp_path, mock_state_manager, empty_state):
    """Test loading concepts from a valid JSON file into an empty state."""
    service = ConceptMappingService(mock_state_manager)
    mock_state_manager.load_state.return_value = empty_state
    mock_state_manager.save_state.return_value = True
    
    concepts_file = tmp_path / "concepts.json"
    concepts_file.write_text(json.dumps({
        "concepts": [
            {"name": "Context Managers", "description": "...", "keywords": ["with"], "category": "lang"},
            {"name": "Decorators", "description": "...", "languages": ["python"]}
        ]
    }))
    
    result = service.load_concepts_from_file(str(concepts_file))
    
    assert result is True
    mock_state_manager.save_state.assert_called_once()
    saved_state = mock_state_manager.save_state.call_args[0][0]
    
    assert len(saved_state.concepts) == 2
    assert "context_managers" in saved_state.concepts
    assert saved_state.concepts["context_managers"].keywords == ["with"]
    assert saved_state.concepts["decorators"].languages == ["python"]

def test_load_concepts_duplicate_skipping(tmp_path, mock_state_manager, populated_state, capsys):
    """Test that load-concepts skips concepts that already exist."""
    service = ConceptMappingService(mock_state_manager)
    mock_state_manager.load_state.return_value = populated_state  # Already has "Decorators"
    mock_state_manager.save_state.return_value = True
    
    concepts_file = tmp_path / "concepts.json"
    concepts_file.write_text(json.dumps({
        "concepts": [
            {"name": "Decorators", "description": "New description"},
            {"name": "Context Managers", "description": "New concept"}
        ]
    }))
    
    service.load_concepts_from_file(str(concepts_file))
    
    saved_state = mock_state_manager.save_state.call_args[0][0]
    assert len(saved_state.concepts) == 2
    assert saved_state.concepts['decorators'].definition == "..."  # Original definition is preserved
    
    captured = capsys.readouterr()
    assert "Skipped 1 duplicates" in captured.out

def test_load_concepts_file_not_found(mock_state_manager, capsys):
    """Test that an error is printed if the concepts file does not exist."""
    service = ConceptMappingService(mock_state_manager)
    service.load_concepts_from_file("non_existent_file.json")
    captured = capsys.readouterr()
    assert "Concepts file not found" in captured.err

def test_load_concepts_invalid_json(tmp_path, mock_state_manager, empty_state, capsys):
    """Test loading a file with invalid JSON."""
    service = ConceptMappingService(mock_state_manager)
    mock_state_manager.load_state.return_value = empty_state
    
    concepts_file = tmp_path / "concepts.json"
    concepts_file.write_text("{'invalid': 'json'}")
    
    service.load_concepts_from_file(str(concepts_file))
    captured = capsys.readouterr()
    assert "Invalid JSON" in captured.err

# --- END NEW TESTS ---


# CORRECTED TEST
@patch('src.business_logic.concept_mapping_service.extract_snippet', return_value="dummy snippet")
@patch('src.business_logic.concept_mapping_service.find_lines_by_identifier', return_value=(10, 20))
def test_add_mapping_duplicate_detection(mock_find_lines, mock_extract_snippet, mock_state_manager, populated_state, capsys):
    """Test that adding a duplicate implementation is skipped."""
    service = ConceptMappingService(mock_state_manager)

    concept_key = normalize_key("Decorators")
    existing_impl = Implementation(
        file_path="file.py", identifier="my_decorator", line_start=10, line_end=20,
        code_snippet="...", confidence="high", pattern_type="decorator",
        evidence="...", added_at="..."
    )
    populated_state.concepts[concept_key].implementations.append(existing_impl)
    mock_state_manager.load_state.return_value = populated_state

    service.add_mapping(
        concept_name="Decorators", file_path="file.py", identifier="my_decorator",
        lines=None, confidence="high", pattern_type="decorator", evidence="..."
    )

    captured = capsys.readouterr()
    # The "Duplicate detected" message is now printed to stdout
    assert "Duplicate detected" in captured.out
    mock_state_manager.save_state.assert_not_called()


def test_add_mapping_undefined_concept(mock_state_manager, capsys):
    """Test adding a mapping to a concept that has not been defined."""
    service = ConceptMappingService(mock_state_manager)
    mock_state_manager.load_state.return_value = ConceptMap(
        metadata=Metadata(project="test", version="1.0")
    )

    service.add_mapping(
        concept_name="NonExistent", file_path="file.py", identifier="ident",
        lines="1-1", confidence="high", pattern_type="...", evidence="..."
    )

    captured = capsys.readouterr()
    assert "Concept 'NonExistent' not found" in captured.err
    mock_state_manager.save_state.assert_not_called()

@patch('src.business_logic.concept_mapping_service.find_lines_by_identifier')
def test_add_mapping_lines_fallback(mock_find_lines, mock_state_manager, populated_state):
    """Test that the --lines argument is used when --identifier fails."""
    service = ConceptMappingService(mock_state_manager)
    mock_state_manager.load_state.return_value = populated_state
    mock_find_lines.return_value = (None, None)

    with patch('src.business_logic.concept_mapping_service.extract_snippet', return_value="snippet"):
        service.add_mapping(
            concept_name="Decorators", file_path="file.py", identifier="bad_ident",
            lines="42-50", confidence="high", pattern_type="...", evidence="..."
        )

    mock_state_manager.save_state.assert_called_once()
    saved_state = mock_state_manager.save_state.call_args[0][0]
    impl = saved_state.concepts[normalize_key("Decorators")].implementations[0]
    assert impl.line_start == 42
    assert impl.line_end == 50

def test_init_project_already_exists(mock_state_manager, capsys):
    """Test that init_project does not overwrite an existing file without --force."""
    service = ConceptMappingService(mock_state_manager)
    mock_state_manager.state_file.exists.return_value = True

    service.init_project("my-project", force=False)

    captured = capsys.readouterr()
    assert "already exists" in captured.out
    mock_state_manager.save_state.assert_not_called()

# --- 'define' tests have been REMOVED ---

def test_add_mapping_no_state_file(mock_state_manager, capsys):
    """Test add_mapping when no state file is found."""
    service = ConceptMappingService(mock_state_manager)
    mock_state_manager.load_state.return_value = None

    service.add_mapping("Concept", "file.py", "id", "1-2", "high", "t", "e")

    captured = capsys.readouterr()
    assert "No state file found" in captured.err
    mock_state_manager.save_state.assert_not_called()

@patch('src.business_logic.concept_mapping_service.find_lines_by_identifier', return_value=(None, None))
def test_add_mapping_no_lines_found(mock_find_lines, mock_state_manager, populated_state, capsys):
    """Test add_mapping fails when neither identifier nor lines can determine a range."""
    service = ConceptMappingService(mock_state_manager)
    mock_state_manager.load_state.return_value = populated_state

    service.add_mapping(
        concept_name="Decorators", file_path="file.py", identifier="bad_ident",
        lines=None, confidence="high", pattern_type="...", evidence="..."
    )

    captured = capsys.readouterr()
    assert "Could not determine lines" in captured.err
    mock_state_manager.save_state.assert_not_called()

@patch('src.business_logic.concept_mapping_service.find_lines_by_identifier', return_value=(10, 20))
@patch('src.business_logic.concept_mapping_service.extract_snippet', return_value=None)
def test_add_mapping_snippet_extraction_fails(mock_extract, mock_find_lines, mock_state_manager, populated_state, capsys):
    """Test add_mapping fails if the code snippet cannot be extracted."""
    service = ConceptMappingService(mock_state_manager)
    mock_state_manager.load_state.return_value = populated_state

    service.add_mapping(
        concept_name="Decorators", file_path="file.py", identifier="ident",
        lines=None, confidence="high", pattern_type="...", evidence="..."
    )

    captured = capsys.readouterr()
    assert "Could not read file content" in captured.err
    mock_state_manager.save_state.assert_not_called()

@patch('src.business_logic.concept_mapping_service.find_lines_by_identifier', return_value=(10, 20))
@patch('src.business_logic.concept_mapping_service.extract_snippet', return_value="snippet")
def test_add_mapping_save_fails(mock_extract, mock_find_lines, mock_state_manager, populated_state, capsys):
    """Test add_mapping handles a failure during state saving."""
    service = ConceptMappingService(mock_state_manager)
    mock_state_manager.load_state.return_value = populated_state
    mock_state_manager.save_state.return_value = False  # Simulate save failure

    service.add_mapping(
        concept_name="Decorators", file_path="file.py", identifier="ident",
        lines=None, confidence="high", pattern_type="...", evidence="..."
    )

    captured = capsys.readouterr()
    assert "Failed to save mapping" in captured.err

@pytest.mark.parametrize("invalid_lines", ["42", "42-", "abc-def"])
@patch('src.business_logic.concept_mapping_service.find_lines_by_identifier', return_value=(None, None))
def test_add_mapping_invalid_lines_format(mock_find_lines, invalid_lines, mock_state_manager, populated_state, capsys):
    """Test that add_mapping handles invalid --lines formats."""
    service = ConceptMappingService(mock_state_manager)
    mock_state_manager.load_state.return_value = populated_state

    service.add_mapping(
        concept_name="Decorators", file_path="file.py", identifier=None,
        lines=invalid_lines, confidence="high", pattern_type="...", evidence="..."
    )

    captured = capsys.readouterr()
    assert "Invalid line format" in captured.err
    mock_state_manager.save_state.assert_not_called()

def test_show_status_no_state_file(mock_state_manager, capsys):
    """Test show_status when no state file is found."""
    service = ConceptMappingService(mock_state_manager)
    mock_state_manager.load_state.return_value = None

    service.show_status()

    captured = capsys.readouterr()
    assert "No state file found" in captured.err

def test_show_status_no_concepts(mock_state_manager, empty_state, capsys):
    """Test show_status with a state that has no concepts defined."""
    service = ConceptMappingService(mock_state_manager)
    mock_state_manager.load_state.return_value = empty_state

    service.show_status()

    captured = capsys.readouterr()
    assert "No concepts loaded yet" in captured.out
