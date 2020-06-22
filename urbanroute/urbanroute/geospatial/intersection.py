"""Geospatial intersection between graphs and dataframes."""

import logging
from typing import Optional
import networkx as nx
import osmnx as ox
import geopandas as gpd


def update_cost(
    G: nx.Graph,
    gdf: gpd.GeoDataFrame,
    edge_df: Optional[gpd.GeoDataFrame] = None,
    cost_attr: Optional[str] = "cost",
    weight_attr: Optional[str] = "weight",
    key_attr: Optional[str] = "key",
):
    """Update the cost of edges the graph from a geo dataframe.

    Args:
        G: Input graph. Must have a geometry attribute on the edges.
        gdf: Must contain geometry column and value column.
        edge_df: The edge geo dataframe of the graph.
        weight: Name of the weight attribute. Default is 'weight'.

    Returns:
        Graph with updated cost attribute.
    """
    # convert G to geodataframe
    if edge_df is None:
        # for a multigraph, remember the keys
        for u, v, k in G.edges(keys=True):
            G[u][v][k][key_attr] = k

        # # create a geodataframe
        edge_df = ox.graph_to_gdfs(G, nodes=False, fill_edge_geometry=True)
        edge_df = edge_df.rename(columns=dict(u="source", v="target"))

    # check the crs of geometries
    if edge_df.crs == None and gdf.crs != None:
        edge_df.crs = gdf.crs
    elif gdf.crs == None and edge_df.crs != None:
        gdf.crs = edge_df.crs

    # get intersection of the geodataframes
    logging.info("%s rows in edge dataframe", len(edge_df))
    join = gpd.sjoin(edge_df, gdf, how="left")
    logging.info("%s rows in join dataframe", len(join))

    edges_in_join = set([(u,v) for u, v in zip(join["source"], join["target"])])
    for u, v in G.edges():
        assert (u, v) in edges_in_join or (v, u) in edges_in_join

    # group the edges and take average pollution
    for key, value in (
        join.groupby(["source", "target", "key"])[cost_attr].mean().iteritems()
    ):
        i, j, k = key[0], key[1], key[2]
        G[i][j][k]["gamma"] = value if value >= 0 else 0
        G[i][j][k][cost_attr] = value * G[i][j][k][weight_attr]

    return G
