"""Geospatial intersection between graphs and dataframes."""

import logging
from typing import Any, Optional
import networkx as nx
import osmnx as ox
import geopandas as gpd
from sqlalchemy import func
from cleanair.databases import DBReader
from cleanair.databases.tables import AirQualityResultTable, OSHighway
from cleanair.decorators import db_query
from cleanair.mixins import ResultQueryMixin
from cleanair.types import Source


class RoadQuery(ResultQueryMixin, DBReader):
    """Class for querying air quality results on roads."""

    @property
    def result_table(self) -> AirQualityResultTable:
        """The sqlalchemy table to query."""
        return AirQualityResultTable

    @db_query
    def pollution_on_roads(self, instance_id: str, timestamp: str) -> Any:
        """Map air pollution forecasts on the hexgrid to the road network."""
        # use a subquery to get the forecasts from the result table
        result_sq = self.query_results(
            instance_id, Source.hexgrid, output_type="subquery"
        )

        with self.dbcnxn.open_session() as session:
            roads = (
                # take the mean and variance of each hexgrid cell the road passes through
                session.query(
                    OSHighway,
                    (func.avg(result_sq.c.NO2_mean) * OSHighway.length).label(
                        "NO2_mean"
                    ),
                    (func.avg(result_sq.c.NO2_var)).label("NO2_var"),
                )
                # join on the intersection of the road network and hexgrid
                .join(
                    result_sq, func.st_intersects(OSHighway.geom, result_sq.c.geom)
                ).filter(result_sq.c.measurement_start_utc == timestamp)
                # group by the id of the road
                .group_by(OSHighway.toid)
            )
            return roads


def update_cost(  # pylint: disable=too-many-arguments
    G: nx.Graph,
    gdf: gpd.GeoDataFrame,
    edge_df: Optional[gpd.GeoDataFrame] = None,
    cost_attr: Optional[str] = "cost",
    weight_attr: Optional[str] = "weight",
    key_attr: Optional[str] = "key",
) -> nx.Graph:
    """Update the cost of edges the graph from a geo dataframe.

    Args:
        G: Input graph. Must have a geometry attribute on the edges.
        gdf: Must contain geometry column and value column.
        edge_df: The edge geo dataframe of the graph.

    Other Args:
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
        edge_df = edge_df.rename(columns=dict(u="source", v="target"))

    # check the crs of geometries
    if edge_df.crs is None and not gdf.crs is None:
        edge_df.crs = gdf.crs
    elif gdf.crs is None and not edge_df.crs is None:
        gdf.crs = edge_df.crs

    # get intersection of the geodataframes
    logging.info("%s rows in edge dataframe", len(edge_df))
    join = gpd.sjoin(edge_df, gdf, how="left")
    logging.info("%s rows in join dataframe", len(join))

    edges_in_join = zip(join["source"], join["target"])
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
