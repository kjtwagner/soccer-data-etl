# Soccer Competition Data Pipeline

This project implements an ETL pipeline that ingests season-long small-sided soccer competition data from Excel and loads it into a normalized relational database for analysis.

## Data
The source data consists of manually tracked practice-level game results, including randomized teams, player participation, goals scored, and attendance-based point adjustments.

### Missing Data & Imputation

When players missed a game due to class, injury, or illness, their individual season-average goals and points were used to fill the missing observation.

Imputed values are identifiable because they are non-integer values in goal and team-point fields. Any observed data, by nature, was an integer. All imputed rows are explicitly flagged in the ETL pipeline via an `is_imputed` column to preserve data provenance.


## Tech Stack
- Python (pandas)
- SQL (PostgreSQL)
- GitHub Projects for task tracking?

## Project Status
Schema design and data audit in progress.
