"""Update the graph with pollution forecasts."""

import logging
import geopandas as gpd
from graph_tool import Graph
import typer
import numpy as np
from cleanair.loggers import get_logger
from urbanroute.geospatial import RoadQuery


def main(
    secretfile: str,
    instance_id: str = typer.Option(
        "d5e691ef9a1f2e86743f614806319d93e30709fe179dfb27e7b99b9b967c8737",
        help="Id of the model fit.",
    ),
    timestamp: str = typer.Option(
        "2020-01-24T09:00:00", help="Timestamp to query air quality result."
    ),
    verbose: bool = typer.Option(False, help="Verbose output"),
) -> None:
    """Main method for updating the graph with pollution values from an instance id."""
    logger = get_logger("Loading graph")
    if verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("Connecting to the database.")
    result = RoadQuery(secretfile=secretfile)

    logger.info("Loading air pollution results for the hex grid at time %s", timestamp)

    # DataFrame: road_id, startnode, endnode, NO2_mean, NO2_var, length, geom(str)
    # for loop (starnode, endnode)

    result_sql: str = result.pollution_on_roads(
        instance_id, timestamp, output_type="sql"
    )
    gdf = gpd.GeoDataFrame.from_postgis(result_sql, result.dbcnxn.engine, crs=4326)
    logger.debug("%s rows returned from the result query.", len(gdf))
    logger.debug(gdf)

    # create an empty graph and add edges from the dataframe
    G = Graph(directed=True)
    logger.debug("Dataframe columns: %s", gdf.columns)
    # source = G.new_edge_property("string")
    # target = G.new_edge_property("string")
    G.add_edge_list(gdf[["startnode", "endnode"]].values, hashed=True)
    logger.info("Graph has %s edges and %s nodes", G.num_edges(), G.num_vertices())
    distance = G.new_edge_property("float", vals=gdf["length"])
    no2 = G.new_edge_property("float", vals=gdf["NO2_mean"])
    logger.debug("The distance attribute vector is %s", distance)
    logger.debug("The no2 attribute is %s", no2)

    # 3. save the graph tools to a file


if __name__ == "__main__":
    typer.run(main)
