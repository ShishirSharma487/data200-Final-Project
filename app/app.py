"""Local Streamlit app for the DATA200 group project.

Run from the project folder:
    python -m streamlit run app/app.py

"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "analysis_groups.csv"
RESULTS = ROOT / "results" / "tables" / "results.json"
BLUE, NAVY = "#1E63D6", "#0A2540"
COV = "w_c + age_c + male_c + trained"
FORMULA = {"Hypertrophy": f"pct_change ~ f_c + s_c + {COV}",            # Model 2
           "Strength": f"pct_change ~ f_c + s_c + f_c:s_c + {COV}"}     # Model 3

st.set_page_config(page_title="Frequency, volume and gains", layout="wide")
st.markdown(f"""<style>
h1, h2, h3 {{ color: {NAVY}; }}
div[data-testid="stMetricValue"] {{ color: {BLUE}; }}
</style>""", unsafe_allow_html=True)


@st.cache_data
def load():
    g = pd.read_csv(DATA)
    out = {}
    for o in ["Hypertrophy", "Strength"]:
        x = g[g["outcome"] == o].copy().reset_index(drop=True)
        mu = {"freq": x["freq"].mean(), "sets": x["sets"].mean(), "weeks": x["weeks"].mean(),
              "age": x["age"].mean(), "male": x["male"].mean() / 100}
        x["f_c"] = x["freq"] - mu["freq"]
        x["s_c"] = (x["sets"] - mu["sets"]) / 10
        x["w_c"] = x["weeks"] - mu["weeks"]
        x["age_c"] = x["age"] - mu["age"]
        x["male_c"] = x["male"] / 100 - mu["male"]
        m = smf.wls(FORMULA[o], x, weights=x["n"]).fit(cov_type="cluster", cov_kwds={"groups": x["study"]}, use_t=True)
        out[o] = {"model": m, "mu": mu, "data": x}
    return out


def make_row(o, fit, freq, sets, weeks, age, male, trained):
    mu = fit[o]["mu"]
    return pd.DataFrame([{"f_c": freq - mu["freq"], "s_c": (sets - mu["sets"]) / 10, "w_c": weeks - mu["weeks"],
                          "age_c": age - mu["age"], "male_c": male / 100 - mu["male"], "trained": trained}])


def predict(o, fit, **kw):
    sf = fit[o]["model"].get_prediction(make_row(o, fit, **kw)).summary_frame()
    return float(sf["mean"].iloc[0]), float(sf["mean_ci_lower"].iloc[0]), float(sf["mean_ci_upper"].iloc[0])


fit = load()
cv = json.load(open(RESULTS))["cv"] if RESULTS.exists() else None
rmse = {"Hypertrophy": cv["Hypertrophy"]["M2"]["cv_rmse"], "Strength": cv["Strength"]["M3"]["cv_rmse"]} if cv else {}

st.title("Training frequency, weekly volume and gains")
st.caption("DATA200 group project · Navaraj Thapa, Abdul Sheikh, Shishir Sharma, Prasanna Shakya · "
           "Data: Pelland et al. (2026) open data on the Open Science Framework (https://osf.io/6z3xu)")

with st.sidebar:
    st.header("Training plan of a group")
    freq = st.slider("Sessions per muscle per week", 1.0, 6.0, 2.0, 0.5)
    sets = st.slider("Hard sets per muscle per week", 2, 40, 12)
    weeks = st.slider("Length of the training period (weeks)", 4, 32, 10)
    age = st.slider("Average age (years)", 18, 46, 24)
    male = st.slider("Percent male in the group", 0, 100, 85)
    status = st.radio("Training status", ["Untrained", "Trained"], horizontal=True)
    trained = 1 if status == "Trained" else 0
    st.markdown("---")
    st.caption("Every prediction is for the **average of a group** in a published training study, not for one person.")

kw = dict(freq=freq, sets=sets, weeks=weeks, age=age, male=male, trained=trained)
tab1, tab2, tab3 = st.tabs(["Prediction", "Explore the effects", "Data and model"])

with tab1:
    c1, c2 = st.columns(2)
    for col, o, unit in [(c1, "Hypertrophy", "muscle size"), (c2, "Strength", "strength")]:
        p, lo, hi = predict(o, fit, **kw)
        with col:
            st.subheader(f"Predicted {unit} gain")
            st.metric("Average change", f"{p:.1f}%")
            st.write(f"95% confidence interval for the average group: **{lo:.1f}% to {hi:.1f}%**")
            if rmse:
                st.write(f"For a **new study** the typical miss is about **±{rmse[o]:.1f} points** (cross-validated error), "
                         "so treat the number as a rough guide.")
    x_h, x_s = fit["Hypertrophy"]["data"], fit["Strength"]["data"]
    warn = []
    if freq > 4: warn.append("More than 4 sessions per muscle per week: only a handful of groups are this high, so this is extrapolation.")
    if sets > 38: warn.append("Above 38 sets per muscle per week the data stop. Treat this as extrapolation.")
    if freq < 1.5 and sets > 20: warn.append("Low frequency with high volume is rare in the data.")
    for w in warn: st.warning(w)
    st.info("Hypertrophy uses Model 2 (frequency + weekly sets + covariates). Strength uses Model 3, which adds the "
            "frequency × weekly sets interaction. Both are weighted by group size with study-clustered standard errors.")

with tab2:
    which = st.radio("Show", ["Effect of frequency", "Effect of weekly sets"], horizontal=True)
    rows = []
    if which == "Effect of frequency":
        grid = np.arange(1.0, 4.01, 0.25)
        for o in ["Hypertrophy", "Strength"]:
            for v in grid:
                p, lo, hi = predict(o, fit, **{**kw, "freq": float(v)}); rows.append((o, v, p, lo, hi))
        xl = "Sessions per muscle per week"
    else:
        grid = np.arange(2, 39, 2)
        for o in ["Hypertrophy", "Strength"]:
            for v in grid:
                p, lo, hi = predict(o, fit, **{**kw, "sets": float(v)}); rows.append((o, v, p, lo, hi))
        xl = "Hard sets per muscle per week"
    df = pd.DataFrame(rows, columns=["outcome", "x", "pred", "low", "high"])
    for o in ["Hypertrophy", "Strength"]:
        st.markdown(f"**{o}**")
        st.line_chart(df[df.outcome == o].set_index("x")[["low", "pred", "high"]].rename(
            columns={"low": "95% low", "pred": "predicted change (%)", "high": "95% high"}),
            x_label=xl, y_label="Change (%)", color=["#9DBBE8", BLUE, "#9DBBE8"], height=260)
    st.caption("Other settings stay as in the sidebar. Bands are 95% confidence intervals for the average group.")

with tab3:
    st.subheader("What the data are")
    st.write("Each row is the average of one published training group (one row per group and outcome). "
             f"Hypertrophy: {len(x_h)} groups from {x_h['study'].nunique()} studies. "
             f"Strength: {len(x_s)} groups from {x_s['study'].nunique()} studies. "
             "Outcomes are percent change from the group's starting average. Groups that did not train are left out.")
    st.subheader("Model coefficients (percentage points)")
    names = {"Intercept": "Intercept (typical group)", "f_c": "Per extra session per week", "s_c": "Per extra 10 weekly sets",
             "f_c:s_c": "Frequency × sets (per 10 sets)", "w_c": "Per extra week of training", "age_c": "Per extra year of age",
             "male_c": "Share male (0 to 1)", "trained": "Trained group (vs untrained)"}
    for o in ["Hypertrophy", "Strength"]:
        m = fit[o]["model"]; ci = m.conf_int()
        t = pd.DataFrame({"b": m.params, "95% low": ci[0], "95% high": ci[1], "p": m.pvalues}).round(3)
        t.index = [names.get(i, i) for i in t.index]
        st.markdown(f"**{o}** (R² = {m.rsquared:.2f})"); st.dataframe(t)
    st.subheader("Heads Up")
    st.markdown("""
- The data are **group averages from published studies**, so results describe groups, not individuals.
- They show **association, not cause**. Studies chose their own frequency and volume.
- Most of the variation lies **between studies**, so predictions for a new study are rough.
- The file has **no protein variable**, so this app does not cover protein.
""")
