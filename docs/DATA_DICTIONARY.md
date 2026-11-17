# Initial data dictionary

- `source_name`: originating dataset/provider (required)
- `source_url`: direct public source URL (required)
- `source_record_id`: stable source identifier (required; deduplication key with source)
- `retrieved_on`: retrieval date (required)
- `district`: Tamil Nadu district (required; validate against approved canonical district list)
- `feature_type`: footway, sidewalk, crossing, ramp, tactile_paving or other
- `evidence_status`: source_mapped, desk_reviewed or field_verified
- `latitude`, `longitude`: WGS84 coordinates within broad Tamil Nadu bounds
- `width_m`, `surface`, `kerb_ramp`, `tactile_paving`, `obstruction_observed`: null when unknown; never guess
- `reviewer`, `reviewed_on`: mandatory for desk-reviewed and field-verified records

Unknown is not the same as absent. Derived scores must document their formula and evidence requirements.
