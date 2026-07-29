"""Lightweight preprocessing helpers used across pages.

The heavy-duty merge of raw sources into the master dataset lives in
build_master_dataset.py at the project root (run once, offline). This
module only contains small, fast helpers used at render time.
"""
import pandas as pd
import numpy as np


def latest_value_per_country(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Return each country's most recent non-null value for value_col."""
    sub = df.dropna(subset=[value_col]).sort_values("year")
    return sub.groupby("country", as_index=False).last()


def year_over_change(df: pd.DataFrame, value_col: str, start_year: int, end_year: int) -> pd.DataFrame:
    """Compute change in value_col between start_year and end_year per country."""
    start = df[df["year"] == start_year][["country", "iso_code", value_col]].rename(
        columns={value_col: "start_value"})
    end = df[df["year"] == end_year][["country", "iso_code", value_col]].rename(
        columns={value_col: "end_value"})
    merged = start.merge(end, on=["country", "iso_code"]).dropna()
    merged["change"] = merged["end_value"] - merged["start_value"]
    merged["pct_change"] = np.where(
        merged["start_value"] != 0,
        100 * merged["change"] / merged["start_value"],
        np.nan,
    )
    return merged.sort_values("change", ascending=False)


def safe_corr(df: pd.DataFrame, x_col: str, y_col: str):
    """Pearson correlation that gracefully handles missing/insufficient data."""
    from scipy import stats
    sub = df[[x_col, y_col]].dropna()
    if len(sub) < 3:
        return None, None, len(sub)
    r, p = stats.pearsonr(sub[x_col], sub[y_col])
    return r, p, len(sub)
