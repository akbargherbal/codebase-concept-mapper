#!/usr/bin/env python3
import argparse
import os
import sys

# Add the project root to the Python path to allow imports from `src`
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.business_logic.concept_mapping_service import ConceptMappingService
from src.utils.state_manager import StateManager

def main():
    parser = argparse.ArgumentParser(
        description="A CLI tool to map programming concepts to code implementations."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_init = subparsers.add_parser("init", help="Initialize a new concepts_map.json file.")
    p_init.add_argument("project_name", help="Name of the project being audited.")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing state file.")

    # --- NEW: load-concepts command ---
    p_load = subparsers.add_parser("load-concepts", help="Load concept definitions from a JSON taxonomy file.")
    p_load.add_argument("concepts_file", help="Path to the concepts taxonomy JSON file.")

    # --- 'define' command has been REMOVED ---

    p_add = subparsers.add_parser("add", help="Map a concept to a code implementation.")
    p_add.add_argument("concept", help="The concept name to map.")
    p_add.add_argument("--file", required=True, help="Path to the file containing the implementation.")
    p_add.add_argument("--identifier", help="Name of class/function (Preferred over lines).")
    p_add.add_argument("--lines", help="Fallback line range (e.g. '10-20').")
    p_add.add_argument("--confidence", default="high", choices=["high", "medium", "low"])
    p_add.add_argument("--type", required=True, help="Type of implementation (e.g., 'class_definition').")
    p_add.add_argument("--evidence", required=True, help="Specific reason for the mapping.")

    subparsers.add_parser("status", help="Show a summary of the current concept map.")

    args = parser.parse_args()

    # The state file is managed relative to the project root for consistency.
    state_file_path = os.path.join(project_root, 'ground_truth', 'data', 'concepts_map.json')
    state_manager = StateManager(state_file_path=state_file_path)
    service = ConceptMappingService(state_manager)

    if args.command == "init":
        service.init_project(args.project_name, args.force)
    elif args.command == "load-concepts":
        service.load_concepts_from_file(args.concepts_file)
    elif args.command == "add":
        service.add_mapping(
            args.concept, args.file, args.identifier, args.lines,
            args.confidence, args.type, args.evidence
        )
    elif args.command == "status":
        service.show_status()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
