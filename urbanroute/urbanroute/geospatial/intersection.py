"""Geospatial intersection between graphs and dataframes."""

from typing import Any
from sqlalchemy import func
from cleanair.databases import DBReader
from cleanair.databases.tables import AirQualityResultTable, OSHighway
from cleanair.decorators import db_query
from cleanair.mixins import ResultQueryMixin
from cleanair.types import Source


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
