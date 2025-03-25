import streamlit as st
import pandas as pd
import pydeck


# Title of Page

st.title("Migration Crisis in Africa as reported by UNHCR")

st.markdown(
    "### Visualization of Migration data from African Countries as collected by UNHCR"
)

# Data Preparation

# upload to data frame, dataset uploaded from UNHCR

df_migration = pd.read_csv("data/unhcr.csv")

# upload our generated csv file for geo-location of destination countries using geo-test.py

df_geo = pd.read_csv("data/Geolocation.csv")
# df_geo.set_index('country', inplace=True)

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

df_map["size"] = df_map["Individuals"] / 50
df_map_origin["size"] = df_map_origin["Individuals"] / 100

df_sorted = df_map.sort_values("Individuals")


st.subheader("Total Migrants in Each Country")

COUNTRIES = df_sorted["Country"].unique()

COUNTRIES_SELECTED = st.multiselect("Select Countries", COUNTRIES)

mask_countries = df_sorted["Country"].isin(COUNTRIES_SELECTED)

if not COUNTRIES_SELECTED:
    filtered_df = df_sorted[
        df_sorted["Country"].isin(
            [
                "Ethiopia",
                "Eritrea",
                "Sudan",
                "South Sudan",
            ]
        )
    ]
else:
    filtered_df = df_sorted[mask_countries]


st.bar_chart(
    filtered_df,
    x="Country",
    y="Individuals",
    horizontal=True,
)

st.subheader("Origin of Migrants")

st.bar_chart(
    df_map_origin,
    x="Country of Origin",
    y="Individuals",
)

st.write("Total Migrants by Type")
st.bar_chart(
    df_migrant_type,
)
st.write("Migration flow accross the year")
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
