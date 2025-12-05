import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.domain.models import ConceptMap, Metadata, Concept, Implementation

class StateManager:
    def __init__(self, state_file_path: str):
        self.state_file = Path(state_file_path)
        self.backup_dir = self.state_file.parent / ".mapper_backups"
        self.temp_file = self.state_file.parent / f"{self.state_file.name}.tmp"

    def _ensure_backup_dir(self):
        self.backup_dir.mkdir(exist_ok=True)

    def _create_backup(self):
        if self.state_file.exists():
            self._ensure_backup_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"{self.state_file.stem}_{timestamp}.json"
            shutil.copy2(self.state_file, backup_path)
            
            backups = sorted(self.backup_dir.glob(f"{self.state_file.stem}_*.json"), key=os.path.getmtime)
            for old_backup in backups[:-5]:
                os.remove(old_backup)

    def _serialize(self, concept_map: ConceptMap) -> dict:
        """Converts the ConceptMap object to a JSON-serializable dictionary."""
        return {
            "metadata": concept_map.metadata.__dict__,
            "concepts": {
                key: {
                    "display_name": concept.display_name,
                    "definition": concept.definition,
                    "implementations": [impl.__dict__ for impl in concept.implementations],
                }
                for key, concept in concept_map.concepts.items()
            },
        }

    def _deserialize(self, data: dict) -> ConceptMap:
        """Converts a dictionary from JSON into a ConceptMap object."""
        metadata = Metadata(**data["metadata"])
        concepts = {
            key: Concept(
                display_name=concept_data["display_name"],
                definition=concept_data.get("definition", ""),
                implementations=[
                    Implementation(**impl_data)
                    for impl_data in concept_data["implementations"]
                ],
            )
            for key, concept_data in data["concepts"].items()
        }
        return ConceptMap(metadata=metadata, concepts=concepts)

    def load_state(self) -> Optional[ConceptMap]:
        if not self.state_file.exists():
            return None
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "metadata" not in data or "concepts" not in data:
                raise ValueError("Invalid schema: missing metadata or concepts")
            return self._deserialize(data)
        except json.JSONDecodeError as e:
            print(f"❌ CORRUPTION DETECTED: Invalid JSON at line {e.lineno}", file=sys.stderr)
            print(f"   Error: {e.msg}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"❌ Failed to load state: {e}", file=sys.stderr)
            sys.exit(1)

    def save_state(self, state: ConceptMap) -> bool:
        self._create_backup()
        state.metadata.last_updated = datetime.now().isoformat()
        try:
            serializable_state = self._serialize(state)
            with open(self.temp_file, "w", encoding="utf-8") as f:
                json.dump(serializable_state, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(self.temp_file, self.state_file)
            return True
        except Exception as e:
            print(f"❌ Save failed: {e}", file=sys.stderr)
            if self.temp_file.exists():
                os.remove(self.temp_file)
            return False

    def initialize_state(self, project_name: str) -> ConceptMap:
        """Creates a new, empty ConceptMap."""
        metadata = Metadata(
            project=project_name,
            version="1.1",
            created_at=datetime.now().isoformat()
        )
        return ConceptMap(metadata=metadata, concepts={})