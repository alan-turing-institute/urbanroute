"""Helper functions for importing/exporting graphs."""

from __future__ import annotations
from typing import TYPE_CHECKING
from graph_tool import Graph

if TYPE_CHECKING:
    import pandas as pd

def from_dataframes(
    edge_df: pd.DataFrame, vertex_df: pd.DataFrame, source: str = "startnode", target: str = "endnode"
) -> Graph:
    """Graph from edge and vertex dataframes. Copies attributes as well."""
    # create directed graph from edge list
    G = Graph(directed=True)
    G.add_edge_list(edge_df[[source, target]].values, hashed=True)

    # reorder vertex dataframe based on order of vertices in graph
    vertex_df = vertex_df.reindex(G.vertices())

    # set vertex properties - all are assumed to be float
    lat = G.new_vertex_property("float", vals=vertex_df.lat)
    lon = G.new_vertex_property("float", vals=vertex_df.lon)
    G.vertex_properties["lat"] = lat
    G.vertex_properties["lon"] = lon

    # set edge properties
    length = G.new_edge_property("float", vals=edge_df["length"])
    no2 = G.new_edge_property("float", vals=edge_df["NO2_mean"])
    G.edge_properties["NO2_mean"] = no2
    G.edge_properties["length"] = length

    return G
