"""Geospatial intersection between graphs and dataframes."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from sqlalchemy import func
from cleanair.databases import DBReader
from cleanair.databases.tables import AirQualityResultTable, OSHighway
from cleanair.decorators import db_query
from cleanair.mixins import ResultQueryMixin
from cleanair.types import Source

if TYPE_CHECKING:
    import pandas as pd


class RoadQuery(ResultQueryMixin, DBReader):
    """Class for querying air quality results on roads."""

    # pylint: disable=no-member
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

    @db_query
    def cast_roads_to_linestring(self) -> Any:
        """Cast the roads geometry from MultiLineString to LineString."""
        with self.dbcnxn.open_session() as session:
            dump_points = session.query(
                OSHighway.toid.label("edge_id"),
                OSHighway.startnode,
                OSHighway.endnode,
                (func.ST_DumpPoints(OSHighway.geom)).geom.label(
                    "geom"
                ),  # the point geom
                (func.ST_DumpPoints(OSHighway.geom))
                .path[2]
                .label("path_id"),  # number of point in sequence
            ).subquery()
            linestrings = session.query(
                dump_points.c.edge_id,
                dump_points.c.startnode,
                dump_points.c.endnode,
                func.ST_MakeLine(dump_points.c.geom).label("geom"),
            ).group_by(
                dump_points.c.edge_id, dump_points.c.startnode, dump_points.c.endnode
            )
            return linestrings

    @db_query
    def __query_endpoints(self, linestrings, function, column) -> Any:
        """Get either start or end nodes."""
        with self.dbcnxn.open_session() as session:
            return session.query(
                column,
                (function(linestrings.c.geom)).label("geom"),
                (func.ST_X(function(linestrings.c.geom))).label("lon"),
                (func.ST_Y(function(linestrings.c.geom))).label("lat"),
            ).group_by(column, linestrings.c.geom)

    @db_query
    def query_start_nodes(self) -> Any:
        """Get the location of nodes in the road network.

        Notes:
            This uses the unique start and end of edges to get the nodes.
        """
        linestrings = self.cast_roads_to_linestring(output_type="subquery")
        return self.__query_endpoints(
            linestrings, func.ST_StartPoint, linestrings.c.startnode
        )

    @db_query
    def query_end_nodes(self) -> Any:
        """Get the end nodes."""
        linestrings = self.cast_roads_to_linestring(output_type="subquery")
        return self.__query_endpoints(
            linestrings, func.ST_EndPoint, linestrings.c.endnode
        )

    def get_nodes_df(self) -> pd.DataFrame:
        """Get all nodes in the London graph."""
        # get the nodes in the graph
        startnodes = self.query_start_nodes(output_type="df")
        endnodes = self.query_end_nodes(output_type="df")
        startnodes = startnodes.rename(columns=dict(startnode="node"))
        endnodes = endnodes.rename(columns=dict(endnode="node"))
        self.logger.info("%s start nodes, %s end nodes", len(startnodes), len(endnodes))
        nodes_df = startnodes.append(endnodes)
        nodes_df = nodes_df.drop_duplicates(subset="node")
        nodes_df = nodes_df.set_index("node")
        self.logger.info("%s nodes after removing duplicates", len(nodes_df))
        return nodes_df
