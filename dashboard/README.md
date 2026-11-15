# Ghana vs Somalia — AFCON Match Intelligence ETL

An end-to-end football data engineering and analytics solution built around Ghana's 2–0 victory over Somalia in the Africa Cup of Nations (AFCON) qualification campaign.

The solution extracts match data from FotMob, transforms and reconciles multiple data sources, produces structured match intelligence datasets, and presents the findings through an interactive Streamlit dashboard.

## Project Overview

**Match:** Ghana vs Somalia  
**Competition:** Africa Cup of Nations Qualification — Group C  
**Date:** 12 November 2026  
**Final Score:** Ghana 2–0 Somalia  
**Primary Data Source:** FotMob

### Objectives

- Extract structured football match data from FotMob.
- Transform raw JSON into analysis-ready datasets.
- Reconcile player appearances, lineups and player statistics.
- Preserve missing and unmatched records instead of making unsupported assumptions.
- Analyse team, player, attacking and defensive performances.
- Build an interactive match intelligence dashboard.
- Establish a reproducible ETL workflow for football analytics.

## Project Architecture

```text
ghana-somalia-afcon-etl/
│
├── data/
│   ├── raw/
│   └── processed/
│       └── match_intelligence/
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── transform_players.py
│   ├── transform_events.py
│   ├── transform_lineups.py
│   ├── reconcile_appearances.py
│   ├── build_reconciled_appearances.py
│   ├── analyse_match.py
│   ├── build_match_timeline.py
│   ├── build_match_intelligence.py
│   └── validate_pipeline.py
│
├── dashboard/
│   └── app.py
│
├── database/
│
├── .streamlit/
│   └── config.toml
│
├── main.py
├── requirements.txt
└── README.md
```

## ETL Workflow

### 1. Extraction

The extraction process retrieves match information from the FotMob match page.

The extracted data includes:

- Match facts
- Team statistics
- Player statistics
- Lineups
- Match events
- Shot map data
- Match momentum and other available match information

Raw match data is stored in JSON format in `data/raw/`.

### 2. Transformation

The raw JSON is transformed into structured CSV datasets.

The transformation process produces:

- Team statistics
- Player statistics
- Player appearances
- Starting lineups and substitutes
- Match events
- Reconciled player appearances

### 3. Data Quality and Reconciliation

A key part of this solution is the reconciliation of player records across FotMob's lineup and player-statistics sources.

The process checks:

- Player identification using match and player IDs.
- Starting players and substitutes.
- Players who entered the match.
- Unused substitutes.
- Missing player-statistics records.
- Unmatched source records.

Missing values are preserved rather than automatically replaced with zero. Unmatched records are retained for investigation instead of being incorrectly assigned to another player.

### 4. Match Analysis

The analysis layer generates structured datasets covering:

- Team performance comparison
- First-half versus second-half performance
- Player performance
- Attacking contributions
- Defensive contributions
- Per-90-minute performance metrics
- Match event timeline
- Consolidated match intelligence

### 5. Match Intelligence Export

The consolidated match intelligence datasets are exported to:

`data/processed/match_intelligence/`

Key outputs:

| Dataset | Records |
|---|---:|
| Match intelligence metrics | 14 |
| Match intelligence timeline | 15 |
| Match intelligence players | 46 |

A JSON match summary is also generated.

## Key Match Findings

### Team Performance

| Metric | Ghana | Somalia |
|---|---:|---:|
| Possession | 76% | 24% |
| Total shots | 23 | 3 |
| Shots on target | 8 | 2 |
| Shots inside the box | 14 | 2 |
| Opposition box touches | 44 | 8 |
| Pass accuracy | 89% | 57% |
| Tackles | 8 | 24 |
| Interceptions | 6 | 8 |
| Clearances | 14 | 18 |
| Blocks | 1 | 5 |

Ghana dominated possession and attacking volume. Somalia recorded more defensive actions, reflecting the greater defensive workload during the match.

### Half-by-Half Analysis

| Metric | Ghana 1H | Ghana 2H | Somalia 1H | Somalia 2H |
|---|---:|---:|---:|---:|
| Possession | 78% | 74% | 22% | 26% |
| Total shots | 8 | 15 | 0 | 3 |
| Shots on target | 4 | 4 | 0 | 2 |
| Shots inside box | 5 | 9 | 0 | 2 |

Ghana increased its attacking volume after half-time, although its shots on target remained unchanged at four.

## Interactive Dashboard

The Streamlit application provides six main sections:

1. Match Overview
2. Team Performance
3. Half-by-Half Analysis
4. Player Intelligence
5. Match Timeline
6. Analyst's Match Report

The dashboard uses Python, Pandas, Plotly and Streamlit, with a consistent green-and-white visual theme.

## Data Quality Validation

The pipeline validation checks include:

- Dataset record counts and structure.
- Duplicate records.
- Match and team identification.
- Player uniqueness.
- Participation classification.
- Appearance reconciliation.
- Preservation of unmatched source records.
- Match event integrity.

The dashboard data quality audit completed with:

**36 checks passed and 0 failed.**

These checks validate the expected dataset structure and selected values; they should not be interpreted as independent verification of every original FotMob statistic.

## Technology Stack

| Area | Technologies |
|---|---|
| Programming | Python |
| Data processing | Pandas, NumPy |
| Data extraction | Requests, BeautifulSoup |
| Visualisation | Plotly, Matplotlib |
| Dashboard | Streamlit |
| Development | VS Code, WSL Ubuntu |
| Version control | Git, GitHub |

## Running the Dashboard

Clone the repository:

```bash
git clone https://github.com/stephen1-hub/ghana-somalia-afcon-etl.git
```

Navigate into the project:

```bash
cd ghana-somalia-afcon-etl
```

Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate
```

Install dependencies:

```bash
uv pip install -r requirements.txt
```

Launch the dashboard:

```bash
streamlit run dashboard/app.py
```

Open the local URL displayed in your terminal.

## Project Limitations

- The analysis depends on the availability and structure of FotMob data.
- Missing player statistics are retained as missing values.
- Some unmatched player records require further source-level investigation.
- Per-90-minute metrics from short appearances require cautious interpretation.
- Defensive actions are not, by themselves, a complete measure of defensive effectiveness.
- The current validation checks do not independently verify every statistic against a second data provider.

## Future Improvements

- Automate match data extraction and scheduled updates.
- Integrate a relational database for historical match storage.
- Expand the analysis to additional AFCON qualification matches.
- Develop reusable match intelligence pipelines.
- Add automated testing and continuous integration.
- Expand player and tactical analysis.
- Introduce additional football data providers where permitted.

## Author

**Stephen Yaw Ayamah**

Aspiring Data Engineer | Football Data Analyst

GitHub: [stephen1-hub](https://github.com/stephen1-hub)

This project demonstrates the application of data engineering, data quality management, football analytics and interactive visualisation to real-world match intelligence.
