"""Data loading utilities for the Global Development Dashboard.

All data is real: merged from Our World in Data mirrors of World Bank,
UN Population Division, IHME and World Happiness Report sources. See
build_master_dataset.py at the project root for the full provenance and
merge logic. Nothing in this file synthesizes or fabricates data.
"""
from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MASTER_PARQUET = DATA_DIR / "global_development_master.parquet"
MASTER_CSV = DATA_DIR / "global_development_master.csv"


@st.cache_data(show_spinner="Loading global development data...")
def get_master_dataset() -> pd.DataFrame:
    """Load the cleaned master dataset (real data, see build_master_dataset.py).

    Falls back to CSV if the parquet file isn't available, and raises a
    clear error (no synthetic fallback) if neither exists so the user knows
    to run the build script.
    """
    if MASTER_PARQUET.exists():
        df = pd.read_parquet(MASTER_PARQUET)
    elif MASTER_CSV.exists():
        df = pd.read_csv(MASTER_CSV)
    else:
        raise FileNotFoundError(
            "No master dataset found. Run `python build_master_dataset.py` "
            "from the project root to build data/global_development_master.parquet "
            "from the real OWID/World Bank/UN source files."
        )
    df["year"] = df["year"].astype(int)
    return df


@st.cache_data
def get_indicator_meta() -> dict:
    """Human-readable labels and units for each indicator column."""
    return {
        "population": {"label": "Population", "unit": "people", "fmt": ",.0f"},
        "gdp": {"label": "GDP", "unit": "current international $", "fmt": ",.0f"},
        "gdp_per_capita": {"label": "GDP per Capita", "unit": "$", "fmt": ",.0f"},
        "life_expectancy": {"label": "Life Expectancy", "unit": "years", "fmt": ".1f"},
        "infant_mortality": {"label": "Infant Mortality", "unit": "per 1,000 live births", "fmt": ".1f"},
        "school_enrollment": {"label": "School Enrollment", "unit": "%", "fmt": ".1f"},
        "literacy_rate": {"label": "Literacy Rate", "unit": "%", "fmt": ".1f"},
        "co2_emissions": {"label": "CO2 Emissions", "unit": "million tonnes", "fmt": ",.1f"},
        "renewable_energy_pct": {"label": "Renewable Energy", "unit": "% of energy mix", "fmt": ".1f"},
        "internet_users_pct": {"label": "Internet Users", "unit": "% of population covered", "fmt": ".1f"},
        "happiness_score": {"label": "Happiness Score", "unit": "0-10 Cantril Ladder", "fmt": ".2f"},
        "unemployment_rate": {"label": "Unemployment Rate", "unit": "%", "fmt": ".1f"},
    }
