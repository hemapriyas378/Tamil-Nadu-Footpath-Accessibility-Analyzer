
# Tamil Nadu Footpath Accessibility Analyzer

## 1. Project Overview

The Tamil Nadu Footpath Accessibility Analyzer is a geospatial data analysis project designed to examine mapped pedestrian infrastructure across all 38 districts of Tamil Nadu.

The project focuses on identifying and analyzing footways, sidewalks, and pedestrian crossings using OpenStreetMap data.

## 2. Objectives

- Collect mapped pedestrian infrastructure data across 38 districts.
- Examine the availability of accessibility-related attributes.
- Analyze district-wise infrastructure distribution.
- Calculate evidence-based accessibility indicators.
- Visualize mapped infrastructure using interactive maps.
- Help identify gaps in available pedestrian infrastructure data.

## 3. Data Source

Primary source: OpenStreetMap (OSM).

Data collection method: Overpass API.

Collected information includes:
- OSM element type and ID
- District name
- Feature type
- Latitude and longitude
- Highway classification
- Footway and sidewalk tags
- Surface information
- Width information
- Wheelchair information
- Tactile paving information
- Kerb information

## 4. Study Area

The study covers all 38 districts of Tamil Nadu, India.

District boundaries were used to identify the administrative areas for data collection.

## 5. Data Processing Workflow

1. Collect district boundary information.
2. Match all 38 districts with their boundary relations.
3. Retrieve mapped infrastructure through Overpass API.
4. Extract relevant OSM attributes.
5. Consolidate district records.
6. Validate identifiers and coordinates.
7. Remove invalid and duplicate records.
8. Perform exploratory data analysis.
9. Calculate accessibility evidence indicators.
10. Generate district-wise visualizations.

## 6. Dataset Summary

- Total cleaned records: 5,765
- Districts represented: 38
- Footway records: 3,888
- Crossing records: 1,406
- Sidewalk records: 471
- Synthetic records added: 0

## 7. Accessibility Attributes

The analysis considers six attributes:

- Width
- Surface
- Wheelchair
- Tactile paving
- Kerb
- Sidewalk

Missing attributes are treated as unknown rather than automatically classified as inaccessible.

## 8. Accessibility Evidence Scoring

The project uses a weighted evidence-based scoring approach.

| Attribute | Weight |
|---|---:|
| Wheelchair | 30 |
| Width | 20 |
| Surface | 15 |
| Kerb | 15 |
| Tactile paving | 10 |
| Sidewalk | 10 |

The score is calculated using available attribute evidence and normalized by the total weight of the attributes with known information.

The score represents mapped evidence, not a certified accessibility rating.

## 9. Exploratory Data Analysis

The project performs:
- District-wise record distribution
- Feature-type distribution
- Accessibility attribute coverage
- District-wise comparison
- Missing-value analysis

## 10. Technology Stack

- Python
- Pandas
- FastAPI
- HTML
- CSS
- JavaScript
- Leaflet.js
- Chart.js
- OpenStreetMap
- Overpass API

## 11. Limitations

- OpenStreetMap data may be incomplete.
- Missing tags do not establish that infrastructure is inaccessible.
- Mapped records are not equivalent to a field survey.
- Evidence scores depend on the availability and interpretation of mapped attributes.
- District comparisons must consider differences in data coverage.

## 12. Expected Outcome

An interactive district-wise analytical platform that presents mapped pedestrian infrastructure, accessibility attribute coverage, evidence scores, and geospatial visualizations across Tamil Nadu.
