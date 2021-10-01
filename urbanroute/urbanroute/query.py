"""Query the urbanair API with GET requests"""

from datetime import datetime
from io import StringIO
import json
from typing import Tuple
import requests
from urllib.parse import urljoin
import typer
import geopandas as gpd
import networkx as nx
import osmnx as ox
import pandas as pd

from . import geospatial as gs

# URL building strings for urbanair
URBANAIR_HEXGRID_FORECAST_URL = "https://urbanair.turing.ac.uk/api/v1/air_quality/forecast/hexgrid/"

# Define the bounding box for London
MIN_LONGITUDE = -0.510
MAX_LONGITUDE = 0.335
MIN_LATITUDE = 51.286
MAX_LATITUDE = 51.692
LONDON_BOUNDING_BOX = (MIN_LONGITUDE, MIN_LATITUDE, MAX_LONGITUDE, MAX_LATITUDE)

class EmptyDatasetWarning(UserWarning):
    """Raise if a dataset has no data"""

def query_hexgrid_geometries(basic_auth: requests.auth.HTTPBasicAuth, bounding_box: Tuple[float]) -> str:
    """Query the hexgrid geometries. Json string returned"""
    params = {
        "lon_min": bounding_box[0],
        "lat_min": bounding_box[1],
        "lon_max": bounding_box[2],
        "lat_max": bounding_box[3],
    }
    geometries_url = urljoin(URBANAIR_HEXGRID_FORECAST_URL, "geometries")
    text = ""
    with requests.Session() as session:
        session.auth = basic_auth
        response = session.get(geometries_url, params=params)
        response.raise_for_status()
        text = response.text
    return text

def get_hexgrid_geometries_gdf(basic_auth: requests.auth.HTTPBasicAuth, bounding_box: Tuple[float]) -> gpd.GeoDataFrame:
    """Get a geodataframe of hexgrid cells with geometries"""
    # get hexgrid geometries
    geojson_str = query_hexgrid_geometries(basic_auth, bounding_box)
    geojson_hexgrid = json.loads(geojson_str)
    feature_list = []
    for feature in geojson_hexgrid["features"]:
        # need to assign the hex id to a properties dictionary for geopandas to read geojson
        feature["properties"] = {"hex_id": feature["hex_id"]}
        feature_list.append(feature)
    hexgrid_df = gpd.GeoDataFrame.from_features(feature_list)
    hexgrid_df.crs = "EPSG:4326"
    return hexgrid_df

def query_forecast_hexgrid_1hr_csv(
    basic_auth: requests.auth.HTTPBasicAuth,
    time: datetime,
    index: int = 0,
    bounding_box: Tuple[float] = LONDON_BOUNDING_BOX,
) -> str:
    """Get the string of a CSV file from the urbanair API"""
    params = {
        "time": time.isoformat(),
        "index": index,
        "lon_min": bounding_box[0],
        "lat_min": bounding_box[1],
        "lon_max": bounding_box[2],
        "lat_max": bounding_box[3],
    }
    csv_url = urljoin(URBANAIR_HEXGRID_FORECAST_URL, "csv")
    text = ""
    with requests.Session() as session:
        session.auth = basic_auth
        response = session.get(csv_url, params=params)
        response.raise_for_status()
        text = response.text
    if len(text) == 0:
        raise EmptyDatasetWarning("No data in CSV file for query_forecast_hexgrid_1hr_csv")
    return text

def get_forecast_hexgrid_1hr_gdf(
    basic_auth: requests.auth.HTTPBasicAuth,
    time: datetime,
    index: int = 0,
    bounding_box: Tuple[float] = LONDON_BOUNDING_BOX,
) -> gpd.GeoDataFrame:
    """Get a geodataframe from the forecast hexgrid 1 hour query with geometries"""
    hexgrid_df = get_hexgrid_geometries_gdf(basic_auth, bounding_box)
    csv_str = query_forecast_hexgrid_1hr_csv(basic_auth, time, index=1, bounding_box=bounding_box)
    forecast_df = pd.read_csv(StringIO(csv_str))
    joined_df = gpd.GeoDataFrame(forecast_df.merge(hexgrid_df, on="hex_id"), crs="EPSG:4326")
    return joined_df

def get_bounding_box(lon_min: float, lat_min: float, lon_max: float, lat_max: float) -> Tuple[float]:
    """Get bounding box incase you forget the order of lats and lons"""
    return (lon_min, lat_min, lon_max, lat_max)
