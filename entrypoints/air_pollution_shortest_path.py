"""Find the least cost path from source to target by minimising air pollution."""

from typing import Optional
import typer
import geopandas as gpd
import osmnx as ox
import networkx as nx
from cleanair.databases.queries import AirQualityResultQuery
from cleanair.loggers import get_logger
import routex as rx
from urbanroute.geospatial import update_cost
from urbanroute.queries import HexGridQuery

def main(instance_id: str, secretfile: str, source: Optional[str] = None, target: Optional[str] = None):
    """
    instance_id: Id of the air quality trained model.

    secretfile: Path to the database secretfile.
    """
    logger = get_logger("Shortest path entrypoint")

    # TODO change this to a AirQualityResultQuery
    result_query = HexGridQuery(secretfile=secretfile)
    logger.info("Querying results from an air quality model")
    result_df = result_query.query_results(instance_id, join_hexgrid=True, output_type="df")
    logger.debug(result_df.head())

    gdf = gpd.GeoDataFrame(result_df, crs=4326, geometry="geom")
    logger.info("%s rows in hexgrid results", len(gdf))

    G: nx.MultiDiGraph = ox.graph_from_address("British Library")
    logger.info("%s nodes and %s edges in graph.", G.number_of_nodes(), G.number_of_edges)

    logger.info("Mapping air quality predictions to the road network.")
    G = update_cost(G, gdf, cost_attr="NO2_mean", weight_attr="length")

if __name__ == "__main__":
    typer.run(main)
