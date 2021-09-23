"""Query the urbanair API with GET requests"""

from datetime import datetime
from io import StringIO
from typing import Tuple
import requests
from urllib.parse import urljoin
import typer
import pandas as pd

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

def get_bounding_box(lon_min: float, lat_min: float, lon_max: float, lat_max: float) -> Tuple[float]:
    """Get bounding box"""
    return (lon_min, lat_min, lon_max, lat_max)

def main(username: str, password: str):
    # small bounding box for testing
    lon_min=-0.125
    lat_min=51.53
    lon_max=-0.120
    lat_max=51.534
    small_bounding_box = get_bounding_box(lon_min, lat_min, lon_max, lat_max)

    # authenticate with password
    basic_auth = requests.auth.HTTPBasicAuth(username, password)

    # get dataframe from API request
    time = datetime(2021, 8, 12, 6, 0, 0)
    csv_str = query_forecast_hexgrid_1hr_csv(basic_auth, time, 0, small_bounding_box)
    df = pd.read_csv(StringIO(csv_str))
    print(df)

if __name__=="__main__":
    typer.run(main)
