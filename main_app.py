import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import tomli

# loading config
with open("config.toml", mode="rb") as fp:
    config = tomli.load(fp)

# Initialize the Dash app
app = dash.Dash(__name__)

# click counter 
current_clicks = 0

def update_fig():
    my_places = pd.read_csv(config["data"]["path"], sep=";")
    fig = px.scatter_mapbox(my_places, lat="lat", lon="lon", hover_name="Name",
                            color_discrete_sequence=["yellow"], zoom=3, height=1000)
    fig.update_layout(
        mapbox_style="white-bg",
        mapbox_layers=[
            {
                "below": 'traces',
                "sourcetype": "raster",
                "sourceattribution": "United States Geological Survey",
                "source": [
                    "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                ]
            }
        ])
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_traces(marker=dict(size=10))
    return fig

# Define the layout of the app
app.layout = html.Div([
    html.H1("Places I want to go"),
    dcc.Input(id='Name', type='text', placeholder='Name'),
    dcc.Input(id='Latitude', type='text', placeholder='Latitude'),
    dcc.Input(id='Longitude', type='text', placeholder='Longitude'),
    html.Button('Add', id='add-button', n_clicks=0),
    html.Div(id='output-div'),
    html.Div(dcc.Graph(id='map-plot')),  # Define an empty graph component with an id
])

# Define a callback to update the DataFrame when the button is clicked
@app.callback(
    Output('output-div', 'children'),
    Output('map-plot', 'figure'),  # Update the 'figure' property of the map
    Input('add-button', 'n_clicks'),
    [Input('Name', 'value'), Input('Latitude', 'value'), Input('Longitude', 'value')]
)
def add_to_dataframe(n_clicks, field1, field2, field3):
    global current_clicks
    if n_clicks > current_clicks and field1 and field2 and field3:
        my_places = pd.read_csv(config["data"]["path"], sep=";")
        new_row = pd.DataFrame({'Name': [field1], 'lat': [field2], 'lon': [field3]})
        my_places = pd.concat([my_places, new_row], ignore_index=True)
        my_places.to_csv(config["data"]["path"], sep=";", index=False)
        current_clicks = current_clicks + 1
        fig = update_fig()
        return f'Data added to DataFrame. Total rows: {len(my_places)}', fig  # Return the updated figure
    return '', update_fig()  # Return an empty string and the current figure


if __name__ == '__main__':
    app.run_server(debug=True, port = 8845)
