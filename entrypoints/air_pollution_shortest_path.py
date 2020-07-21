"""Find the least cost path from source to target by minimising air pollution."""

from typing import Tuple, Optional
import logging
import time
import typer
import geopandas as gpd
import osmnx as ox
import networkx as nx
from graph_tool.all import *
from fastapi import FastAPI
from cleanair.loggers import get_logger
from urbanroute.geospatial import update_cost, ellipse_bounding_box
from urbanroute.queries import HexGridQuery


APP = FastAPI()
logger = get_logger("Shortest path entrypoint")
logger.setLevel(logging.DEBUG)
print("Loading full graph of London...")
start = time.time()
G = load_graph("../graphs/London.graphml")
print("Graph loaded in", time.time() - start, "seconds")
logger.info("%s nodes and %s edges in the graph.", G.num_vertices, G.num_edges)
print("Loading air pollution results")
secretfile: str = "/home/james/clean-air-infrastructure/.secrets/db_secrets_ad.json"
instance_id: str = "d5e691ef9a1f2e86743f614806319d93e30709fe179dfb27e7b99b9b967c8737"
start_time: Optional[str] = "2020-01-24T09:00:00"
upto_time: Optional[str] = "2020-01-24T10:00:00"
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
astar_search(G,)


def return_route(
    secretfile: str,
    instance_id,
    source: Tuple[float, float],
    start_time: str,
    target: Tuple[float, float],
    upto_time: str,
    verbose: bool = True,
):
    """
    Find the least polluted path.
    secretfile: Path to the database secretfile.
    instance_id: Id of the air quality trained model.
    source: (source latitude, source longitude) for source point.
    target: (target latitude, target longitude) for target point.
    verbose: enable debug logging.
    """
    # use bounding box of surrounding ellipse to limit graph size
    # box = ellipse_bounding_box((source[1], source[0]), (target[1], target[0]))
    # G: nx.MultiDiGraph = ox.graph_from_bbox(box[0], box[1], box[2], box[3])
    # logger.info(
    # "%s nodes and %s edges in graph.", G.number_of_nodes(), G.number_of_edges()
    # )

    logger.info("Mapping air quality predictions to the road network.")
    G = update_cost(G, gdf, cost_attr="NO2_mean", weight_attr="length")
    logger.debug("Printing basic stats for the graph:")
    logger.debug(ox.stats.basic_stats(G))
    start = time.time()

    route = nx.dijkstra_path(
        G,
        ox.distance.get_nearest_node(G, source),
        ox.distance.get_nearest_node(G, target),
        weight="NO2_mean",
    )
    print(time.time() - start)
    return [G.nodes[r] for r in route]


def main(  # pylint: disable=too-many-arguments
    secretfile: str,
    instance_id: str = typer.Option(
        "d5e691ef9a1f2e86743f614806319d93e30709fe179dfb27e7b99b9b967c8737",
        help="Id of the air quality trained model.",
    ),
    source_lat: float = 51.4929,
    source_long: float = -0.1215,
    start_time: Optional[str] = typer.Option(
        "2020-01-24T09:00:00",
        help="Beginning of air quality predictions (inclusive). ISO formatted string.",
    ),
    target_lat: float = 51.5929,
    target_long: float = -0.1215,
    upto_time: Optional[str] = typer.Option(
        "2020-01-24T10:00:00",
        help="End of air quality predictions (exclusive). ISO formatted string.",
    ),
    verbose: Optional[bool] = typer.Option(False, help="Output debug logs.",),
):
    """
    secretfile: Path to the database secretfile.
    instance_id: Id of the air quality trained model.
    sourceLat: latitude of the source point.
    sourceLong: longitude of the source point.
    targetLat: latitude of the target point.
    targetLong: longitude of the target point.
    verbose: enable debug logging.
    """
    return_route(
        secretfile,
        instance_id,
        (source_lat, source_long),
        start_time,
        (target_lat, target_long),
        upto_time,
        verbose,
    )


if __name__ == "__main__":
    typer.run(main)


@APP.get("/route/")
async def get_route(
    source_lat: float, source_long: float, target_lat: float, target_long: float
):
    """
    API route to get route from A to B.
    sourceLat: latitude of the source point.
    sourceLong: longitude of the source point.
    targetLat: latitude of the target point.
    targetLong: longitude of the target point.
    """
    secretfile: str = "/home/james/clean-air-infrastructure/.secrets/db_secrets_ad.json"
    instance_id: str = "d5e691ef9a1f2e86743f614806319d93e30709fe179dfb27e7b99b9b967c8737"
    start_time: Optional[str] = "2020-01-24T09:00:00"
    upto_time: Optional[str] = "2020-01-24T10:00:00"
    return return_route(
        secretfile,
        instance_id,
        (source_lat, source_long),
        start_time,
        (target_lat, target_long),
        upto_time,
    )
