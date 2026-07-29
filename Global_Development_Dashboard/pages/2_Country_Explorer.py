import streamlit as st
from utils.data_loader import get_master_dataset, get_indicator_meta
from utils.helpers import format_kpi
from utils.charts import time_series_line, radar_chart

st.set_page_config(page_title="Country Explorer", page_icon="🔍", layout="wide")
st.title("🔍 Country Explorer")
st.caption("Deep-dive into a single country's development story — or compare two.")

df = get_master_dataset()
meta = get_indicator_meta()

compare_mode = st.toggle("Compare two countries")

all_countries = sorted(df["country"].dropna().unique())
default_idx = all_countries.index("United States") if "United States" in all_countries else 0

if compare_mode:
    c1, c2 = st.columns(2)
    country_a = c1.selectbox("Country A", all_countries, index=default_idx)
    country_b = c2.selectbox("Country B", all_countries,
                              index=min(default_idx + 1, len(all_countries) - 1))
    countries = [country_a, country_b]
else:
    country = st.selectbox("Select a country", all_countries, index=default_idx,
                            help="Type to search")
    countries = [country]

country_df = df[df["country"].isin(countries)].sort_values("year")

for c in countries:
    latest = country_df[country_df["country"] == c].dropna(
        subset=["population"], how="all").sort_values("year").tail(1)
    if latest.empty:
        continue
    row = latest.iloc[0]
    st.markdown(f"#### 🏳️ {c} — profile ({int(row['year'])})")
    cols = st.columns(4)
    cols[0].metric("Population", format_kpi(row.get("population")))
    cols[1].metric("GDP", "$" + format_kpi(row.get("gdp")))
    cols[2].metric("GDP per Capita", "$" + format_kpi(row.get("gdp_per_capita")))
    cols[3].metric("Life Expectancy", format_kpi(row.get("life_expectancy"), "decimal") + " yrs")
    cols = st.columns(4)
    cols[0].metric("Literacy Rate", format_kpi(row.get("literacy_rate"), "percent"))
    cols[1].metric("CO2 Emissions", format_kpi(row.get("co2_emissions")) + " Mt")
    cols[2].metric("Renewable Energy", format_kpi(row.get("renewable_energy_pct"), "percent"))
    cols[3].metric("Happiness Score", format_kpi(row.get("happiness_score"), "decimal"))

st.markdown("---")
st.markdown("#### 📈 Time-series trends")

indicators = [
    ("gdp_per_capita", "GDP per Capita over Time"),
    ("life_expectancy", "Life Expectancy over Time"),
    ("co2_emissions", "CO2 Emissions over Time"),
    ("population", "Population over Time"),
]
cols = st.columns(2)
for i, (col, title) in enumerate(indicators):
    d = country_df.dropna(subset=[col])
    with cols[i % 2]:
        if d.empty:
            st.info(f"No data available for {meta[col]['label']}.")
            continue
        fig = time_series_line(d, "year", col, color_col="country" if compare_mode else None,
                                title=title, subtitle=f"Unit: {meta[col]['unit']}")
        st.plotly_chart(fig, use_container_width=True)

if not compare_mode:
    st.markdown("---")
    st.markdown("#### 🕸️ How does this country compare to the world average?")
    radar_cols = ["life_expectancy", "gdp_per_capita", "happiness_score",
                  "renewable_energy_pct", "literacy_rate"]
    latest_year = country_df["year"].max()
    c_row = country_df[country_df["year"] == latest_year]
    world_row = df[df["year"] == latest_year]
    if not c_row.empty:
        # Normalize each metric 0-100 relative to the global max for comparability
        cats, c_vals, w_vals = [], [], []
        for col in radar_cols:
            gmax = df[col].max(skipna=True)
            if gmax and gmax > 0 and col in c_row and c_row[col].notna().any():
                cats.append(meta[col]["label"])
                c_vals.append(100 * c_row[col].mean() / gmax)
                w_vals.append(100 * world_row[col].mean(skipna=True) / gmax)
        if cats:
            fig = radar_chart(cats, c_vals, w_vals, countries[0],
                               f"{countries[0]} vs. World Average ({int(latest_year)})",
                               "Each axis scaled 0-100 relative to the global maximum for that indicator.")
            st.plotly_chart(fig, use_container_width=True)
