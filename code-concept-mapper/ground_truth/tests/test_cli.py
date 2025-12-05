import sys
import os
import json
from unittest.mock import patch

from ground_truth.tools.concept_mapper import main as cli_main

def test_cli_init_command(tmp_path, monkeypatch):
    """
    Tests the 'init' command end-to-end by patching the project_root.
    """
    # This is the file that the script will create inside our tmp_path
    state_file = tmp_path / "ground_truth" / "data" / "concepts_map.json"
    
    # Ensure the parent directories exist for the script to write into
    state_file.parent.mkdir(parents=True)

    monkeypatch.setattr(sys, 'argv', ['concept_mapper', 'init', 'test-project'])
    
    # CORRECTED PATCH: We patch the global 'project_root' variable.
    with patch('ground_truth.tools.concept_mapper.project_root', str(tmp_path)):
        cli_main()

    # Assertions: Check if the command worked correctly
    assert state_file.exists()
    with open(state_file, "r") as f:
        data = json.load(f)
    
    assert data['metadata']['project'] == 'test-project'
    assert data['concepts'] == {}

def test_cli_full_workflow(tmp_path, monkeypatch, capsys):
    """
    Tests a full init -> load-concepts -> status workflow.
    """
    state_file = tmp_path / "ground_truth" / "data" / "concepts_map.json"
    state_file.parent.mkdir(parents=True)
    
    # Create a dummy concepts file for the test
    concepts_file = tmp_path / "concepts.json"
    concepts_file.write_text(json.dumps({
        "concepts": [{"name": "Decorators", "description": "Functions that wrap others"}]
    }))

    # 1. Run INIT
    monkeypatch.setattr(sys, 'argv', ['concept_mapper', 'init', 'workflow-project'])
    with patch('ground_truth.tools.concept_mapper.project_root', str(tmp_path)):
        cli_main()
    
    # 2. Run LOAD-CONCEPTS (replaces 'define')
    monkeypatch.setattr(sys, 'argv', [
        'concept_mapper', 'load-concepts', str(concepts_file)
    ])
    with patch('ground_truth.tools.concept_mapper.project_root', str(tmp_path)):
        cli_main()

    # Verify the load command worked by reading the file
    with open(state_file, "r") as f:
        data = json.load(f)
    assert 'decorators' in data['concepts']
    assert data['concepts']['decorators']['display_name'] == 'Decorators'

    # 3. Run STATUS
    monkeypatch.setattr(sys, 'argv', ['concept_mapper', 'status'])
    with patch('ground_truth.tools.concept_mapper.project_root', str(tmp_path)):
        cli_main()
    
    # Check the output captured by pytest
    captured = capsys.readouterr()
    assert "workflow-project" in captured.out
    assert "Decorators" in captured.out
    assert "[0]" in captured.out


# Add this function to the existing test_cli.py file
def test_cli_add_command(tmp_path, monkeypatch):
    """Tests the 'add' command end-to-end."""
    state_file = tmp_path / "ground_truth" / "data" / "concepts_map.json"
    state_file.parent.mkdir(parents=True)

    # Create a dummy source file for the tool to parse
    source_file = tmp_path / "source.py"
    source_file.write_text("class MyDecorator:\n    pass\n")
    
    # Create a dummy concepts file
    concepts_file = tmp_path / "concepts.json"
    concepts_file.write_text(json.dumps({
        "concepts": [{"name": "Decorators", "description": "..."}]
    }))

    # Setup: Run init and load-concepts first
    monkeypatch.setattr(sys, 'argv', ['concept_mapper', 'init', 'add-test'])
    with patch('ground_truth.tools.concept_mapper.project_root', str(tmp_path)):
        cli_main()
    
    monkeypatch.setattr(sys, 'argv', ['concept_mapper', 'load-concepts', str(concepts_file)])
    with patch('ground_truth.tools.concept_mapper.project_root', str(tmp_path)):
        cli_main()

    # Run the 'add' command
    monkeypatch.setattr(sys, 'argv', [
        'concept_mapper', 'add', 'Decorators',
        '--file', str(source_file),
        '--identifier', 'MyDecorator',
        '--type', 'class_definition',
        '--evidence', 'A test decorator'
    ])
    with patch('ground_truth.tools.concept_mapper.project_root', str(tmp_path)):
        cli_main()

    # Assertions
    with open(state_file, "r") as f:
        data = json.load(f)
    
    implementations = data['concepts']['decorators']['implementations']
    assert len(implementations) == 1
    assert implementations[0]['identifier'] == 'MyDecorator'
    assert implementations[0]['line_start'] == 1
    assert implementations[0]['line_end'] == 2
    assert "class MyDecorator" in implementations[0]['code_snippet']
