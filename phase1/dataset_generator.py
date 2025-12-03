"""
Phase 1: Test Dataset Generator (Colab Optimized)
Clones repos and samples random files for embedding tests
"""
import os
import json
import random
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Configuration
TEST_REPOS = {
    "python": [
        ("pallets/flask", "src/flask"),
        ("psf/requests", "src/requests"),
        ("aio-libs/aiohttp", "aiohttp"),
        ("django/django", "django")
    ],
    "javascript": [
        ("axios/axios", "lib"),
        ("expressjs/express", "lib"),
        ("facebook/react", "packages/react/src"),
        ("vercel/next.js", "packages/next/src")
    ]
}

FILES_PER_REPO = 12
MIN_LINES = 50
MAX_LINES = 500
OUTPUT_DIR = Path("test_code")
METADATA_FILE = OUTPUT_DIR / "metadata.json"


class DatasetGenerator:
    def __init__(self, use_drive=False, drive_path="/content/drive/MyDrive/phase1_cache"):
        """
        Args:
            use_drive: If True, save to Google Drive for persistence
            drive_path: Path to save cached data on Drive
        """
        self.output_dir = OUTPUT_DIR
        self.use_drive = use_drive
        self.drive_path = Path(drive_path) if use_drive else None
        self.metadata = {
            "generation_date": None,
            "repos": {},
            "files": [],
            "stats": {}
        }
        
    def setup_drive(self):
        """Mount Google Drive if requested"""
        if self.use_drive:
            try:
                from google.colab import drive
                drive.mount('/content/drive')
                self.drive_path.mkdir(parents=True, exist_ok=True)
                print(f"✓ Google Drive mounted at {self.drive_path}")
                return True
            except ImportError:
                print("⚠️ Google Colab not detected. Skipping Drive mount.")
                self.use_drive = False
                return False
        return False
    
    def setup_directories(self):
        """Create output directories"""
        (self.output_dir / "python").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "javascript").mkdir(parents=True, exist_ok=True)
        print(f"✓ Created output directories in {self.output_dir}")
    
    def clone_repo(self, repo_url: str, target_dir: Path) -> bool:
        """Clone a repository if not already present"""
        if target_dir.exists():
            print(f"  Repository already exists at {target_dir}")
            return True
        
        try:
            # Use --filter for faster clones on Colab
            cmd = [
                "git", "clone", 
                "--depth", "1",
                "--filter=blob:none",  # Faster partial clone
                "--no-checkout",  # Don't checkout yet
                f"https://github.com/{repo_url}.git", 
                str(target_dir)
            ]
            subprocess.run(cmd, check=True, capture_output=True, timeout=120)
            
            # Sparse checkout only the directory we need
            subprocess.run(
                ["git", "-C", str(target_dir), "checkout"],
                check=True, capture_output=True, timeout=60
            )
            
            print(f"  ✓ Cloned {repo_url}")
            return True
        except subprocess.TimeoutExpired:
            print(f"  ✗ Timeout cloning {repo_url}")
            return False
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to clone {repo_url}: {e}")
            return False
    
    def is_valid_code_file(self, filepath: Path, lang: str) -> bool:
        """Check if file is valid for testing"""
        # Skip test files, configs, builds
        skip_patterns = [
            'test', '__test__', 'spec.', '.test.', '.spec.',
            'config', 'setup', 'build', 'dist', 'node_modules',
            '__pycache__', '.pyc', 'migrations', 'vendor',
            '.min.', 'bundle', 'webpack'  # Skip minified/bundled
        ]
        
        filepath_str = str(filepath).lower()
        if any(pattern in filepath_str for pattern in skip_patterns):
            return False
        
        # Check file extension
        if lang == "python" and not filepath.suffix == ".py":
            return False
        if lang == "javascript" and filepath.suffix not in [".js", ".jsx", ".ts", ".tsx"]:
            return False
        
        # Check file size
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                line_count = len(lines)
                
                if line_count < MIN_LINES or line_count > MAX_LINES:
                    return False
                
                # Check it's not just comments/empty (stricter check)
                content = ''.join(lines)
                code_lines = [
                    l for l in lines 
                    if l.strip() 
                    and not l.strip().startswith(('#', '//', '/*', '*', '"""', "'''"))
                ]
                
                if len(code_lines) < MIN_LINES * 0.6:  # At least 60% real code
                    return False
                
                # Must have some function/class definitions
                has_def = any(
                    keyword in content 
                    for keyword in ['def ', 'class ', 'function ', 'const ', 'let ']
                )
                if not has_def:
                    return False
                
                return True
        except Exception:
            return False
    
    def find_candidate_files(self, repo_path: Path, source_dir: str, lang: str) -> List[Path]:
        """Find all valid code files in repo"""
        candidates = []
        search_path = repo_path / source_dir if source_dir else repo_path
        
        if not search_path.exists():
            print(f"  Warning: {search_path} does not exist")
            return candidates
        
        for filepath in search_path.rglob("*"):
            if filepath.is_file() and self.is_valid_code_file(filepath, lang):
                candidates.append(filepath)
        
        return candidates
    
    def sample_files(self, candidates: List[Path], count: int) -> List[Path]:
        """Randomly sample files"""
        if len(candidates) <= count:
            return candidates
        return random.sample(candidates, count)
    
    def copy_file_to_output(self, source: Path, lang: str, repo_name: str, index: int) -> Dict:
        """Copy file to output directory with sanitized name"""
        # Create sanitized filename
        safe_repo = repo_name.replace("/", "_")
        ext = source.suffix
        output_name = f"{safe_repo}_{index:02d}{ext}"
        output_path = self.output_dir / lang / output_name
        
        # Copy content
        with open(source, 'r', encoding='utf-8', errors='ignore') as src:
            content = src.read()
        
        with open(output_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        # Return metadata
        return {
            "output_file": str(output_path.relative_to(self.output_dir)),
            "original_path": str(source),
            "repo": repo_name,
            "language": lang,
            "lines": len(content.splitlines())
        }
    
    def save_checkpoint(self):
        """Save progress to Drive if enabled"""
        if self.use_drive and self.drive_path:
            checkpoint_path = self.drive_path / "checkpoint.json"
            with open(checkpoint_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            print(f"  💾 Checkpoint saved to {checkpoint_path}")
    
    def generate_dataset(self):
        """Main dataset generation workflow"""
        print("\n" + "="*60)
        print("PHASE 1: GENERATING TEST DATASET (COLAB OPTIMIZED)")
        print("="*60)
        
        # Setup
        self.setup_drive()
        self.setup_directories()
        self.metadata["generation_date"] = datetime.now().isoformat()
        
        temp_repos_dir = Path("temp_repos")
        temp_repos_dir.mkdir(exist_ok=True)
        
        total_files = 0
        
        for lang, repos in TEST_REPOS.items():
            print(f"\n📦 Processing {lang.upper()} repositories...")
            lang_files = 0
            
            for repo_url, source_dir in repos:
                print(f"\n  Repository: {repo_url}")
                
                # Clone repository
                repo_name = repo_url.split('/')[-1]
                repo_path = temp_repos_dir / repo_name
                
                if not self.clone_repo(repo_url, repo_path):
                    continue
                
                # Find candidate files
                candidates = self.find_candidate_files(repo_path, source_dir, lang)
                print(f"  Found {len(candidates)} candidate files")
                
                # Sample files
                sampled = self.sample_files(candidates, FILES_PER_REPO)
                print(f"  Sampled {len(sampled)} files")
                
                # Copy files to output
                repo_metadata = {
                    "url": f"https://github.com/{repo_url}",
                    "source_dir": source_dir,
                    "files_sampled": len(sampled),
                    "files": []
                }
                
                for idx, filepath in enumerate(sampled, 1):
                    file_meta = self.copy_file_to_output(filepath, lang, repo_url, idx)
                    repo_metadata["files"].append(file_meta)
                    self.metadata["files"].append(file_meta)
                    lang_files += 1
                
                self.metadata["repos"][repo_url] = repo_metadata
                
                # Save checkpoint after each repo
                self.save_checkpoint()
            
            print(f"\n  ✓ {lang.upper()}: {lang_files} files collected")
            total_files += lang_files
        
        # Generate statistics
        self.metadata["stats"] = {
            "total_files": total_files,
            "python_files": sum(1 for f in self.metadata["files"] if f["language"] == "python"),
            "javascript_files": sum(1 for f in self.metadata["files"] if f["language"] == "javascript"),
            "total_repos": len(self.metadata["repos"])
        }
        
        # Save metadata
        with open(METADATA_FILE, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        # Copy to Drive if enabled
        if self.use_drive:
            import shutil
            drive_output = self.drive_path / "test_code"
            if drive_output.exists():
                shutil.rmtree(drive_output)
            shutil.copytree(self.output_dir, drive_output)
            print(f"\n💾 Dataset backed up to {drive_output}")
        
        print("\n" + "="*60)
        print("DATASET GENERATION COMPLETE")
        print("="*60)
        print(f"Total files: {total_files}")
        print(f"Python: {self.metadata['stats']['python_files']}")
        print(f"JavaScript: {self.metadata['stats']['javascript_files']}")
        print(f"Metadata saved to: {METADATA_FILE}")
        print("="*60 + "\n")


def main():
    """
    Usage:
    # Local or Colab without Drive persistence
    python dataset_generator.py
    
    # Colab with Drive persistence (recommended)
    python dataset_generator.py --use-drive
    """
    import sys
    use_drive = "--use-drive" in sys.argv or "-d" in sys.argv
    
    random.seed(42)  # Reproducibility
    generator = DatasetGenerator(use_drive=use_drive)
    generator.generate_dataset()


if __name__ == "__main__":
    main()