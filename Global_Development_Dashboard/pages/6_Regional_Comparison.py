import streamlit as st
from utils.data_loader import get_master_dataset
from utils.charts import grouped_bar, stacked_bar, box_by_region, heatmap, treemap

st.set_page_config(page_title="Regional Comparison", page_icon="🌐", layout="wide")
st.title("🌐 Regional Comparison")
st.caption("Which regions lead — and lag — on key development indicators?")

df = get_master_dataset()
year = st.slider("Year", int(df["year"].min()), int(df["year"].max()), int(df["year"].max()))
year_df = df[df["year"] == year]

st.markdown("#### GDP per Capita & Life Expectancy by Region")
grouped = year_df.groupby("region", as_index=False).agg(
    gdp_per_capita=("gdp_per_capita", "mean"), life_expectancy=("life_expectancy", "mean"))
grouped = grouped.dropna()
if not grouped.empty:
    fig = grouped_bar(grouped, "region", ["gdp_per_capita", "life_expectancy"],
                       "GDP per Capita vs. Life Expectancy by Region",
                       "Two indicators side-by-side per region.")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("#### CO2 Emissions & Renewable Energy by Region")
stacked = year_df.groupby("region", as_index=False).agg(
    co2_emissions=("co2_emissions", "mean"), renewable_energy_pct=("renewable_energy_pct", "mean"))
stacked = stacked.dropna()
if not stacked.empty:
    fig = stacked_bar(stacked, "region", ["co2_emissions", "renewable_energy_pct"],
                       "Average CO2 Emissions & Renewable Share by Region",
                       "Stacked view highlights the environmental trade-off across regions.")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("#### GDP per Capita Distribution by Region (Box Plot)")
box_df = year_df.dropna(subset=["gdp_per_capita", "region"])
if not box_df.empty:
    fig = box_by_region(box_df, "region", "gdp_per_capita",
                         "GDP per Capita Spread by Region",
                         "Box shows median, quartiles, and outlier countries.")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("#### Regional Averages Heatmap")
heat_cols = ["gdp", "gdp_per_capita", "life_expectancy", "happiness_score", "co2_emissions"]
heat_df = year_df.groupby("region")[heat_cols].mean().dropna(how="all")
if not heat_df.empty:
    fig = heatmap(heat_df, "Regional Averages Across Key Indicators",
                  "Normalize mentally by column — units differ across metrics.")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("#### GDP Treemap (Region → Country)")
treemap_df = year_df.dropna(subset=["gdp", "region", "country"])
if not treemap_df.empty:
    fig = treemap(treemap_df, ["region", "country"], "gdp",
                  f"Global GDP Composition, {year}",
                  "Box size = share of GDP. Click to drill into a region.")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("#### 🏆 Quick answers")
c1, c2, c3, c4 = st.columns(4)
if not grouped.empty:
    c1.metric("Highest GDP/Capita region", grouped.loc[grouped["gdp_per_capita"].idxmax(), "region"])
    c2.metric("Highest life expectancy region", grouped.loc[grouped["life_expectancy"].idxmax(), "region"])
happy = year_df.groupby("region")["happiness_score"].mean().dropna()
if not happy.empty:
    c3.metric("Happiest region", happy.idxmax())
emis = year_df.groupby("region")["co2_emissions"].mean().dropna()
if not emis.empty:
    c4.metric("Lowest emissions region", emis.idxmin())
