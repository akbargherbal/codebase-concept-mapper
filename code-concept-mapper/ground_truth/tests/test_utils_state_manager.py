import json
import os
import pytest
import sys
from src.utils.state_manager import StateManager
from datetime import datetime, timedelta

def test_load_state_non_existent(tmp_path):
    """Test that loading a non-existent state file returns None."""
    state_file = tmp_path / "concepts_map.json"
    manager = StateManager(state_file_path=str(state_file))
    assert manager.load_state() is None

def test_save_and_load_cycle(tmp_path, empty_concept_map):
    """Test that saving and then loading a state preserves data."""
    state_file = tmp_path / "concepts_map.json"
    manager = StateManager(state_file_path=str(state_file))

    # Save the initial state
    assert manager.save_state(empty_concept_map) is True
    assert state_file.exists()

    # Load it back and verify
    loaded_state = manager.load_state()
    assert loaded_state is not None
    assert loaded_state.metadata.project == "test-project"
    assert loaded_state.concepts == {}

def test_backup_rotation(tmp_path, empty_concept_map, mocker):
    """Test that old backups are removed by mocking datetime with a generator."""
    state_file = tmp_path / "concepts_map.json"
    manager = StateManager(state_file_path=str(state_file))
    backup_dir = tmp_path / ".mapper_backups"

    start_time = datetime(2025, 12, 5, 12, 0, 0)

    # This generator will yield a new, incremented time on each call.
    def time_generator(start):
        current = start
        while True:
            yield current
            current += timedelta(seconds=1)

    # Patch datetime.now to use our generator
    mock_datetime = mocker.patch('src.utils.state_manager.datetime')
    mock_datetime.now.side_effect = time_generator(start_time)

    # Create 6 backups
    for i in range(6):
        manager.save_state(empty_concept_map)

    backups = list(backup_dir.glob("*.json"))
    assert len(backups) == 5  # Should have pruned the oldest one

    # Verify the oldest backup is gone (the one from 12:00:00)
    backup_filenames = [b.name for b in backups]
    first_backup_timestamp = start_time.strftime('%Y%m%d_%H%M%S')
    assert f"concepts_map_{first_backup_timestamp}.json" not in backup_filenames

def test_load_state_corrupted_json(tmp_path, capsys):
    """Test loading a file with invalid JSON exits gracefully."""
    state_file = tmp_path / "concepts_map.json"
    state_file.write_text("{'invalid': 'json',}")  # Invalid JSON with trailing comma
    manager = StateManager(state_file_path=str(state_file))

    with pytest.raises(SystemExit) as e:
        manager.load_state()

    assert e.type == SystemExit
    assert e.value.code == 1
    captured = capsys.readouterr()
    assert "CORRUPTION DETECTED" in captured.err

def test_load_state_invalid_schema(tmp_path, capsys):
    """Test loading a file with valid JSON but missing required keys."""
    state_file = tmp_path / "concepts_map.json"
    # Missing 'concepts' key
    state_file.write_text(json.dumps({"metadata": {"project": "test"}}))
    manager = StateManager(state_file_path=str(state_file))

    with pytest.raises(SystemExit) as e:
        manager.load_state()

    assert e.type == SystemExit
    assert e.value.code == 1
    captured = capsys.readouterr()
    assert "Failed to load state" in captured.err
    assert "Invalid schema" in captured.err

def test_save_state_fails(tmp_path, empty_concept_map, mocker, capsys):
    """Test that save_state handles exceptions, returns False, and cleans up."""
    state_file = tmp_path / "concepts_map.json"
    manager = StateManager(state_file_path=str(state_file))

    # Mock json.dump to raise an exception
    mocker.patch('json.dump', side_effect=IOError("Disk full"))

    result = manager.save_state(empty_concept_map)
    assert result is False
    # Temp file should be cleaned up
    assert not manager.temp_file.exists()
    captured = capsys.readouterr()
    assert "Save failed: Disk full" in captured.err