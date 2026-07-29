"""Global Development Dashboard — main entry point.

Run with: streamlit run app.py
"""
import streamlit as st
from utils.data_loader import get_master_dataset
from utils.helpers import apply_global_filters

st.set_page_config(
    page_title="Global Development Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container {padding-top: 2rem;}
    div[data-testid="stMetricValue"] {font-size: 1.6rem;}
    h1, h2, h3 {font-family: Helvetica, Arial, sans-serif;}
</style>
""", unsafe_allow_html=True)

st.title("🌍 Global Development Dashboard")
st.subheader("Exploring Economic, Social, and Environmental Progress")

st.markdown(
    "How have countries developed over the last few decades, and what "
    "factors are most strongly associated with higher quality of life? "
    "This dashboard combines real indicators — population, GDP, life "
    "expectancy, CO2 emissions, renewable energy, happiness, and more — "
    "sourced from the **World Bank, UN Population Division, IHME, and the "
    "World Happiness Report** (via Our World in Data) to help answer that "
    "question."
)

try:
    df = get_master_dataset()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

filtered_df = apply_global_filters(df)
st.session_state["filtered_df"] = filtered_df
st.session_state["master_df"] = df

col1, col2, col3 = st.columns(3)
col1.metric("Countries in dataset", df["country"].nunique())
col2.metric("Years covered", f"{df['year'].min()}–{df['year'].max()}")
col3.metric("Currently selected", filtered_df["country"].nunique())

st.markdown("---")
st.markdown(
    """
### 👈 Use the sidebar to filter, then explore the pages:

1. **Executive Summary** — KPIs, world map, top-10 rankings, global trends
2. **Country Explorer** — Deep dive into a single country's profile over time
3. **Trends** — Multi-country time-series, slopegraphs, animated scatter
4. **Geographic Analysis** — Choropleth & bubble maps, regional rankings
5. **Relationships** — Scatter plots, trendlines, and correlation analysis
6. **Regional Comparison** — Grouped bars, box plots, heatmaps, treemaps
7. **Key Insights** — Auto-generated takeaways from the filtered data

*All data is real and traceable — see the README for full source citations.*
"""
)
