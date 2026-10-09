# Data source

## File
- `raw/pelland_extracted_data.xlsx` is the file `Extracted Data.xlsx` from the Open Science Framework project https://osf.io/6z3xu, saved without any change.
  (Checked: it is byte-for-byte identical to the file inside the OSF download `6z3xu-osfstorage-archive.zip`.)
- The OSF project belongs to the meta-regression by Pelland, Remmert, Robinson, Hinson and Zourdos (2026), *Sports Medicine*, 56(2), 481-505,
  https://doi.org/10.1007/s40279-025-02344-w. The article's data availability statement says the extracted dataset, analysis scripts,
  estimates, plots and supplementary materials are on the OSF at https://osf.io/6z3xu.

## What it contains
- 710 rows x 95 columns, 70 studies, 168 training groups (the article's main models used 67 studies).
- One row = one outcome (hypertrophy or strength measure) in one training group of one study. Values are group averages (pre and post means, group size), not individual people.
- Predictors we use: `frequency.all` (sessions per muscle per week) and `sets.week.all` (hard sets per muscle per week).
- Covariates we use: `weeks`, `age`, `sex.male` (percent male), `train.status`, `n`.
- No numeric protein column. Protein appears only in free-text notes for a dozen or so studies, so protein is not analysed.

## What we did to it (all in `notebooks/DATA200_analysis.ipynb`)
1. Percent change = (post - pre) / pre x 100 for each row.
2. Dropped 60 rows of no-training control groups (frequency 0, sets 0) from the dose-response models.
3. Averaged the measures within each group and outcome, giving one row per group and outcome (233 rows).
4. Dropped 4 rows with missing `sex.male`, leaving 229 (79 hypertrophy, 150 strength).
5. Saved the cleaned table as `processed/analysis_groups.csv`.
