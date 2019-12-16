import dash
import dash_core_components as dcc
import dash_html_components as html
import requests
import geopandas as gpd
import folium
from folium.plugins import HeatMap
import carto2gpd

from geopandas import gpd
import osmnx as ox
import networkx as nx
from IPython.display import IFrame # loads HTML files
import dash_core_components as dcc

 

# initialize the app
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# set a title
app.title = "Dash + Folium: Route planning"


def get_folium_map(place):
    """
    Make the Folium map
    """
    # initialize the Folium map
    From = "Times square"
    To = place
    G = ox.graph_from_address("Times square, New York", 
                          distance=2000,network_type='drive')
    ox.extended_stats(G).keys()
    
    origin = gpd.tools.geocode(From, provider='nominatim', user_agent="my-application")
    destination = gpd.tools.geocode(To, provider='nominatim', user_agent="my-application")

    start = list(zip(origin.geometry.y, origin.geometry.x))
    end = list(zip(destination.geometry.y, destination.geometry.x))

    orig_node = ox.get_nearest_node(G, start[0]) 
    dest_node = ox.get_nearest_node(G, end[0])

    route = nx.shortest_path(G, 
                     orig_node, dest_node, 
                     weight='length')

    # The interactive map of the street network
    graph_map = ox.plot_graph_folium(G, popup_attribute="name", edge_width=2)

    # The interactive map of the route, with the streets in the background
    route_graph_map = ox.plot_route_folium(G, route, route_map=graph_map)


    #filepath = 'foliumChart.html'
    #route_graph_map.save(filepath)
    figure = folium.Figure(width=450, height=450)
    route_graph_map.add_to(figure)

    # return the Pane object
    return figure.get_root().render()


markdown_text = """
# Route planning tool
"""

# set the layout
app.layout = html.Div(
    [
        # the title!
        dcc.Markdown(markdown_text),
        # DIV ELEMENT FOR DAYS SLIDER
        html.Div(
            [
                html.Label("Where to go?"),
                #dcc.Slider(id="daysSlider", min=30, max=365, value=90),
                dcc.Dropdown(id="placePicker",
                    options=[
                        {'label': 'Museum of Arts and Design', 'value': '2 Columbus Cir, New York'},
                        {'label': 'Empire state building', 'value': 'Empire state building'},
                        {'label': 'New York Hilton Midtown', 'value': '1335 6th Ave, New York'},
                        {'label': 'Pennsylvania station', 'value': 'Pennsylvania station, New York'},
                        {'label': 'Grand Central Terminal', 'value': 'Grand Central Terminal, New York'},
                        {'label': 'Trump tower', 'value': 'Trump tower, New York'}
                    ],
                    value='Empire state building'
                ), 
                html.P(id="placePickerValue", children=""),
            ],
            style={
                "width": "250px",
                "margin-right": "auto",
                "margin-left": "auto",
                "text-align": "center",
            },
        ),
        # MAP IFRAME
        html.Div(
            [
                html.Iframe(
                    id="map",
                    height="500",
                    width="800",
                    sandbox="allow-scripts",
                    style={"border-width": "0px", "align": "center"},
                )
            ],
            style={"display": "flex", "justify-content": "center"},
        ),
    ]
)


@app.callback(
    [
        dash.dependencies.Output("map", "srcDoc"),
        dash.dependencies.Output("placePickerValue", "children"),
    ],
    [dash.dependencies.Input("placePicker", "value")],
)
def render(days):

    # query the CARTO database
    #gdf = get_data(days)

    # make and return our map
    map_html = get_folium_map(days)

    text = f"Please give it some times..."

    return map_html,text


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=5000, debug=True)