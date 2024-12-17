import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_leaflet as dl
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta

# Create Dash app
app = dash.Dash(__name__)
app.title = "Weather Dashboard"

# Layout
app.layout = html.Div([
    html.H1("Weather Dashboard", style={"text-align": "center"}),

    html.Div([
        html.H3("Select Location on the Map"),
        dl.Map([
            dl.TileLayer(),
            dl.Marker(position=[52.52, 13.419], id="map-marker")
        ], center=[52.52, 13.419], zoom=5, id='map', style={"height": "400px", "width": "100%"}),
    ], style={"margin-bottom": "20px"}),

    html.Div([
        dcc.Dropdown(
            id="data-type",
            options=[
                {"label": "Temperature", "value": "temperature_2m"},
                {"label": "Precipitation", "value": "precipitation"},
                {"label": "Wind Speed", "value": "windspeed_10m"}
            ],
            value="temperature_2m",
            style={"width": "50%"}
        ),
        dcc.RadioItems(
            id="data-range",
            options=[
                {"label": "Forecast (next 7 days)", "value": "forecast"},
                {"label": "Historical (past 7 days)", "value": "historical"}
            ],
            value="forecast",
            inline=True
        )
    ]),

    html.Div([
        dcc.Graph(id="daily-graph", style={"height": "400px"}),
        dcc.Graph(id="hourly-graph", style={"height": "400px"})
    ])
])

@app.callback(
    [Output("daily-graph", "figure"), Output("hourly-graph", "figure")],
    [Input("map-marker", "position"), Input("data-type", "value"), Input("data-range", "value")]
)
def update_weather_dashboard(position, data_type, data_range):
    latitude, longitude = position

    base_url = "https://api.open-meteo.com/v1/forecast"

    # Define parameters based on the selected range
    if data_range == "forecast":
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": data_type,
            "timezone": "Europe/Berlin"
        }
    else:  # Historical data
        end_date = datetime.now().date() - timedelta(days=1)
        start_date = end_date - timedelta(days=6)
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": data_type,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "timezone": "Europe/Berlin"
        }

    try:
        # Fetch data
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # Process hourly data
        hourly_data = pd.DataFrame({
            "time": pd.to_datetime(data["hourly"]["time"]),
            data_type: data["hourly"][data_type]
        })

        # Create hourly graph
        hourly_fig = px.line(hourly_data, x="time", y=data_type,
                             title=f"Hourly {data_type.replace('_', ' ').title()}",
                             labels={"time": "Time", data_type: "Value"})

        # 
        return hourly_fig, hourly_fig

    except requests.RequestException as e:
        error_fig = px.scatter(title=f"Error: Unable to fetch data - {e}")
        return error_fig, error_fig

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
