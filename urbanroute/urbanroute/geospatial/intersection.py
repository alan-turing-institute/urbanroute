"""Geospatial intersection between graphs and dataframes."""

import logging
from typing import Optional
import networkx as nx
import osmnx as ox
import geopandas as gpd


def update_cost(  # pylint: disable=too-many-arguments
    G: nx.Graph,
    gdf: gpd.GeoDataFrame,
    edge_df: Optional[gpd.GeoDataFrame] = None,
    cost_attr: str = "cost",
    pollution_attr: str = "NO2_mean",
    weight_attr: str = "weight",
    key_attr: str = "key",
    source: str = "u",
    target: str = "v",
    key: str = "key",
) -> nx.Graph:
    """Update the cost of edges the graph from a geo dataframe.

    Args:
        G: Input graph. Must have a geometry attribute on the edges.
        gdf: Must contain geometry column and value column.

    Other Args:
        edge_df: The edge geo dataframe of the graph.
        cost_attr: Name of the cost function.
        weight_attr: Name of the weight function.
        key_attr: Name of the key for multi graphs.

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
        edge_df = edge_df.rename(columns=dict(u=source, v=target))

    # check the crs of geometries
    if not getattr(edge_df, "crs", None) and getattr(gdf, "crs", None):
        # set the coordinate system of the edges to be the same as the pollution
        edge_df.crs = gdf.crs
    elif not getattr(gdf, "crs", None) and getattr(edge_df, "crs", None):
        # set hte coordinate system of the pollution to be the same as the edges
        gdf.crs = edge_df.crs
    elif not getattr(edge_df, "crs", None) and not getattr(gdf, "crs", None):
        raise ValueError("The CRS for both edges and pollution geometries is not set")
    
    if gdf.crs != edge_df.crs:
        raise ValueError(f"The CRS of edges ({getattr(edge_df, 'crs', None)}) and pollution ({getattr(gdf, 'crs', None)}) geometries do not match")

    # get intersection of the geodataframes
    logging.info("%s rows in edge dataframe", len(edge_df))
    join = gpd.sjoin(edge_df, gdf, how="left")
    logging.info("%s rows in join dataframe", len(join))

    # group the edges and take average pollution
    for index, value in (
        join.groupby(join.index)[pollution_attr].mean().iteritems()
    ):
        i, j, k = index[0], index[1], index[2]
        G[i][j][k][pollution_attr] = value if value >= 0 else 0
        G[i][j][k][cost_attr] = value * G[i][j][k][weight_attr]

    return G
