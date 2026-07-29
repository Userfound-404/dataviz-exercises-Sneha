import streamlit as st
from utils.data_loader import get_master_dataset, get_indicator_meta
from utils.preprocessing import year_over_change
from utils.charts import time_series_line, area_chart, slopegraph, animated_scatter

st.set_page_config(page_title="Trends", page_icon="📈", layout="wide")
st.title("📈 Trends")
st.caption("How have indicators evolved over time, and which countries are changing fastest?")

df = get_master_dataset()
meta = get_indicator_meta()

indicator_options = {v["label"]: k for k, v in meta.items()
                      if k not in ("school_enrollment", "unemployment_rate")}
label = st.selectbox("Indicator", list(indicator_options.keys()),
                      index=list(indicator_options.keys()).index("GDP per Capita"))
indicator = indicator_options[label]

year_min, year_max = int(df["year"].min()), int(df["year"].max())
start_year, end_year = st.slider("Year range", year_min, year_max, (2000, year_max))

default_countries = ["United States", "China", "India", "Germany", "Nigeria", "Brazil"]
default_countries = [c for c in default_countries if c in df["country"].unique()]
countries = st.multiselect("Countries", sorted(df["country"].unique()), default=default_countries)

sub = df[(df["country"].isin(countries)) & (df["year"].between(start_year, end_year))]

st.markdown("#### Multi-country trajectory")
d = sub.dropna(subset=[indicator])
if not d.empty:
    fig = time_series_line(d, "year", indicator, color_col="country",
                            title=f"{label} by Country, {start_year}-{end_year}",
                            subtitle=f"Unit: {meta[indicator]['unit']}")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data for the selected countries/indicator/year range.")

st.markdown("#### Cumulative pattern (area chart)")
if not d.empty:
    fig = area_chart(d, "year", indicator, color_col="country",
                      title=f"{label} — Stacked Area View", subtitle="Shows relative contribution across countries.")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown(f"#### Slopegraph: change from {start_year} to {end_year}")
slope_df = year_over_change(df[df["country"].isin(countries)], indicator, start_year, end_year)
if not slope_df.empty:
    fig = slopegraph(slope_df, "start_value", "end_value", "country",
                      f"{label}: {start_year} vs {end_year}",
                      "Green = increase, red = decrease.",
                      start_label=str(start_year), end_label=str(end_year))
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🚀 Fastest-growing (largest % increase)**")
        st.dataframe(slope_df.nlargest(5, "pct_change")[["country", "start_value", "end_value", "pct_change"]],
                     hide_index=True, use_container_width=True)
    with c2:
        st.markdown("**📉 Largest declines**")
        st.dataframe(slope_df.nsmallest(5, "pct_change")[["country", "start_value", "end_value", "pct_change"]],
                     hide_index=True, use_container_width=True)
else:
    st.info("Not enough data to build a slopegraph for this selection.")

st.markdown("---")
st.markdown("#### 🎞️ Animated scatter: GDP per Capita vs. Life Expectancy")
anim_df = df.dropna(subset=["gdp_per_capita", "life_expectancy", "population", "region"])
anim_df = anim_df[anim_df["year"].between(start_year, end_year)]
if not anim_df.empty:
    fig = animated_scatter(anim_df, "gdp_per_capita", "life_expectancy", "population", "region",
                            "country", "year",
                            "GDP per Capita vs. Life Expectancy Over Time",
                            "Bubble size = population, color = region. Press play to see the story unfold.")
    st.plotly_chart(fig, use_container_width=True)
