"""Get a graph of the London road network with air quality data queried from the urbanair API."""

from datetime import datetime
from pathlib import Path
import requests

import networkx as nx
import osmnx as ox
import pandas as pd
import typer

from urbanroute import get_bounding_box, get_forecast_hexgrid_1hr_gdf
from urbanroute import geospatial as gs

def main(username: str, password: str, csv_output_dir: Path):
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
    pollution_df = get_forecast_hexgrid_1hr_gdf(basic_auth, time, index=1, bounding_box=small_bounding_box)
    print(pollution_df)

    directed_multigraph = ox.graph.graph_from_bbox(lat_max, lat_min, lon_max, lon_min)
    # convert directed into undirected graph if the geometries of two arcs match
    undirected_multi_graph = ox.get_undirected(directed_multigraph)
    G = gs.update_cost(undirected_multi_graph, pollution_df, weight_attr="length")
    assert G.number_of_edges() == undirected_multi_graph.number_of_edges()
    print(nx.info(G))

    # convert the undirected multi graph into an undirected simple graph with no loops or multi edges


    for u, v, k, data in G.edges(data=True, keys=True):
        assert "NO2_mean" in data
        assert data["NO2_mean"] > 0
        assert data["cost"] == data["NO2_mean"] * data["length"]

    # G.remove_edges_from(nx.selfloop_edges(G))
    edges_df = nx.to_pandas_edgelist(G, source="source", target="target")
    nodes_df = pd.DataFrame.from_dict(dict(G.nodes(data=True)), orient='index')
    nodes_df = nodes_df.rename(columns={"y": "lat", "x": "lon"})
    print(edges_df.loc[edges_df.key > 0])
    print(nodes_df)

    # save edges with pollution to CSV
    LONDONAQ_TINY_EDGES_FILENAME = "londonaq_tiny_edges.csv"
    LONDONAQ_TINY_NODES_FILENAME = "londonaq_tiny_nodes.csv"

    csv_output_dir.mkdir(exist_ok=True, parents=False)
    edges_df.to_csv(csv_output_dir / LONDONAQ_TINY_EDGES_FILENAME, index=False)
    nodes_df.to_csv(csv_output_dir / LONDONAQ_TINY_NODES_FILENAME, index=True, index_label="node")

# output is a CSV file representing an undirected simple graph

# convert the multi directed graph into a simple undirected graph
# save the simple undirected graph as a CSV file

if __name__=="__main__":
    typer.run(main)
