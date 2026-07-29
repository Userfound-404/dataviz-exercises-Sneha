import streamlit as st
from utils.data_loader import get_master_dataset, get_indicator_meta
from utils.charts import choropleth_world, bubble_map, top_n_bar

st.set_page_config(page_title="Geographic Analysis", page_icon="🗺️", layout="wide")
st.title("🗺️ Geographic Analysis")
st.caption("Where in the world are indicators highest and lowest?")

df = get_master_dataset()
meta = get_indicator_meta()

geo_indicators = ["gdp_per_capita", "life_expectancy", "co2_emissions",
                   "renewable_energy_pct", "internet_users_pct"]
label = st.selectbox("Indicator", [meta[k]["label"] for k in geo_indicators])
indicator = [k for k in geo_indicators if meta[k]["label"] == label][0]

c1, c2 = st.columns(2)
year = c1.slider("Year", int(df["year"].min()), int(df["year"].max()), int(df["year"].max()))
regions = sorted(df["region"].dropna().unique())
sel_regions = c2.multiselect("Region", regions, default=[])

year_df = df[df["year"] == year]
if sel_regions:
    year_df = year_df[year_df["region"].isin(sel_regions)]

st.markdown(f"#### {label} — World Map, {year}")
map_df = year_df.dropna(subset=[indicator])
if not map_df.empty:
    fig = choropleth_world(map_df, indicator, label, f"{label} by Country, {year}",
                            f"Unit: {meta[indicator]['unit']}")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available for this indicator/year/region.")

st.markdown(f"#### {label} — Bubble Map (sized by population)")
bubble_df = year_df.dropna(subset=[indicator, "population"])
if not bubble_df.empty:
    fig = bubble_map(bubble_df, "population", indicator, "country",
                      f"Population Bubbles Colored by {label}, {year}",
                      "Bubble size = population.")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("#### Regional ranking")
regional_avg = year_df.dropna(subset=[indicator]).groupby("region", as_index=False)[indicator].mean()
if not regional_avg.empty:
    fig = top_n_bar(regional_avg, "region", indicator, len(regional_avg),
                     f"Average {label} by Region, {year}",
                     "Regions ranked from highest to lowest average.")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Geographic clustering often reflects shared history, trade "
        "linkages, and climate — not just current policy choices."
    )
