import pytest
from src.domain.models import ConceptMap, Metadata

@pytest.fixture
def empty_concept_map():
    """A fixture for a new, empty ConceptMap object."""
    return ConceptMap(metadata=Metadata(project="test-project", version="1.0"))