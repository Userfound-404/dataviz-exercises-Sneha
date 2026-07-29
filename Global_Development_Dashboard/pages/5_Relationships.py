import streamlit as st
from utils.data_loader import get_master_dataset, get_indicator_meta
from utils.preprocessing import safe_corr
from utils.charts import scatter_with_trend

st.set_page_config(page_title="Relationships", page_icon="🔗", layout="wide")
st.title("🔗 Relationships")
st.caption("What factors are most strongly associated with higher quality of life?")

df = get_master_dataset()
meta = get_indicator_meta()

numeric_indicators = ["gdp", "gdp_per_capita", "life_expectancy", "happiness_score",
                       "school_enrollment", "literacy_rate", "co2_emissions",
                       "renewable_energy_pct", "population", "internet_users_pct",
                       "infant_mortality"]
options = {meta[k]["label"]: k for k in numeric_indicators}

c1, c2, c3 = st.columns(3)
x_label = c1.selectbox("X variable", list(options.keys()),
                        index=list(options.keys()).index("GDP per Capita"))
y_label = c2.selectbox("Y variable", list(options.keys()),
                        index=list(options.keys()).index("Life Expectancy"))
year = c3.slider("Year", int(df["year"].min()), int(df["year"].max()), int(df["year"].max()))

x_col, y_col = options[x_label], options[y_label]

year_df = df[df["year"] == year].dropna(subset=[x_col, y_col])

st.markdown("**Suggested pairings:** GDP vs Life Expectancy · GDP vs Happiness · "
            "Literacy vs GDP · GDP vs CO2 · Renewables vs CO2 · Population vs GDP")

if year_df.empty:
    st.warning("No overlapping data for this pair of variables in the selected year. Try a different year.")
    st.stop()

fig = scatter_with_trend(
    year_df, x_col, y_col, size_col="population", color_col="region", hover_name="country",
    title=f"{x_label} vs. {y_label} ({year})",
    subtitle="Bubble size = population, color = region. Line = OLS trend.")
st.plotly_chart(fig, use_container_width=True)

r, p, n = safe_corr(year_df, x_col, y_col)
if r is not None:
    st.markdown(f"**Pearson correlation coefficient:** r = `{r:.3f}`, p = `{p:.4f}`, n = `{n}` countries")
    strength = abs(r)
    if strength >= 0.7:
        st.success(f"Strong {'positive' if r > 0 else 'negative'} relationship between {x_label} and {y_label}.")
    elif strength >= 0.4:
        st.info(f"Moderate {'positive' if r > 0 else 'negative'} relationship between {x_label} and {y_label}.")
    else:
        st.warning(f"Weak relationship between {x_label} and {y_label} — other factors likely dominate.")
else:
    st.info("Not enough overlapping data points to compute a correlation.")

st.caption(
    "Correlation does not imply causation — many of these relationships are "
    "confounded by history, institutions, and geography."
)
