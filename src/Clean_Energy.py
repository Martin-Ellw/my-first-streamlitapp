import streamlit as st
from urllib.request import urlopen
import json
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
#pio.renderers.default = 'colab'   # try changing this in case your plots aren't shown
import pandas as pd
from copy import deepcopy

st.set_page_config(layout="wide")

@st.cache
def load_data(path):
    df = pd.read_csv(path)
    return df

energy_raw = load_data(path="../data/renewable_power_plants_CH.csv")
energy = deepcopy(energy_raw)

with open("../data/georef-switzerland-kanton.geojson") as response:
    cantons = json.load(response)

#cantons["features"][0]["properties"]

# Match the canton code from the df with the canton name in the json --> build reference dictionary

cantons_dict = {'TG':'Thurgau', 'GR':'Graubünden', 'LU':'Luzern', 'BE':'Bern', 'VS':'Valais',
                'BL':'Basel-Landschaft', 'SO':'Solothurn', 'VD':'Vaud', 'SH':'Schaffhausen', 'ZH':'Zürich',
                'AG':'Aargau', 'UR':'Uri', 'NE':'Neuchâtel', 'TI':'Ticino', 'SG':'St. Gallen', 'GE':'Genève',
                'GL':'Glarus', 'JU':'Jura', 'ZG':'Zug', 'OW':'Obwalden', 'FR':'Fribourg', 'SZ':'Schwyz',
                'AR':'Appenzell Ausserrhoden', 'AI':'Appenzell Innerrhoden', 'NW':'Nidwalden', 'BS':'Basel-Stadt'}

energy["canton_name"] = energy["canton"].map(cantons_dict)

#energy.info()
energy.head()

sources_per_canton = energy.groupby("canton_name").size().reset_index(name="count")
sources_per_canton.head()


# building the diagram:

st.title("Renewable Energy Sources in CH")
st.header("Qty per Cantone")

# Setting up Widget columns
left_column, middle_column, right_column = st.columns([1, 2, 1])


# Widgets: radio buttons
show_only_new = left_column.radio(
    label='Show only sources built since 2015', options=['Yes', 'No'])

if show_only_new == "Yes":
    energy = energy[energy["commissioning_date"] > "2015-01-01"]


# Widgets: selectbox
energy_types = ["All"] +sorted(pd.unique(energy['energy_source_level_2']))
e_type = middle_column.selectbox("Choose an Energy Type", energy_types)


# Widgets: checkbox  -- how to move checkbox ? left_column.st.checkbox doesnt work
if right_column.checkbox("Show Energy Production Data Table"):
    st.subheader("This is the Green-Energy dataset:")
    if e_type == "All" :  st.dataframe(data=energy)
    else: st.dataframe(data=energy[energy["energy_source_level_2"]==e_type])



#  link selection to map
if e_type == "All":
    sources_per_canton = energy.groupby("canton_name").size().reset_index(name="count")
else:
    sources_per_canton = energy[energy["energy_source_level_2"]==e_type].groupby("canton_name").size().reset_index(name="count")

fig = px.choropleth_mapbox(
    sources_per_canton,
    color="count",
    geojson=cantons,
    locations="canton_name",
    featureidkey="properties.kan_name",
    center={"lat": 46.8, "lon": 8.3},
    mapbox_style="open-street-map",
    zoom=6.5,
    opacity=0.8,
    width=900,
    height=500,
    labels={"canton_name":"Canton",
           "count":"Number of Sources"},
    title="<b>Number of Clean Energy Sources per Canton</b>",
    color_continuous_scale="Cividis",
)
fig.update_layout(margin={"r":0,"t":35,"l":0,"b":0},
                  font={"family":"Sans",
                       "color":"maroon"},
                  hoverlabel={"bgcolor":"white",
                              "font_size":12,
                             "font_family":"Sans"},
                  title={"font_size":20,
                        "xanchor":"left", "x":0.01,
                        "yanchor":"bottom", "y":0.95}
                 )


from plotly.subplots import make_subplots
import plotly.graph_objects as go

fig2 = make_subplots(
    rows=1, cols=1,  # change to 2 for map incl
    subplot_titles=(
        "Energy Production per Cantone",
        "Map in Subplot")
    )
#  unsuccessful attempt to comment with """
# """ unsuccessful attempt to incl map in subplot
# fig2.add_trace(px.choropleth_mapbox(
#     sources_per_canton,
#     color="count",
#     geojson=cantons,
#     locations="canton_name",
#     featureidkey="properties.kan_name",
#     center={"lat": 46.8, "lon": 8.3},
#     mapbox_style="open-street-map",
#     zoom=6.5,
#     opacity=0.8,
#     width=900,
#     height=500,
#     labels={"canton_name":"Canton",
#            "count":"Number of Sources"},
#     title="<b>Number of Clean Energy Sources per Canton</b>",
#     color_continuous_scale="Cividis"),
#     row=1, col=2)
#
#
# fig2.update_layout(margin={"r":0,"t":35,"l":0,"b":0},
#                   font={"family":"Sans",
#                        "color":"maroon"},
#                   hoverlabel={"bgcolor":"white",
#                               "font_size":12,
#                              "font_family":"Sans"},
#                   title={"font_size":20,
#                         "xanchor":"left", "x":0.01,
#                         "yanchor":"bottom", "y":0.95}
#                  )
# """

fig2.add_trace(go.Scatter(x=sorted(energy.canton_name), y=energy.production, mode='markers', name="Energy production"), row=1, col=1)
fig2.update_layout(height=750, width=1000)

fig
fig2
print("hooray")
#fig.show()
