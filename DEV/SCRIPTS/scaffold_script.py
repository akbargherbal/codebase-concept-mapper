#!/usr/bin/env python3
"""
scaffold.py - Project Structure Generator for Code Concept Mapper

Creates the complete directory structure and placeholder files for the
code-concept-mapper project.

Usage:
    python scaffold.py [--dry-run]

Options:
    --dry-run    Print the structure without creating files
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def create_placeholder_content(file_type, file_path):
    """Generate appropriate placeholder content based on file type."""
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    file_name = os.path.basename(file_path)
    
    placeholders = {
        '.md': f"# {file_name.replace('.md', '').replace('_', ' ').title()}\n\n"
               f"*Created: {timestamp}*\n\n"
               f"TODO: Add content\n",
        
        '.py': f'"""\n{file_name}\n\n'
               f'Created: {timestamp}\n'
               f'TODO: Implement\n'
               f'"""\n\n',
        
        '.txt': f"# {file_name}\n# Created: {timestamp}\n\nTODO: Add content\n",
        
        '.json': '{\n  "TODO": "Add content"\n}\n',
        
        '.yaml': f"# {file_name}\n# Created: {timestamp}\n\nTODO: Add content\n",
        
        '.sh': f"#!/bin/bash\n# {file_name}\n# Created: {timestamp}\n\n"
               f"# TODO: Implement script\n",
        
        '.gitignore': "# Python\n__pycache__/\n*.py[cod]\n*$py.class\n"
                      "*.so\n.Python\n\n# Virtual environments\nvenv/\nenv/\n"
                      "ENV/\n\n# IDEs\n.vscode/\n.idea/\n*.swp\n*.swo\n\n"
                      "# Project specific\n.mapper_backups/\n*.tmp\n"
                      "config/*.yaml\n!config/*.yaml.example\n",
        
        'requirements.txt': "# Core dependencies\n# TODO: Add actual requirements\n\n"
                           "# Testing\npytest>=7.4.0\npytest-cov>=4.1.0\n",
    }
    
    # Match by extension
    ext = os.path.splitext(file_path)[1]
    if ext in placeholders:
        return placeholders[ext]
    
    # Match by exact filename
    if file_name in placeholders:
        return placeholders[file_name]
    
    # Default placeholder
    return f"# {file_name}\n# Created: {timestamp}\n"


PROJECT_STRUCTURE = {
    # Root files
    'README.md': 'file',
    'requirements.txt': 'file',
    '.gitignore': 'file',
    
    # Documentation
    'docs/sessions/session_01.md': 'file',
    'docs/sessions/session_02.md': 'file',
    'docs/sessions/session_03.md': 'file',
    'docs/sessions/session_04.md': 'file',
    'docs/NEW_CONTEXT.md': 'file',
    'docs/PHASED_PLAN.md': 'file',
    'docs/architecture/abstraction_layer.md': 'file',
    'docs/architecture/google_integration.md': 'file',
    
    # Ground Truth (Phase 1B)
    'ground_truth/tools/concept_mapper.py': 'file',
    'ground_truth/tools/validator.py': 'file',
    'ground_truth/tools/__init__.py': 'file',
    'ground_truth/personas/GEMINI.md': 'file',
    'ground_truth/data/concepts_map.json': 'file',
    'ground_truth/data/.mapper_backups/.gitkeep': 'file',
    'ground_truth/tests/test_concept_mapper.py': 'file',
    'ground_truth/tests/fixtures/.gitkeep': 'file',
    'ground_truth/tests/__init__.py': 'file',
    'ground_truth/README.md': 'file',
    
    # Corpus (Test repositories)
    'corpus/flask/src/.gitkeep': 'file',
    'corpus/django/.gitkeep': 'file',
    'corpus/express/.gitkeep': 'file',
    'corpus/README.md': 'file',
    
    # Phase 1 Validation
    'phase1_validation/quick_test.py': 'file',
    'phase1_validation/validators/keyword_validators.py': 'file',
    'phase1_validation/validators/__init__.py': 'file',
    'phase1_validation/results/phase1a_results.json': 'file',
    'phase1_validation/README.md': 'file',
    
    # Source code (Future phases)
    'src/__init__.py': 'file',
    'src/domain/__init__.py': 'file',
    'src/domain/models.py': 'file',
    'src/providers/__init__.py': 'file',
    'src/providers/base.py': 'file',
    'src/providers/google_provider.py': 'file',
    'src/providers/local_provider.py': 'file',
    'src/business_logic/__init__.py': 'file',
    'src/business_logic/concept_mapper.py': 'file',
    'src/business_logic/taxonomy.py': 'file',
    'src/business_logic/rankers.py': 'file',
    'src/utils/__init__.py': 'file',
    'src/utils/validators.py': 'file',
    
    # Configuration
    'config/concepts.yaml': 'file',
    'config/providers.yaml.example': 'file',
    'config/README.md': 'file',
    
    # Scripts
    'scripts/index_repository.py': 'file',
    'scripts/run_ground_truth.sh': 'file',
    'scripts/evaluate_accuracy.py': 'file',
    
    # Notebooks (optional)
    'notebooks/phase1_diagnostics.ipynb': 'file',
    'notebooks/.gitkeep': 'file',
}


def create_structure(base_path, structure, dry_run=False):
    """Create the directory structure and files."""
    
    created_dirs = set()
    created_files = []
    
    for path, item_type in structure.items():
        full_path = base_path / path
        
        # Create parent directories
        parent_dir = full_path.parent
        if parent_dir not in created_dirs:
            if dry_run:
                print(f"[DIR]  {parent_dir.relative_to(base_path)}/")
            else:
                parent_dir.mkdir(parents=True, exist_ok=True)
            created_dirs.add(parent_dir)
        
        # Create file
        if item_type == 'file':
            if dry_run:
                print(f"[FILE] {full_path.relative_to(base_path)}")
            else:
                if not full_path.exists():
                    content = create_placeholder_content(item_type, str(full_path))
                    full_path.write_text(content, encoding='utf-8')
                    created_files.append(full_path)
    
    return created_dirs, created_files


def print_summary(base_path, dirs, files, dry_run=False):
    """Print summary of created structure."""
    
    action = "Would create" if dry_run else "Created"
    
    print("\n" + "="*60)
    print(f"Project scaffolding {'preview' if dry_run else 'complete'}!")
    print("="*60)
    print(f"\n{action} project structure at: {base_path.absolute()}")
    print(f"  - Directories: {len(dirs)}")
    print(f"  - Files: {len(files)}")
    
    if not dry_run:
        print("\nNext steps:")
        print("  1. cd code-concept-mapper")
        print("  2. Review the structure")
        print("  3. Move your existing files:")
        print("     - concept_mapper.py → ground_truth/tools/")
        print("     - GEMINI.md → ground_truth/personas/")
        print("     - session_*.md → docs/sessions/")
        print("  4. Start implementing!")
    
    print("\n" + "="*60)


def main():
    """Main execution function."""
    
    # Parse arguments
    dry_run = '--dry-run' in sys.argv
    
    # Define base path
    base_path = Path.cwd() / 'code-concept-mapper'
    
    # Check if project already exists
    if base_path.exists() and not dry_run:
        response = input(f"\n⚠️  '{base_path}' already exists. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return 1
    
    print(f"\n{'Previewing' if dry_run else 'Creating'} project structure...")
    print(f"Target: {base_path.absolute()}\n")
    
    # Create structure
    dirs, files = create_structure(base_path, PROJECT_STRUCTURE, dry_run)
    
    # Print summary
    print_summary(base_path, dirs, files, dry_run)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
