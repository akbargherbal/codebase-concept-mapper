import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from src.domain.models import Concept, Implementation
from src.utils.state_manager import StateManager
from src.utils.code_parser import find_lines_by_identifier, extract_snippet

def normalize_key(name: str) -> str:
    """Creates a consistent key from a display name."""
    return name.lower().strip().replace(" ", "_").replace("-", "_")

class ConceptMappingService:
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager

    def init_project(self, project_name: str, force: bool = False):
        if self.state_manager.state_file.exists() and not force:
            print(f"⚠️  State file '{self.state_manager.state_file}' already exists. Use --force to overwrite.")
            return
        
        state = self.state_manager.initialize_state(project_name)
        if self.state_manager.save_state(state):
            print(f"✅ Initialized concept map for '{project_name}'")

    # --- define_concept method has been REMOVED ---

    def load_concepts_from_file(self, concepts_file_path: str) -> bool:
        """Load concept definitions from a JSON taxonomy file."""
        concepts_file = Path(concepts_file_path)
        if not concepts_file.exists():
            print(f"❌ Concepts file not found: {concepts_file_path}", file=sys.stderr)
            return False
        
        state = self.state_manager.load_state()
        if not state:
            print("❌ No state file found. Run 'init' first.", file=sys.stderr)
            return False
        
        try:
            with open(concepts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'concepts' not in data or not isinstance(data['concepts'], list):
                print("❌ Invalid taxonomy schema: missing or invalid 'concepts' list.", file=sys.stderr)
                return False
            
            loaded_count = 0
            skipped_count = 0
            for concept_data in data['concepts']:
                if 'name' not in concept_data or 'description' not in concept_data:
                    print(f"⚠️  Skipping invalid concept entry (missing name/desc): {concept_data}", file=sys.stderr)
                    continue
                
                key = normalize_key(concept_data['name'])
                
                if key not in state.concepts:
                    new_concept = Concept(
                        display_name=concept_data['name'],
                        definition=concept_data['description'],
                        keywords=concept_data.get('keywords', []),
                        languages=concept_data.get('languages', []),
                        category=concept_data.get('category')
                    )
                    state.concepts[key] = new_concept
                    loaded_count += 1
                else:
                    skipped_count += 1
            
            if self.state_manager.save_state(state):
                print(f"✅ Taxonomy loaded successfully.")
                if loaded_count > 0:
                    print(f"   - Added {loaded_count} new concepts.")
                if skipped_count > 0:
                    print(f"   - Skipped {skipped_count} duplicates.")
                return True
            else:
                print("❌ Failed to save state after loading concepts.", file=sys.stderr)
                return False
        
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {concepts_file_path} at line {e.lineno}: {e.msg}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"❌ Failed to load concepts: {e}", file=sys.stderr)
            return False

    def add_mapping(self, concept_name: str, file_path: str, identifier: Optional[str], 
                    lines: Optional[str], confidence: str, pattern_type: str, evidence: str):
        state = self.state_manager.load_state()
        if not state:
            print("❌ No state file found. Run 'init' first.", file=sys.stderr)
            return

        key = normalize_key(concept_name)
        if key not in state.concepts:
            print(f"❌ Concept '{concept_name}' not found. Load it first with the 'load-concepts' command.", file=sys.stderr)
            return

        final_start, final_end = self._determine_lines(file_path, identifier, lines)
        if not final_start:
            return

        snippet = extract_snippet(file_path, final_start, final_end)
        if not snippet:
            print(f"❌ Could not read file content at {file_path}:{final_start}-{final_end}", file=sys.stderr)
            return

        for impl in state.concepts[key].implementations:
            if impl.file_path == file_path and impl.line_start == final_start:
                print(f"⚠️  Duplicate detected at {file_path}:{final_start}. Skipping.")
                return

        new_impl = Implementation(
            file_path=file_path, identifier=identifier, line_start=final_start,
            line_end=final_end, code_snippet=snippet, confidence=confidence,
            pattern_type=pattern_type, evidence=evidence, added_at=datetime.now().isoformat(),
        )

        state.concepts[key].implementations.append(new_impl)
        if self.state_manager.save_state(state):
            print(f"✅ Mapped '{concept_name}' → {file_path} ({final_start}-{final_end})")
        else:
            print(f"❌ Failed to save mapping", file=sys.stderr)

    def _determine_lines(self, file_path, identifier, lines):
        if identifier:
            print(f"🔎 Scanning {file_path} for identifier '{identifier}'...")
            start, end = find_lines_by_identifier(file_path, identifier)
            if start and end:
                print(f"   ✓ Found at lines {start}-{end}")
                return start, end
            print(f"   ⚠️  Identifier '{identifier}' not found in AST. Falling back to --lines if provided.")

        if lines:
            try:
                parts = lines.split("-")
                if len(parts) != 2: raise ValueError("Expected format: start-end")
                start, end = int(parts[0]), int(parts[1])
                print(f"   Using manual line range: {start}-{end}")
                return start, end
            except ValueError as e:
                print(f"❌ Invalid line format: {e}", file=sys.stderr)
                return None, None
        
        print("❌ Could not determine lines. Provide a valid --identifier or --lines.", file=sys.stderr)
        return None, None

    def show_status(self):
        state = self.state_manager.load_state()
        if not state:
            print("❌ No state file found. Run 'init' first.", file=sys.stderr)
            return
        
        print(f"\n📊 Project: {state.metadata.project}")
        print(f"   Last Updated: {state.metadata.last_updated}")
        print("-" * 40)
        if not state.concepts:
            print("   No concepts loaded yet. Use 'load-concepts' to add a taxonomy.")
        else:
            for data in sorted(state.concepts.values(), key=lambda c: c.display_name):
                count = len(data.implementations)
                print(f"   • {data.display_name:<20} [{count}]")
        print("-" * 40)
