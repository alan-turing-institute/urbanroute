"""Update the graph with pollution forecasts."""

import logging
from pathlib import Path
import geopandas as gpd
import typer
from cleanair.loggers import get_logger
from cleanair.types import Source
from urbanroute.geospatial import RoadQuery
from urbanroute.utils import FileManager, from_dataframes


def main(
    secretfile: str,
    cache_dir: Path = typer.Option("graphs", help="Directory to store graph."),
    overlay_dir: Path = typer.Option(
        "apps/routing/overlays", help="Directory to store overlay."
    ),
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
    nodes_df = result.get_nodes_df()

    # query the actual predictions to be used as the background
    overlay_sql = result.query_results(instance_id, Source.hexgrid, output_type="sql")
    overlay_df = gpd.GeoDataFrame.from_postgis(
        overlay_sql, result.dbcnxn.engine, crs=4326
    )
    overlay_df = overlay_df.loc[overlay_df.measurement_start_utc == timestamp]
    logger.info(
        "Writing the geodataframe as a PNG to be used as the overlay for the web app."
    )
    manager = FileManager(overlay_dir)
    manager.save_overlay_to_file(overlay_df)

    # query the predictions mapped to the roads
    logger.info("Loading air pollution results for the hex grid at time %s", timestamp)
    result_sql: str = result.pollution_on_roads(
        instance_id, timestamp, output_type="sql"
    )
    gdf = gpd.GeoDataFrame.from_postgis(result_sql, result.dbcnxn.engine, crs=4326)
    logger.debug("%s rows returned from the result query.", len(gdf))
    logger.debug(gdf)

    # add the edge attributes (only distance & pollution for now)
    G = from_dataframes(gdf, nodes_df)
    logger.info("Graph has %s edges and %s nodes", G.num_edges(), G.num_vertices())

    # save the graph tools to a file
    logger.info("Saving the graph to file.")
    manager = FileManager(cache_dir)
    manager.save_graph_to_file(G)


if __name__ == "__main__":
    typer.run(main)
