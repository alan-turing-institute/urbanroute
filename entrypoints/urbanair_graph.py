"""Get a graph of the London road network with air quality data queried from the urbanair API."""

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from networkx.classes.function import neighbors
import requests

import networkx as nx
import osmnx as ox
import pandas as pd
import typer

from urbanroute import get_bounding_box, get_forecast_hexgrid_1hr_gdf
from urbanroute import geospatial as gs

class LondonaqTimestamp(Enum):
    """Timestamps of the forecasts for London air quality forecasts"""

    A = datetime(2021, 10, 13, 8, 0, 0, tzinfo=timezone.utc)  # 9am BST

class LondonaqLocation(str, Enum):
    """Names of locations that the London air quality graph is centered upon"""

    bb = "Big Ben"
    kx = "King's Cross"
    tiny = "King's Cross"
    ro = "Royal Observatory Greenwich"
    ws = "Wembley Stadium"


class LondonaqLocationShort(str, Enum):
    """Short codes for londonaq locations"""

    bb = "bb"
    kx = "kx"
    tiny = "tiny"
    ro = "ro"
    ws = "ws"

def num_non_leaf_neighbors(G: nx.Graph, vertex: int):
    return len([v for v, d in G.degree(G.neighbors(vertex)) if d > 1])

def main(name: LondonaqLocationShort, timestamp_id: str, username: str, password: str, csv_output_dir: Path):

    timestamp = LondonaqTimestamp[timestamp_id]
    csv_output_dir.mkdir(exist_ok=True, parents=False)

    if name == LondonaqLocationShort.tiny:
        distance = 200
    else:
        distance = 5000
    address = LondonaqLocation[name.name].value
    center_point = ox.geocoder.geocode(query=address)
    north, south, east, west = ox.utils_geo.bbox_from_point(center_point, distance)
    bounding_box = get_bounding_box(west, south, east, north)
    directed_multigraph = ox.graph_from_bbox(north, south, east, west)

    # the root vertex should be close to the center of the graph, must have degree at least 2,
    # and at least two of the root's neighbours must have degree at least 2
    center_node = ox.distance.nearest_nodes(directed_multigraph, center_point[0], center_point[1])
    if not center_node in directed_multigraph:
        raise ValueError(f"{center_node} is the center node but is not in the returned graph.")
    root_vertex = center_node
    root_found = False
    attempted_roots = []
    for i in range(directed_multigraph.number_of_nodes()):
        deg = nx.degree(directed_multigraph, root_vertex)
        if deg >= 2 and num_non_leaf_neighbors(directed_multigraph, root_vertex) >= 2:
            root_found = True
            break
        if deg == 1:
            print("Unsuitible vertex: degree 1")
            attempted_roots.append(root_vertex)
        # try a neighbor of the current root
        for v in directed_multigraph.neighbors(root_vertex):
            if v not in attempted_roots:
                root_vertex = v
    if not root_found:
        raise ValueError("No suitable roots found in graph")

    # authenticate with password
    basic_auth = requests.auth.HTTPBasicAuth(username, password)

    # get dataframe from API request
    pollution_df = get_forecast_hexgrid_1hr_gdf(basic_auth, timestamp.value, index=1, bounding_box=bounding_box)
    print(pollution_df)

    # convert directed into undirected graph if the geometries of two arcs match
    undirected_multi_graph = ox.get_undirected(directed_multigraph)
    G = gs.update_cost(undirected_multi_graph, pollution_df, weight_attr="length")
    assert G.number_of_edges() == undirected_multi_graph.number_of_edges()
    print(nx.info(G))

    edges_df = nx.to_pandas_edgelist(G, source="source", target="target")
    nodes_df = pd.DataFrame.from_dict(dict(G.nodes(data=True)), orient='index')
    nodes_df["is_depot"] = nodes_df.index == root_vertex
    assert nodes_df.is_depot.sum() == 1
    prefix = "laq" + name.value + timestamp.name

    # output is a CSV file representing an undirected simple graph
    edges_df.to_csv(csv_output_dir / (prefix+ "_edges.csv"), index=False)
    nodes_df.to_csv(csv_output_dir / (prefix + "_nodes.csv"), index=True, index_label="node")

if __name__=="__main__":
    typer.run(main)
