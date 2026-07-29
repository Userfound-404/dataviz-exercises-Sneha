"""Global sidebar filters, KPI formatting, and CSV download helpers."""
import streamlit as st
import pandas as pd


def format_kpi(value, kind="number"):
    """Human-friendly K/M/B/T formatting for large numbers."""
    if value is None or pd.isna(value):
        return "N/A"
    if kind == "percent":
        return f"{value:,.1f}%"
    if kind == "decimal":
        return f"{value:,.2f}"
    abs_v = abs(value)
    if abs_v >= 1e12:
        return f"{value/1e12:,.2f}T"
    if abs_v >= 1e9:
        return f"{value/1e9:,.2f}B"
    if abs_v >= 1e6:
        return f"{value/1e6:,.2f}M"
    if abs_v >= 1e3:
        return f"{value/1e3:,.1f}K"
    return f"{value:,.1f}"


def _reset_filters():
    for k in list(st.session_state.keys()):
        if k.startswith("flt_"):
            del st.session_state[k]


def apply_global_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render the cascading global sidebar and return the filtered dataframe.

    Filters: Year, Region, Country, Income Group, Population range, GDP range.
    Selecting a region narrows the country options (cascading).
    """
    st.sidebar.header("🔎 Global Filters")

    year_min, year_max = int(df["year"].min()), int(df["year"].max())
    year = st.sidebar.slider("Year", year_min, year_max, year_max, key="flt_year")

    year_df = df[df["year"] == year]

    regions = sorted(year_df["region"].dropna().unique().tolist())
    sel_regions = st.sidebar.multiselect("Region", regions, default=[], key="flt_region")

    region_df = year_df if not sel_regions else year_df[year_df["region"].isin(sel_regions)]

    income_groups = sorted(region_df["income_group"].dropna().unique().tolist())
    sel_income = st.sidebar.multiselect("Income Group", income_groups, default=[], key="flt_income")

    income_df = region_df if not sel_income else region_df[region_df["income_group"].isin(sel_income)]

    countries = sorted(income_df["country"].dropna().unique().tolist())
    sel_countries = st.sidebar.multiselect(
        "Country (cascades with Region/Income Group above)", countries, default=[], key="flt_country")

    country_df = income_df if not sel_countries else income_df[income_df["country"].isin(sel_countries)]

    if len(country_df) and country_df["population"].notna().any():
        pop_min = float(country_df["population"].min(skipna=True) or 0)
        pop_max = float(country_df["population"].max(skipna=True) or 1)
        pop_range = st.sidebar.slider(
            "Population Range", pop_min, pop_max, (pop_min, pop_max), key="flt_pop")
    else:
        pop_range = None

    if len(country_df) and country_df["gdp"].notna().any():
        gdp_min = float(country_df["gdp"].min(skipna=True) or 0)
        gdp_max = float(country_df["gdp"].max(skipna=True) or 1)
        gdp_range = st.sidebar.slider(
            "GDP Range ($)", gdp_min, gdp_max, (gdp_min, gdp_max), key="flt_gdp")
    else:
        gdp_range = None

    filtered = country_df.copy()
    if pop_range:
        filtered = filtered[
            filtered["population"].between(pop_range[0], pop_range[1]) | filtered["population"].isna()]
    if gdp_range:
        filtered = filtered[filtered["gdp"].between(gdp_range[0], gdp_range[1]) | filtered["gdp"].isna()]

    st.sidebar.markdown(f"**{filtered['country'].nunique()} countries selected**")

    st.sidebar.button("↺ Reset Filters", on_click=_reset_filters)

    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button(
        "⬇️ Download filtered data (CSV)", data=csv_bytes,
        file_name=f"global_development_filtered_{year}.csv", mime="text/csv")

    st.sidebar.caption(
        "Data: World Bank, UN Population Division, IHME, World Happiness "
        "Report — via Our World in Data. See README for full source list.")

    return filtered
