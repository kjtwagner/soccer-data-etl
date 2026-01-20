## ETL Pipeline Notes

### Imputed Observations

Player-game observations may be imputed when a player is unavailable. Imputation is performed upstream in the source Excel file using player-specific averages.

During transformation, imputed rows are identified by detecting non-integer values in numeric performance columns and flagged accordingly.

This allows downstream consumers to:
- Exclude imputed rows
- Analyze observed vs imputed performance
- Apply alternative imputation strategies
