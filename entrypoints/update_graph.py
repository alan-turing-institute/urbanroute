"""Update the graph with pollution forecasts."""

import logging
from typing import Any, TYPE_CHECKING
import geopandas as gpd
from sqlalchemy import func
import typer
from cleanair.databases import DBReader
from cleanair.databases.tables import AirQualityResultTable, OSHighway
from cleanair.decorators import db_query
from cleanair.loggers import get_logger
from cleanair.mixins import ResultQueryMixin
from cleanair.types import Source

if TYPE_CHECKING:
    import pandas as pd

class ResultQuery(ResultQueryMixin, DBReader):
    """Class for querying air quality results."""

    @property
    def result_table(self) -> AirQualityResultTable:
        """The sqlalchemy table to query."""
        return AirQualityResultTable

    @db_query
    def pollution_on_roads(self, instance_id: str, timestamp: str) -> Any:
        """Map air pollution forecasts on the hexgrid to the road network."""
        # use a subquery to get the forecasts from the result table
        result_sq = self.query_results(instance_id, Source.hexgrid, output_type="subquery")

        with self.dbcnxn.open_session() as session:
            roads = (
                # take the mean and variance of each hexgrid cell the road passes through
                session.query(
                    OSHighway,
                    (func.avg(result_sq.c.NO2_mean) * OSHighway.length).label("NO2_mean"),
                    (func.avg(result_sq.c.NO2_var)).label("NO2_var"),
                )
                # join on the intersection of the road network and hexgrid
                .join(result_sq, func.st_intersects(OSHighway.geom, result_sq.c.geom))
                .filter(result_sq.c.measurement_start_utc == timestamp)
                # group by the id of the road
                .group_by(OSHighway.toid)
            )
            return roads

def main(
    secretfile: str,
    instance_id: str = typer.Option(
        "d5e691ef9a1f2e86743f614806319d93e30709fe179dfb27e7b99b9b967c8737",
        help="Id of the model fit.",
    ),
    timestamp: str = typer.Option("2020-01-24T09:00:00", help="Timestamp to query air quality result."),
    verbose: bool = typer.Option(False, help="Verbose output"),
) -> None:
    """Main method for updating the graph with pollution values from an instance id."""
    logger = get_logger("Loading graph")
    if verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("Connecting to the database.")
    result = ResultQuery(secretfile=secretfile)

    logger.info("Loading air pollution results for the hex grid at time %s", timestamp)

    # DataFrame: road_id, startnode, endnode, NO2_mean, NO2_var, length, geom(str)
    # for loop (starnode, endnode)

    # 1. create a empty graph tools graph
    # 2. load the graph from G.add_edge_list(df.values, hashed=True)
    # 3. save the graph tools to a file
    result_sql: str = result.pollution_on_roads(instance_id, timestamp, output_type="sql")
    gdf = gpd.GeoDataFrame.from_postgis(result_sql, result.dbcnxn.engine, crs=4326)
    logger.debug("%s rows returned from the result query.", len(gdf))
    logger.debug(gdf)

if __name__ == "__main__":
    typer.run(main)
