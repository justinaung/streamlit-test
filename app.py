import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk
import numpy as np


DATE_COLUMN = 'last_review'
DATA_URL = 'listings_syd_Mar2020.csv'


@st.cache
def load_data(nrows=None):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data.rename(lambda x: x.lower(), axis='columns', inplace=True)
    data = data.drop(axis=1, columns=['neighbourhood_group'])
    data = data.dropna()
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

data = load_data()

#
# Sidebar widgets
#
room_types = list(data['room_type'].unique())
room_types_multiselect = st.sidebar.multiselect(
    label='Room types',
    options=room_types,
    default=room_types[:2]
)

price_input_min = st.sidebar.number_input(
    'Minimum price',
    int(data['price'].min()),
    int(data['price'].max()),
    value=600,
    step=10,
)
price_input_max = st.sidebar.number_input(
    'Maximum price',
    int(data['price'].min()),
    int(data['price'].max()),
    value=3000,
    step=10,
)

hoods = list(data['neighbourhood'].unique())
hoods_multiselect = st.sidebar.multiselect(
    label='Neighbourhoods in Sydney',
    options=hoods,
    default=hoods[:30]
)

filtered_data = data[
    data['room_type'].isin(room_types_multiselect)
    & data['neighbourhood'].isin(hoods_multiselect)
    & data['price'].between(price_input_min, price_input_max)
]

'# Exploring Sydney Airbnb Data'

'## Sydney Map'
view_state = pdk.ViewState(
  latitude=-33.8692,
  longitude=151.2266,
  min_zoom=8,
  zoom=10,
  max_zoom=16,
  pitch=25,
)
scatter = pdk.Layer(
    'ScatterplotLayer',
    data=filtered_data,
    get_position=['longitude', 'latitude'],
    auto_highlight=True,
    get_radius=200,
    get_fill_color=[255, 0, 0, 75],
    pickable=True,
)
tooltip = """
    <h3>{name}</h3>
    <table>
        <tr>
            <th>Room type:</th>
            <td>{room_type}</td>
        <tr>
        <tr>
            <th>Price:</th>
            <td>${price}</td>
        <tr>
        <tr>
            <th>Neighbourhood:</th>
            <td>{neighbourhood}</td>
        <tr>
    </table>
"""
st.pydeck_chart(pdk.Deck(
    layers=[scatter],
    initial_view_state=view_state,
    tooltip={'html': tooltip},
))

'## Bar Chart'
stacked_bar_chart = alt.Chart(filtered_data).transform_aggregate(
    count='count()',
    groupby=['neighbourhood', 'room_type']
).mark_bar().encode(
    alt.X('neighbourhood:N', sort='-y', title='Neighbourhood'),
    alt.Y('count:Q', title='Number of Airbnbs'),
    color=alt.Color('room_type', legend=alt.Legend(title='Room type')),
    tooltip=['count:Q', 'room_type', 'neighbourhood']
).interactive()
st.altair_chart(stacked_bar_chart)

if st.checkbox('Show filtered raw data'):
    '## Filterd Raw Data'
    filtered_data

