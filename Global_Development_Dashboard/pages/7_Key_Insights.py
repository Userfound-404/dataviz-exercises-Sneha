import streamlit as st
from utils.data_loader import get_master_dataset
from utils.preprocessing import year_over_change, safe_corr

st.set_page_config(page_title="Key Insights", page_icon="💡", layout="wide")
st.title("💡 Key Insights")
st.caption("Automatically generated takeaways from the current dataset.")

df = get_master_dataset()

year_max = int(df["year"].max())
year_start = max(int(df["year"].min()), year_max - 10)

st.info(f"Insights computed over {year_start}–{year_max} using all available countries.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### 🚀 Top improving country — Life Expectancy")
    change = year_over_change(df, "life_expectancy", year_start, year_max)
    if not change.empty:
        top = change.iloc[0]
        st.metric(top["country"], f"+{top['change']:.1f} years",
                  f"{top['start_value']:.1f} → {top['end_value']:.1f}")
    else:
        st.info("Not enough data.")

    st.markdown("##### 💰 Highest GDP country (latest year)")
    latest = df[df["year"] == year_max].dropna(subset=["gdp"])
    if not latest.empty:
        top_gdp = latest.loc[latest["gdp"].idxmax()]
        st.metric(top_gdp["country"], f"${top_gdp['gdp']:,.0f}")
    else:
        st.info("Not enough data.")

with col2:
    st.markdown("##### 😊 Region with highest happiness")
    happy = df[df["year"] == year_max].groupby("region")["happiness_score"].mean().dropna()
    if not happy.empty:
        st.metric(happy.idxmax(), f"{happy.max():.2f} / 10")
    else:
        st.info("Not enough data.")

    st.markdown("##### 🌱 Region with lowest CO2 emissions")
    emis = df[df["year"] == year_max].groupby("region")["co2_emissions"].mean().dropna()
    if not emis.empty:
        st.metric(emis.idxmin(), f"{emis.min():,.1f} Mt avg")
    else:
        st.info("Not enough data.")

st.markdown("---")
st.markdown("##### 📊 Strongest GDP–Life Expectancy correlation (latest year)")
year_df = df[df["year"] == year_max]
r, p, n = safe_corr(year_df, "gdp_per_capita", "life_expectancy")
if r is not None:
    st.metric("Pearson r", f"{r:.3f}", f"n={n} countries, p={p:.4f}")
    st.write(
        "This confirms the well-documented **Preston Curve**: rising income "
        "is associated with rising life expectancy, though with strongly "
        "diminishing returns at high income levels."
    )
else:
    st.info("Not enough data to compute this correlation.")

st.markdown("---")
st.caption(
    "These insights are generated directly from the filtered/underlying "
    "real dataset — no numbers here are simulated or hard-coded."
)
