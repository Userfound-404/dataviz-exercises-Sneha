# 🌍 Global Development Dashboard

**Exploring Economic, Social, and Environmental Progress**

An interactive, multipage Streamlit dashboard that explores how countries
have developed over the last three decades, and what factors are most
strongly associated with higher quality of life. Built following
storytelling-with-data principles (Cole Nussbaumer Knaflic) and dashboard
design best practices (Steve Wexler, *The Big Book of Dashboards*).

## ⚠️ About the data — read this first

**Every number in this dashboard is real**, merged from public sources —
nothing is simulated or invented. See [Dataset sources](#dataset-sources)
below for exact provenance, and `build_master_dataset.py` for the full,
reproducible merge pipeline.

Two indicators requested in the original spec — **school enrollment** and
**unemployment rate** — could not be sourced as clean, global,
country-by-year files from the available public mirrors in the time
available. Rather than fabricate plausible-looking numbers, these columns
are included in the schema but left as `NaN`; the dashboard displays
"N/A" for them instead of guessing. Everything else (population, GDP, GDP
per capita, life expectancy, infant mortality, literacy rate, CO2
emissions, renewable energy share, internet coverage, happiness score) is
real, sourced data.

## Features

- **Executive Summary** — KPI cards, world choropleth, top-10 rankings, global trend sparklines
- **Country Explorer** — single-country profile cards, time series, radar chart vs. world average, and a two-country compare mode
- **Trends** — multi-line charts, area charts, slopegraphs, animated GDP-vs-life-expectancy scatter
- **Geographic Analysis** — choropleth + bubble maps, regional rankings
- **Relationships** — scatter + OLS trendline with Pearson correlation for any two indicators
- **Regional Comparison** — grouped/stacked bars, box plots, heatmap, treemap
- **Key Insights** — auto-generated takeaways (top improver, highest GDP, strongest correlation, etc.)
- Cascading global sidebar filters (year → region → income group → country), population/GDP range sliders, CSV download of the filtered data, and a "Reset Filters" button

## Folder structure

```
Global_Development_Dashboard/
│
├── app.py                          # Main entry point / landing page
├── build_master_dataset.py         # Reproducible real-data merge pipeline
├── pages/
│   ├── 1_Executive_Summary.py
│   ├── 2_Country_Explorer.py
│   ├── 3_Trends.py
│   ├── 4_Geographic_Analysis.py
│   ├── 5_Relationships.py
│   ├── 6_Regional_Comparison.py
│   └── 7_Key_Insights.py
├── utils/
│   ├── data_loader.py              # @st.cache_data dataset loading
│   ├── preprocessing.py            # change/correlation helpers
│   ├── charts.py                   # reusable Plotly chart functions
│   └── helpers.py                  # sidebar filters, KPI formatting
├── data/
│   ├── raw/                        # original downloaded source files
│   ├── global_development_master.parquet
│   └── global_development_master.csv
├── requirements.txt
└── README.md
```

## Installation

```bash
cd Global_Development_Dashboard
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## How to run

The cleaned dataset is already built and included at
`data/global_development_master.parquet`. Just run:

```bash
streamlit run app.py
```

Streamlit will open at `http://localhost:8501`.

To rebuild the dataset from scratch (re-downloading raw source files),
run `build_master_dataset.py` after re-populating `data/raw/` — see the
script's docstring for the exact source URLs used.

## Dataset sources

All data was retrieved from the following **real, public, authentic**
sources (all are freely redistributable under the sources' own open-data
terms; OWID mirrors are CC BY):

| Indicator(s) | Original source | Retrieved via |
|---|---|---|
| Population, GDP, CO2 emissions | World Bank / Maddison Project / Global Carbon Project | [`owid/co2-data`](https://github.com/owid/co2-data) (GitHub) |
| Renewable energy share | Ember, EIA | [`owid/energy-data`](https://github.com/owid/energy-data) (GitHub) |
| Life expectancy at birth | World Bank (2015 release) | OWID archived dataset repo |
| Infant mortality rate | IHME (2017 release) | OWID archived dataset repo |
| Literacy rate | World Bank, CIA World Factbook | OWID archived dataset repo |
| Internet coverage | Internet World Stats (2019) | OWID archived dataset repo |
| Happiness score (Cantril Ladder) | World Happiness Report 2022 | OWID archived dataset repo |
| Region (continent) | UN M49 standard | [`lukes/ISO-3166-Countries-with-Regional-Codes`](https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes) |
| Income group | World Bank Country and Lending Groups (FY2024 classification) | Compiled from World Bank's published classification table |

The merge logic (join keys, cleaning, derived `gdp_per_capita`) is fully
visible and reproducible in `build_master_dataset.py`.

## Dashboard screenshots
<img width="1710" height="1112" alt="Screenshot 2026-07-29 at 9 56 15 PM" src="https://github.com/user-attachments/assets/0ddef21c-0d5f-47a9-aaf8-0881aaba3ec3" />


## Future improvements

- Source a clean, global school-enrollment and unemployment-rate series to fill the two remaining `NaN` columns
- Add country-development clustering (KMeans) as a "Country Segments" page
- Schedule automatic re-pulls of the underlying OWID/World Bank files
- Add a simple regression model predicting life expectancy/happiness from economic + environmental features
- Deploy to Streamlit Community Cloud for a public portfolio link
