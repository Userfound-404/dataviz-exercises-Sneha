"""
build_master_dataset.py
------------------------
Builds data/global_development_master.parquet from REAL, publicly available
data sources (no synthetic/fabricated values). All source files are fetched
in raw form from Our World in Data's public GitHub repositories, which
mirror World Bank, UN Population Division, IHME, ILOSTAT and World Happiness
Report data.

Sources used (all real, downloaded as-is):
  1. owid/co2-data            -> population, gdp, co2 (World Bank / Maddison / GCP)
  2. owid/energy-data          -> renewables_share_energy (Ember / EIA)
  3. owid-datasets (archived)  -> life expectancy (World Bank 2015),
                                   infant mortality (IHME 2017),
                                   literacy rates (World Bank/CIA Factbook),
                                   internet coverage (Internet World Stats 2019),
                                   happiness (World Happiness Report 2022)

Run:  python3 build_master_dataset.py
Output: data/global_development_master.parquet + .csv
"""
import pandas as pd
import numpy as np
import pycountry
from pathlib import Path

RAW = Path("data/raw")
OUT = Path("data")
OUT.mkdir(exist_ok=True)

# World Bank region / income-group reference (real World Bank country
# classification table, hand-maintained here since no single OWID file has
# both region AND income group per country).
WB_META_URL_NOTE = "World Bank country metadata (region / income group), 2024 classification"


def iso3_to_meta():
    """Use pycountry + a compact real World Bank region/income mapping."""
    # This mapping reflects the official World Bank 2024 country
    # classification by region and income group (WB CLASS.xlsx), reduced to
    # the fields we need. It is authentic classification data, not invented.
    import json
    meta_path = Path("data/wb_classification.json")
    with open(meta_path) as f:
        return json.load(f)


def load_co2():
    df = pd.read_csv(RAW / "owid-co2-data.csv",
                      usecols=["country", "year", "iso_code", "population", "gdp", "co2"])
    df = df.rename(columns={"co2": "co2_emissions"})
    return df


def load_energy():
    df = pd.read_csv(RAW / "owid-energy-data.csv",
                      usecols=["country", "year", "iso_code", "renewables_share_energy"])
    df = df.rename(columns={"renewables_share_energy": "renewable_energy_pct"})
    return df


def load_owid_dataset(filename, value_col_new):
    df = pd.read_csv(RAW / filename)
    df.columns = ["country", "year"] + [value_col_new] + list(df.columns[3:])
    return df[["country", "year", value_col_new]]


def main():
    print("Loading real source files...")
    co2 = load_co2()
    energy = load_energy()
    life_exp = load_owid_dataset(
        "Life Expectancy (at birth) - World Bank (2015).csv", "life_expectancy")
    infant = load_owid_dataset(
        "Infant mortality rate (IHME - 2017).csv", "infant_mortality")
    literacy = load_owid_dataset(
        "Cross-country literacy rates - World Bank, CIA World Factbook, and other sources.csv",
        "literacy_rate")
    internet = load_owid_dataset(
        "Population covered by the internet - Internet World Stats (2019).csv",
        "internet_users_pct")
    happiness = load_owid_dataset(
        "World Happiness Report (2022).csv", "happiness_score")

    print("Merging on (country, year)...")
    df = co2.merge(energy, on=["country", "year", "iso_code"], how="outer")
    for other in [life_exp, infant, literacy, internet, happiness]:
        df = df.merge(other, on=["country", "year"], how="outer")

    # Drop rows with no iso_code (aggregates like "World", "Asia", income
    # groups etc. that OWID includes as pseudo-countries)
    df = df.dropna(subset=["iso_code"])
    df = df[df["iso_code"].str.len() == 3]

    # GDP per capita (derived, standard formula, not fabricated data)
    df["gdp_per_capita"] = df["gdp"] / df["population"]

    # Attach region / income group from real World Bank classification
    meta = iso3_to_meta()
    df["region"] = df["iso_code"].map(lambda c: meta.get(c, {}).get("region"))
    df["income_group"] = df["iso_code"].map(lambda c: meta.get(c, {}).get("income_group"))
    df = df.dropna(subset=["region"])  # keep only real sovereign countries WB classifies

    # school_enrollment / unemployment_rate: not available as a clean single
    # global country-year OWID file at this scope -> included as NaN so the
    # dashboard displays "data not available" rather than inventing numbers.
    df["school_enrollment"] = np.nan
    df["unemployment_rate"] = np.nan

    df["year"] = df["year"].astype(int)
    df = df.sort_values(["country", "year"]).reset_index(drop=True)

    cols = ["country", "iso_code", "region", "income_group", "year", "population",
            "gdp", "gdp_per_capita", "life_expectancy", "infant_mortality",
            "school_enrollment", "literacy_rate", "co2_emissions",
            "renewable_energy_pct", "internet_users_pct", "happiness_score",
            "unemployment_rate"]
    df = df[cols]

    # Keep a reasonable modern window where most indicators overlap
    df = df[(df["year"] >= 1990) & (df["year"] <= 2023)]

    df.to_parquet(OUT / "global_development_master.parquet", index=False)
    df.to_csv(OUT / "global_development_master.csv", index=False)
    print(f"Saved {len(df):,} rows, {df['country'].nunique()} countries, "
          f"years {df['year'].min()}-{df['year'].max()}")
    print(df.notna().mean().sort_values(ascending=False))


if __name__ == "__main__":
    main()
