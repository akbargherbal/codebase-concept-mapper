import sys
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

    def define_concept(self, name: str, desc: str):
        state = self.state_manager.load_state()
        if not state:
            print("❌ No state file found. Run 'init' first.", file=sys.stderr)
            return
        
        key = normalize_key(name)
        
        if key not in state.concepts:
            state.concepts[key] = Concept(display_name=name, definition=desc)
            print(f"✅ Defined new concept: {name}")
        else:
            state.concepts[key].definition = desc
            print(f"✅ Updated definition for: {name}")

        if self.state_manager.save_state(state):
            print(f"   Definition set to: '{desc}'")

    def add_mapping(self, concept_name: str, file_path: str, identifier: Optional[str], 
                    lines: Optional[str], confidence: str, pattern_type: str, evidence: str):
        state = self.state_manager.load_state()
        if not state:
            print("❌ No state file found. Run 'init' first.", file=sys.stderr)
            return

        key = normalize_key(concept_name)
        if key not in state.concepts:
            print(f"❌ Concept '{concept_name}' not found. Define it first with 'define' command.", file=sys.stderr)
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
            print(f"🔍 Scanning {file_path} for identifier '{identifier}'...")
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
            print("   No concepts defined yet. Use 'define' to add one.")
        else:
            for data in sorted(state.concepts.values(), key=lambda c: c.display_name):
                count = len(data.implementations)
                print(f"   • {data.display_name:<20} [{count}]")
        print("-" * 40)