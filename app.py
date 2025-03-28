import streamlit as st
import pandas as pd
import pydeck

st.set_page_config(layout="wide")

st.markdown(
    """
<style>
div[data-testid="metric-container"] label {
    font-size: 48px !important;
}
</style>
""",
    unsafe_allow_html=True,
)


def big_metric(label, value, delta=None):
    st.markdown(
        f"""
    <style>
    .big-metric-label {{
        font-size: 24px !important;
    }}
    </style>
    <div class="big-metric-label">{label}</div>
    """,
        unsafe_allow_html=True,
    )
    st.metric(label="", value=value, delta=delta)


def paragraph(text, font_size=24, line_height=1.6):
    st.markdown(
        f"""
    <p style='font-size:{font_size}px; line-height:{line_height}'>
    {text}
    </p>
    """,
        unsafe_allow_html=True,
    )


# Data Preparation

# upload to data frame, dataset uploaded from UNHCR

df_migration = pd.read_csv("data/unhcr.csv")


# st.dataframe(df_migration)
st.title(
    "Key Statistics for Refugees and Asylum-Seekers in Southern, East and Horn of Africa"
)
paragraph(
    "The data in this page is aggregated from UNHCR dataset which is available at https://data.humdata.org/dataset/unhcr-situations"
)
total_migrants = df_migration.loc[df_migration["Individuals"] > 0, "Individuals"].sum()
total_refugees = df_migration.loc[
    df_migration["Population type"] == "Refugees", "Individuals"
].sum()
total_asylum_seekers = df_migration.loc[
    df_migration["Population type"] == "Asylum-Seekers", "Individuals"
].sum()

col1, col2, col3 = st.columns(3)

with col1:
    big_metric(label="Total Refugees and Asylum Seekers", value=f"{total_migrants:,}")
with col2:
    big_metric(label="Total Refugees", value=f"{total_refugees:,}")
with col3:
    big_metric(label="Total Asylum Seekers", value=f"{total_asylum_seekers:,}")

# Sudan statistics

total_sudan_migrants = df_migration.loc[
    df_migration["Country of Origin"] == "Sudan", "Individuals"
].sum()

total_sudan_internally_displaced = df_migration.loc[
    (df_migration["Country"] == "Sudan")
    & (df_migration["Country of Origin"] == "Sudan"),
    "Individuals",
].sum()

sum_Chad = df_migration.loc[
    (df_migration["Country"] == "Chad")
    & (df_migration["Country of Origin"] == "Sudan"),
    "Individuals",
].sum()
sum_Ethiopia = df_migration.loc[
    (df_migration["Country"] == "Ethiopia")
    & (df_migration["Country of Origin"] == "Sudan"),
    "Individuals",
].sum()
sum_Central_African_Republic = df_migration.loc[
    (df_migration["Country"] == "Central African Republic")
    & (df_migration["Country of Origin"] == "Sudan"),
    "Individuals",
].sum()
sum_South_Sudan = df_migration.loc[
    (df_migration["Country"] == "South Sudan")
    & (df_migration["Country of Origin"] == "Sudan"),
    "Individuals",
].sum()

st.subheader("State of Sudan")
paragraph(
    "Due to the conflict that arose in Sudan in 2023, the total refugees from Sudan has sky-rocketed"
)
col1, col2, col3 = st.columns(3)
with col1:
    big_metric(label=" Total Migrants from Sudan", value=f"{total_sudan_migrants:,}")
with col2:
    big_metric(label="Sudanese Migrants in Chad", value=f"{sum_Chad:,}")
with col3:
    big_metric(label="Sudanese Migrants in Ethiopia", value=f"{sum_Ethiopia:,}")

col4, col5, col6 = st.columns(3)

with col4:
    big_metric(
        label="Sudanese Migrants in Central African Republic",
        value=f"{sum_Central_African_Republic:,}",
    )
with col5:
    big_metric(
        label="Sudanese Migrants in South Sudan",
        value=f"{sum_South_Sudan:,}",
    )
with col6:
    big_metric(
        label="Sudanese Migrants displaced internally",
        value=f"{total_sudan_internally_displaced:,}",
    )


# upload our generated csv file for geo-location of destination countries using geo-test.py

df_geo = pd.read_csv("data/Geolocation.csv")
# df_geo.set_index('country', inplace=True)

# st.dataframe(df_geo)

# upload our generated csv file for geo-location of countries of origin using origin.py
df_geo_origin = pd.read_csv("data/origin.csv")


# Rename our data frame which holds location data
df_geo.rename(
    columns={"Unnamed: 0": "No.", "country": "Country", "lat": "lat", "long": "lon"},
    errors="raise",
    inplace=True,
)

df_geo_origin.rename(
    columns={
        "Unnamed: 0": "No.",
        "country": "Country of Origin",
        "latitude": "latitude",
        "longitude": "longitude",
    },
    inplace=True,
    errors="raise",
)

df_merge_test = pd.merge(df_migration, df_geo, left_on="Country", right_on="Country")
df_merge_all = pd.merge(
    df_merge_test,
    df_geo_origin,
    left_on="Country of Origin",
    right_on="Country of Origin",
)

df_filtered = df_merge_all[df_merge_all["Individuals"] > 10000]
# Group data by total migrants to each country
df_aggregate = df_migration.groupby("Country")["Individuals"].sum().to_frame()

df_origin_aggregate = (
    df_migration.groupby("Country of Origin")["Individuals"].sum().to_frame()
)

df_migrant_type = (
    df_migration.groupby("Population type")["Individuals"].sum().to_frame()
)

df_by_date = df_migration.groupby("Date")["Individuals"].sum().to_frame()


# Merge the aggregate dataframe with the location dataframe
df_map = pd.merge(df_geo, df_aggregate, on="Country")
df_map_origin = pd.merge(df_geo_origin, df_origin_aggregate, on="Country of Origin")

df_map_origin.head()

df_map["size"] = df_map["Individuals"] / 50
df_map_origin["size"] = df_map_origin["Individuals"] / 100

df_sorted = df_map.sort_values(by="Individuals", ascending=False)
# Page Layout

# Title of Page
st.title("Migration Crisis in Africa as reported by UNHCR")

st.markdown(
    "### Visualization of Migration data from African Countries as collected by UNHCR"
)


st.subheader("Total Migrants in Each Country")

with st.expander("Click to expand filters"):
    COUNTRIES = df_sorted["Country"].unique()
    COUNTRIES_SELECTED = st.multiselect("Select Countries", COUNTRIES)
    mask_countries = df_sorted["Country"].isin(COUNTRIES_SELECTED)
    if not COUNTRIES_SELECTED:
        filtered_df = df_sorted[df_sorted["Individuals"] > 1500000]
    else:
        filtered_df = df_sorted[mask_countries]


st.bar_chart(
    filtered_df.set_index("No.").sort_values("Individuals"),
    x="Country",
    y="Individuals",
)

st.subheader("Origin of Migrants")

with st.container():
    COUNTRIES_ORIGIN = df_map_origin["Country of Origin"].unique()

    COUNTRIES_ORIGIN_SELECTED = st.multiselect("Select Countries", COUNTRIES_ORIGIN)
    mask_origin_countries = df_map_origin["Country of Origin"].isin(
        COUNTRIES_ORIGIN_SELECTED
    )

    if not COUNTRIES_ORIGIN_SELECTED:
        filtered_origin_df = df_map_origin[df_map_origin["Individuals"] > 1500000]

    else:
        filtered_origin_df = df_map_origin[mask_origin_countries]

st.markdown("<br>", unsafe_allow_html=True)
st.bar_chart(
    filtered_origin_df,
    x="Country of Origin",
    y="Individuals",
)

st.write("Total Migrants by Type")
st.bar_chart(
    df_migrant_type,
)
st.subheader("Migration flow accross the year")

st.line_chart(df_by_date)

point_layer = pydeck.Layer(
    "ScatterplotLayer",
    data=df_map,
    id="immigration-countries",
    get_position=["lon", "lat"],
    get_color="[255, 75, 75]",
    pickable=True,
    auto_highlight=True,
    get_radius="size",
)
point_origin_layer = pydeck.Layer(
    "ScatterplotLayer",
    data=df_map_origin,
    id="immigration-countries-origin",
    get_position=["longitude", "latitude"],
    get_color="[75, 75, 255]",
    pickable=True,
    auto_highlight=True,
    get_radius="size",
)


path_layer = pydeck.Layer(
    "GreatCircleLayer",
    data=df_filtered,
    pickable=True,
    get_strock_width=12,
    get_source_position=["longitude", "latitude"],
    get_target_position=["lon", "lat"],
    get_source_color=[64, 255, 0],
    get_target_color=[0, 128, 200],
    auto_highlight=True,
)
view_state = pydeck.ViewState(
    latitude=18, longitude=35, controller=True, zoom=2.5, pitch=30
)

chart = pydeck.Deck(
    [point_layer, point_origin_layer, path_layer],
    initial_view_state=view_state,
    tooltip={
        "text": "{Country},{Country of Origin}\nLat:{lat} Lon{lon}\nMigrants: {Individuals}"
    },
)

st.write("A map visualizer of total migrants in each country")
event = st.pydeck_chart(chart, on_select="rerun", selection_mode="multi-object")

event.selection
