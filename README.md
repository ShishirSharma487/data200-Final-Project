# Training Frequency, Weekly Volume and Muscle and Strength Gains

DATA200 Applied Statistical Analysis, group project (Navaraj Thapa, Abdul Sheikh, Shishir Sharma, Prasanna Shakya).

We analyze the open data from the resistance-training meta-regression by Pelland et al. (2026) (OSF: https://osf.io/6z3xu).
We ask whether weekly training frequency and weekly volume (hard sets per muscle) go with bigger gains in muscle size and strength.
The file has no usable protein variable, so the second predictor is weekly volume. See `data/DATA_SOURCE.md`.

## Main findings (group averages, association only)
- Weekly volume goes with muscle growth: about +2.4 percentage points per 10 extra hard sets a week (95% CI 1.1 to 3.7).
- Frequency goes with strength gain: about +2.0 percentage points per extra weekly session (95% CI 0.3 to 3.7).
- Models predict new studies poorly (most variation is between studies).

## Folders
```
data/raw/pelland_extracted_data.xlsx   original file, never edited
data/processed/analysis_groups.csv     cleaned table written by the notebook
data/DATA_SOURCE.md                    where the data come from and what we did to them
notebooks/DATA200_analysis.ipynb       full analysis
app/app.py                             local Streamlit app
results/figures, results/tables        figures and tables written by the notebook
report/                                APA 7 report
```

## How to run
1. Python 3.10 or newer. Optional: `python -m venv .venv` and activate it.
2. `pip install -r requirements.txt`
3. Notebook: `jupyter notebook`, open `notebooks/DATA200_analysis.ipynb`, then Kernel > Restart and Run All (about 4 minutes; the bootstrap is the slow part).
4. App (run from this folder, after the notebook has written `data/processed/analysis_groups.csv`): `python -m streamlit run app/app.py`
