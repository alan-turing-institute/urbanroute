"""Query the urbanair API with GET requests"""

from datetime import datetime
from io import StringIO
import json
from typing import Any, List, Optional, Set, Tuple
import requests
from urllib.parse import urljoin
import geopandas as gpd
import networkx as nx
import numpy as np
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

def vertices_ordered_by_shortest_path(
    G: nx.Graph, source: Any, append_unreachable: bool = True, weight: Optional[str] = None
) -> List[Any]:
    """Get a list of vertices ordered by the shortest path from the source

    Args:
        G: Networkx graph
        source: Vertex to start shortest path search from
        append_unreachable: If true, vertices that are unreachable from the source are appended to the end of the list
            in no particular order
        weight: Name of the weight attribute. If None, edge weight is one.

    Returns:
        List of vertices in the graph ordered by distance from source vertex.
    """
    distances = nx.shortest_path_length(G, source=source, weight=weight)
    ordered_nodes = []
    for node, _ in sorted(distances.items(), key=lambda x: x[1]):
        ordered_nodes.append(node)
    if append_unreachable == True:
        ordered_nodes.extend(set(G.nodes()) - set(ordered_nodes))
    return ordered_nodes

def vertices_ordered_by_betweenness_centrality(
    G: nx.Graph, weight: Optional[str] = None
) -> List[Any]:
    """Get a list of vertices ordered by the betweenness centrality

    Args:
        G: Undirected input graph
        weight: Name of weight attribute. If None, edge weight is one

    Returns:
        List of vertices ordered by the betweenness centrality

    Notes:
        Only vertices of degree 2 or greater are considered in the subset betweenness centrality    
    """
    sources = [v for v in G.nodes() if G.degree(v) > 2]
    node_betweenness = nx.betweenness_centrality_subset(G, sources, sources, weight=weight)
    ordered_nodes = []
    for node, _ in sorted(node_betweenness.items(), key=lambda x: x[1], reverse=True):
        ordered_nodes.append(node)
    return ordered_nodes

def vertices_ordered_by_coordinate_centrality(
    G: nx.Graph
) -> List[Any]:
    """Vertex list ordered by the Euclidean distance to the center of the coordinates of the vertices

    Args:
        G: networkx graph

    Returns:
        List of vertices ordered by distance to the coordinate center

    Notes:
        The center is chosen by taking the mean of all vertex coordinates
    """
    vertex_data = list(map(lambda x: dict(node=x[0], **x[1]), G.nodes(data=True)))
    nodes_df = pd.DataFrame(vertex_data)
    nodes_df = nodes_df.set_index("node")

    # get mean of x and y coordinate
    x, y = nodes_df["x"].mean(), nodes_df["y"].mean()
    # order by Euclidean distance to mean
    closest_to_mean = list(nodes_df.iloc[(np.sqrt((nodes_df['x']-x)**2 + (nodes_df["y"] - y) ** 2)).argsort()].index)
    return closest_to_mean

def num_non_leaf_neighbors(G: nx.Graph, vertex: int):
    """Get the number of non-leaf neighbors"""
    return len([v for v, d in G.degree(G.neighbors(vertex)) if d > 1])


def is_valid_root(G: nx.Graph, vertex: Any) -> bool:
    """Is the given vertex a valid root vertex?"""
    return nx.degree(G, vertex) >= 2 and num_non_leaf_neighbors(G, vertex) >= 2


class RootVertexNotFoundException(nx.NodeNotFound):
    """Root vertex not found exception"""

def largest_biconnected_component(G: nx.Graph) -> Set:
    """Get the largest biconnected component"""
    largest = {}
    size = 0
    for component in nx.biconnected_components(G):
        if len(component) > size:
            largest = component
            size = len(component)
    return largest

def find_non_trivial_root_vertex(G: nx.Graph, vertex_ordering: List) -> Any:
    """Find a potential root vertex that is not a leaf and has at least two non-leaf neighbors"""
    largest = largest_biconnected_component(nx.to_undirected(G))
    # for vertex in vertices_ordered_by_shortest_path(G, start_vertex, weight=weight):
    for vertex in vertex_ordering:
        if is_valid_root(G, vertex) and vertex in largest:
            return vertex
    raise RootVertexNotFoundException(
        "No non-leaf vertices with at least two non-leaf neighbors were found in the graph"
    )

def frames_from_urbanair_api(
    username: str,
    password: str,
    address: str,
    distance: int,
    timestamp: datetime,
    network_type: str = "drive",
    root_priority: str = "betweenness_centrality",
) -> Tuple[pd.DataFrame]:
    """Queries the urbanair API and osmnx to get the edge and node dataframes of a graph"""    
    center_point = ox.geocoder.geocode(query=address)
    north, south, east, west = ox.utils_geo.bbox_from_point(center_point, distance)
    bounding_box = get_bounding_box(west, south, east, north)
    directed_multigraph = ox.graph_from_bbox(north, south, east, west, network_type=network_type)

    # the root vertex should be close to the center of the graph, must have degree at least 2,
    # and at least two of the root's neighbours must have degree at least 2
    if root_priority == "betweenness_centrality":
        vertex_ordering = vertices_ordered_by_betweenness_centrality(directed_multigraph, weight="length")
    elif root_priority == "coordinate_centrality":
        vertex_ordering = vertices_ordered_by_coordinate_centrality(directed_multigraph)
    else:
        raise ValueError("'betweenness_centrality' and 'coordinate_centrality' are the only valid options for root_priority")
    root_vertex = find_non_trivial_root_vertex(directed_multigraph, vertex_ordering)

    # authenticate with password
    basic_auth = requests.auth.HTTPBasicAuth(username, password)

    # get dataframe from API request
    print("Getting air quality forecast around", address, "for", timestamp.isoformat(), "...")
    pollution_df = get_forecast_hexgrid_1hr_gdf(basic_auth, timestamp, index=1, bounding_box=bounding_box)
    print("...Done for", address)

    # convert directed into undirected graph if the geometries of two arcs match
    undirected_multi_graph = ox.get_undirected(directed_multigraph)
    G = gs.update_cost(undirected_multi_graph, pollution_df, weight_attr="length")
    assert G.number_of_edges() == undirected_multi_graph.number_of_edges()

    edges_df = nx.to_pandas_edgelist(G, source="source", target="target")
    nodes_df = pd.DataFrame.from_dict(dict(G.nodes(data=True)), orient='index')
    nodes_df["is_depot"] = nodes_df.index == root_vertex
    assert nodes_df.is_depot.sum() == 1
    return edges_df, nodes_df
