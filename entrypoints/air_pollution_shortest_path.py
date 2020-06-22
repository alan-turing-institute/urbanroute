"""Find the least cost path from source to target by minimising air pollution."""

from typing import Optional
import logging
import typer
import geopandas as gpd
import osmnx as ox
import networkx as nx
from cleanair.databases.queries import AirQualityResultQuery
from cleanair.loggers import get_logger

from routex.types import Node
from urbanroute.geospatial import update_cost
from urbanroute.queries import HexGridQuery


def main(  # pylint: disable=too-many-arguments
    secretfile: str,
    instance_id: str = "d5e691ef9a1f2e86743f614806319d93e30709fe179dfb27e7b99b9b967c8737",
    source: Optional[Node] = None,
    start_time: Optional[str] = "2020-01-24T09:00:00",
    target: Optional[Node] = None,
    upto_time: Optional[str] = "2020-01-24T10:00:00",
    verbose: Optional[bool] = False,
):
    """
    instance_id: Id of the air quality trained model.

    secretfile: Path to the database secretfile.
    """
    logger = get_logger("Shortest path entrypoint")
    if verbose:
        logger.level = logging.DEBUG

    # TODO change this to a AirQualityResultQuery
    result_query = HexGridQuery(secretfile=secretfile)
    logger.info("Querying results from an air quality model")
    result_sql = result_query.query_results(
        instance_id,
        join_hexgrid=True,
        output_type="sql",
        start_time=start_time,
        upto_time=upto_time,
    )
    logger.debug(result_sql)

    gdf = gpd.GeoDataFrame.from_postgis(result_sql, result_query.dbcnxn.engine, crs=4326)
    gdf = gdf.rename(columns=dict(geom="geometry"))
    gdf.crs = "EPSG:4326"
    # gdf = gpd.GeoDataFrame(result_df, crs=4326, geometry="geom")
    logger.info("%s rows in hexgrid results", len(gdf))

    G: nx.MultiDiGraph = ox.graph_from_address("British Library")
    logger.info(
        "%s nodes and %s edges in graph.", G.number_of_nodes(), G.number_of_edges()
    )

    logger.info("Mapping air quality predictions to the road network.")
    G = update_cost(G, gdf, cost_attr="NO2_mean", weight_attr="length")
    logger.debug("Printing basic stats for the graph:")
    logger.debug(ox.stats.basic_stats(G))


    for i, (u, v, k, data) in enumerate(G.edges(keys=True, data=True)):
        if i > 10:
            break
        print(u, v, k, data)
        print()

if __name__ == "__main__":
    typer.run(main)
