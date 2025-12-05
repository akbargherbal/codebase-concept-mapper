from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Implementation:
    file_path: str
    identifier: Optional[str]
    line_start: int
    line_end: int
    code_snippet: str
    confidence: str
    pattern_type: str
    evidence: str
    added_at: str

@dataclass
class Concept:
    display_name: str
    definition: str
    implementations: List[Implementation] = field(default_factory=list)

@dataclass
class Metadata:
    project: str
    version: str
    created_at: Optional[str] = None
    last_updated: Optional[str] = None

@dataclass
class ConceptMap:
    metadata: Metadata
    concepts: Dict[str, Concept] = field(default_factory=dict)