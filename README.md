# Tamil Nadu Footpath Accessibility Analyzer

A district-wise geospatial data analysis platform for exploring mapped pedestrian infrastructure and accessibility-related information across all 38 districts of Tamil Nadu, India.

## Project Overview

The Tamil Nadu Footpath Accessibility Analyzer collects and analyzes pedestrian infrastructure data from OpenStreetMap (OSM). It provides interactive maps, district-wise comparisons, attribute coverage analysis, and evidence-based accessibility indicators.

The project focuses on footways, sidewalks, and pedestrian crossings.

## Key Features

- Data collection across 38 Tamil Nadu districts
- OpenStreetMap data integration through Overpass API
- Dataset validation and cleaning
- District-wise infrastructure analysis
- Accessibility attribute coverage analysis
- Evidence-based scoring indicators
- Interactive infrastructure maps
- District-wise comparison charts
- Infrastructure record filtering

## Dataset Summary

| Metric | Count |
|---|---:|
| Districts represented | 38 |
| Cleaned records | 5,765 |
| Footways | 3,888 |
| Crossings | 1,406 |
| Sidewalks | 471 |

No synthetic records were added to the collected dataset.

## Accessibility Attributes

The analysis considers:

- Width
- Surface
- Wheelchair
- Tactile paving
- Kerb
- Sidewalk

Missing information is treated as unknown, not as proof of inaccessibility.

## Technology Stack

**Backend:** Python, FastAPI, Pandas

**Frontend:** HTML, CSS, JavaScript

**Mapping:** Leaflet.js, OpenStreetMap

**Charts:** Chart.js

**Data Source:** OpenStreetMap, Overpass API

## Project Structure

```text
TN_Footpath_Accessibility_Analyzer/
│
├── app/
│   ├── accessibility_scoring.py
│   ├── clean_dataset.py
│   ├── coverage_analysis.py
│   ├── district_comparison.py
│   ├── district_osm_collector.py
│   ├── eda_analysis.py
│   ├── final_data_audit.py
│   ├── geospatial_analysis.py
│   ├── osm_processor.py
│   ├── validate_dataset.py
│   └── web_app.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docs/
│   ├── DATA_SOURCES.md
│   └── PROJECT_METHODOLOGY.md
│
├── static/
│   ├── style.css
│   └── script.js
│
├── templates/
│   └── index.html
│
├── tests/
│
├── README.md
└── requirements.txt
```

## Running the Project

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd TN_Footpath_Accessibility_Analyzer
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the FastAPI application

```bash
uvicorn app.web_app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Project Limitations

- OpenStreetMap coverage varies across districts.
- Mapped infrastructure does not guarantee physical accessibility.
- Missing tags indicate unavailable information.
- Evidence scores are not certified accessibility ratings.
- Field verification is needed to confirm real-world conditions.

## Future Enhancements

- Improve geographic accuracy using district boundary polygons.
- Expand verified public data sources.
- Improve accessibility assessment using applicable standards.
- Add field-survey data integration.
- Expand data coverage through additional validated collection.

## Data Attribution

This project uses OpenStreetMap data.

© OpenStreetMap contributors.

https://www.openstreetmap.org/copyright

## Project Purpose

To support data-driven exploration of pedestrian infrastructure and accessibility-related information across Tamil Nadu.
