import pytest
from pydantic import ValidationError
from app.models import Observation

def sample():
    return dict(source_name="Test source", source_url="https://example.org/data",
                source_record_id="abc-1", retrieved_on="2026-11-17",
                district="Salem", feature_type="footway",
                latitude=11.6643, longitude=78.1460)

def test_source_mapped_allowed():
    assert Observation(**sample()).evidence_status == "source_mapped"

def test_field_verified_requires_reviewer():
    with pytest.raises(ValidationError):
        Observation(**{**sample(), "evidence_status":"field_verified"})
