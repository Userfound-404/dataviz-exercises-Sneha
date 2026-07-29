import streamlit as st
from utils.data_loader import get_master_dataset
from utils.helpers import apply_global_filters, format_kpi
from utils.charts import choropleth_world, top_n_bar, sparkline_trend

st.set_page_config(page_title="Executive Summary", page_icon="📊", layout="wide")
st.title("📊 Executive Summary")
st.caption("A 10-second overview of global development, right now.")

df = get_master_dataset()
fdf = apply_global_filters(df)

if fdf.empty:
    st.warning("No data matches the current filters. Try widening your selection.")
    st.stop()

year = int(fdf["year"].max())
year_df = fdf[fdf["year"] == year]

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Countries", year_df["country"].nunique())
c2.metric("Selected Year", year)
c3.metric("Avg GDP / Capita", format_kpi(year_df["gdp_per_capita"].mean()))
c4.metric("Avg Life Expectancy", format_kpi(year_df["life_expectancy"].mean(), "decimal") + " yrs")
c5.metric("Avg Happiness", format_kpi(year_df["happiness_score"].mean(), "decimal"))
c6.metric("Avg CO2 Emissions", format_kpi(year_df["co2_emissions"].mean()) + " Mt")

st.markdown("---")

st.markdown("#### 🗺️ Where does the world stand today?")
map_df = year_df.dropna(subset=["gdp_per_capita"])
if not map_df.empty:
    fig = choropleth_world(
        map_df, "gdp_per_capita", "GDP per Capita ($)",
        f"GDP per Capita by Country, {year}",
        "Darker shades indicate higher GDP per capita. Hover for exact values.")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Wealth remains concentrated in North America, Western Europe, and parts of East Asia and the Gulf.")
else:
    st.info("No GDP per capita data available for this selection/year.")

col_a, col_b = st.columns(2)
with col_a:
    d = year_df.dropna(subset=["gdp"])
    if not d.empty:
        fig = top_n_bar(d, "country", "gdp", 10, "Top 10 Countries by GDP",
                         "Total nominal GDP, current international $", color_col="region")
        st.plotly_chart(fig, use_container_width=True)
with col_b:
    d = year_df.dropna(subset=["happiness_score"])
    if not d.empty:
        fig = top_n_bar(d, "country", "happiness_score", 10, "Top 10 Happiest Countries",
                         "World Happiness Report Cantril Ladder score (0-10)", color_col="region")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No happiness data available for this selection/year.")

st.markdown("#### 📈 Long-run global trends")
col_c, col_d = st.columns(2)
global_trend = fdf.groupby("year", as_index=False).agg(
    gdp_per_capita=("gdp_per_capita", "mean"),
    life_expectancy=("life_expectancy", "mean"),
)
with col_c:
    fig = sparkline_trend(global_trend, "year", "gdp_per_capita",
                           "Global Average GDP per Capita Over Time",
                           "A century-scale look at rising average incomes.")
    st.plotly_chart(fig, use_container_width=True)
with col_d:
    fig = sparkline_trend(global_trend, "year", "life_expectancy",
                           "Global Average Life Expectancy Over Time",
                           "Health gains have been broad-based across regions.")
    st.plotly_chart(fig, use_container_width=True)
