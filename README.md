# North Carolina Redistricting: Racial Dislocation Analysis (2022-2025)

This repository contains code and data for analyzing racial dislocation in North Carolina congressional districts across multiple redistricting plans (2022, 2024, and 2025 maps). And yes, this is a shamelessly AI generated readme, though I did go through and apply a few edits. :)

## Project Overview

This project measures **racial dislocation** — a metric that quantifies the extent to which voters are grouped into districts with racial compositions that differ from their geographic neighborhoods. The analysis focuses on Any Part Black voters in North Carolina and examines how different redistricting plans affect the concentration or dilution of Black voting power.

### What is Racial Dislocation?

Racial dislocation is calculated as the difference between:

- The share of Any Part Black voters in a person's congressional district
- The share of Any Part Black voters among their k-nearest neighbors

**Positive values** indicate racial concentration (or "packing") — voters are in districts with higher minority representation than their neighborhood.

**Negative values** indicate racial dilution (or "cracking") — voters are in districts with lower minority representation than their neighborhood.

## Repository Structure

```
├── 00_source_data/                   # Raw data files
│   ├── cbsa_2020/                    # Core-Based Statistical Area shapefiles
│   ├── district-shapes_*/            # Congressional district boundaries (2022, 2024, 2025)
│   ├── election_data/                # NC election results by precinct
│   └── nhgis_blocks_2020_raceonly/   # Census block data with demographics
├── 10_code/
│   ├── 00_prep_district_maps/   # District boundary preparation
│   ├── 10_race/                 # Racial dislocation analysis
│   │   ├── 00_calc_and_save_knn_race.py      # Calculate k-nearest neighbors
│   │   ├── 10_calc_dislocation_race.py       # Calculate dislocation scores
│   │   ├── 35_analyze_dislocation_by_voter_triad.py  # Piedmont Triad maps
│   │   ├── 37_analyze_dislocation_by_voter_dist1.py  # District 1 & 3 maps
│   │   ├── 45_compare_d1d3_2024v2025.py              # Districts 1 & 3 distributional comparison
│   │   ├── 47_compare_statewide_2022_2025.py # Statewide comparison
│   │   └── 50_table_race.py                   # Summary tables
├── 20_intermediate_data/    # Processed data files
│   ├── nc_knn_*_race.geojson             # KNN calculations
│   ├── nc_dislocation_*_race.geojson     # Dislocation scores by map
│   └── ncdistricts_*.geojson             # Cleaned district boundaries
└── 30_results/              # Output figures and tables
```

### Data Processing Pipeline

1. **Voter Data Preparation** (`00_calc_and_save_knn_race.py`)
   - Loads Census block-level demographic data (2020)
   - Samples 2% of voting-age population (VAP) for computational efficiency
   - Calculates k-nearest neighbors where k = total voters / 14 districts

2. **Dislocation Calculation** (`10_calc_dislocation_race.py`)
   - For each map (2022, 2024, 2025), assigns voters to congressional districts
   - Calculates racial dislocation: district racial composition - neighborhood racial composition
   - Outputs georeferenced point data with dislocation scores

3. **Analysis & Visualization** (files 35-50)
   - Creates density plots showing distribution of dislocation scores
   - Generates maps visualizing dislocation by geography
   - Compares individual-level changes between redistricting plans
   - Produces summary statistics by district and demographic group

## Key Findings

The analysis examines:

- **Geographic patterns**: Focus on Districts 1 and 3, eastern North Carolina, and the Piedmont Triad
- **Temporal changes**: How dislocation shifted from 2022 → 2024 → 2025 maps
- **Racial disparities**: Differences in dislocation for Black vs. Non-Black voters
- **District-level metrics**: Mean and median dislocation by district

## Dependencies

- `geopandas` - Spatial data handling
- `pandas` - Data manipulation
- `matplotlib` - Visualization
- `seaborn` - Statistical plotting
- `partisan_dislocation` - Custom dislocation calculation library
- `numpy` - Numerical computing

## Usage

To reproduce the analysis:

```bash
# 0. Clean up census data
python 10_code/00_prep_district_maps/10_add_demographics.py

# 1. Calculate k-nearest neighbors (slow)
python 10_code/10_race/00_calc_and_save_knn_race.py

# 2. Calculate dislocation scores for each map
python 10_code/10_race/10_calc_dislocation_race.py

# 3. Generate visualizations and comparisons
python 10_code/10_race/35_analyze_dislocation_by_voter_triad.py
python 10_code/10_race/45_compare_d1d3_2024v2025.py
python 10_code/10_race/47_compare_statewide_2022_2025.py

# 4. Create summary tables
python 10_code/10_race/50_table_race.py
```

## Output

Results are saved to `30_results/` including:

- High-resolution maps (600 DPI) showing voter-level dislocation
- Density plots comparing dislocation distributions across maps
- Summary tables of mean dislocation by district and demographic group

## Notes

- Analysis uses 2% sample of VAP for computational efficiency
- Projection: NAD83 / North Carolina (EPSG:32119) for accurate distance calculations
- "Any Part Black" includes individuals who identify as Black alone or in combination with other races

## Contact

<nick@nickeubank.com>
