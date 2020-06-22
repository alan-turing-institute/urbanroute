"""Geospatial intersection between graphs and dataframes."""

from typing import Optional
import networkx as nx
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

        # create a geodataframe
        edge_df = gpd.GeoDataFrame(nx.to_pandas_edgelist(G), geometry="geometry")
        # edge_df = edge_df.dropna(subset=['source', 'target', 'geometry'])
        edge_df = edge_df.dropna(subset=["geometry"])

    # check the crs of geometries
    if edge_df.crs == None and gdf.crs != None:
        edge_df.crs = gdf.crs
    elif gdf.crs == None and edge_df.crs != None:
        gdf.crs = edge_df.crs

    # get intersection of the geodataframes
    join = gpd.sjoin(edge_df, gdf, how="left")

    # group the edges and take average pollution
    for key, value in (
        join.groupby(["source", "target", "key"])[cost_attr].mean().iteritems()
    ):
        i, j, k = key[0], key[1], key[2]
        G[i][j][k]["gamma"] = value if value >= 0 else 0
        G[i][j][k][cost_attr] = value * G[i][j][k][weight_attr]

    return G
