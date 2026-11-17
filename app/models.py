from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, HttpUrl, model_validator

class Observation(BaseModel):
    source_name: str = Field(min_length=2, max_length=120)
    source_url: HttpUrl
    source_record_id: str = Field(min_length=1, max_length=160)
    retrieved_on: date
    district: str = Field(min_length=2, max_length=80)
    feature_type: Literal["footway", "sidewalk", "crossing", "ramp", "tactile_paving", "other"]
    evidence_status: Literal["source_mapped", "desk_reviewed", "field_verified"] = "source_mapped"
    latitude: float = Field(ge=8.0, le=14.0)
    longitude: float = Field(ge=76.0, le=81.0)
    width_m: float | None = Field(default=None, ge=0, le=20)
    surface: str | None = None
    kerb_ramp: bool | None = None
    tactile_paving: bool | None = None
    obstruction_observed: bool | None = None
    reviewer: str | None = None
    reviewed_on: date | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def require_review_details(self):
        if self.evidence_status != "source_mapped" and (not self.reviewer or not self.reviewed_on):
            raise ValueError("Reviewed/verified records require reviewer and reviewed_on.")
        return self
