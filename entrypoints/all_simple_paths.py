"""Generate all simple paths in the graph in order to visualise the Pareto front"""

from typing import Optional
import logging
import typer
import geopandas as gpd
import osmnx as ox
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import networkx as nx
from cleanair.loggers import get_logger
from urbanroute.geospatial import update_cost, ellipse_bounding_box
from urbanroute.queries import HexGridQuery


def load_graph(
    secretfile: str,
    instance_id: str,
    source_lat: float,
    source_long: float,
    start_time: str,
    target_lat: float,
    target_long: float,
    upto_time: str,
    verbose: bool,
    logger,
):
    """
    load the graph from the database
    secretfile: Path to the database secretfile.
    instance_id: Id of the air quality trained model.
    sourceLat: latitude of the source point.
    sourceLong: longitude of the source point.
    targetLat: latitude of the target point.
    targetLong: longitude of the target point.
    verbose: enable debug logging.
    """
    if verbose:
        logger.setLevel(logging.DEBUG)
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

    gdf = gpd.GeoDataFrame.from_postgis(
        result_sql, result_query.dbcnxn.engine, crs=4326
    )
    gdf = gdf.rename(columns=dict(geom="geometry"))
    gdf.crs = "EPSG:4326"
    # gdf = gpd.GeoDataFrame(result_df, crs=4326, geometry="geom")
    logger.info("%s rows in hexgrid results", len(gdf))

    # use bounding box of surrounding ellipse to limit graph size
    box = ellipse_bounding_box((source_long, source_lat), (target_long, target_lat))
    G: nx.MultiDiGraph = ox.graph_from_bbox(box[0], box[1], box[2], box[3])
    logger.info(
        "%s nodes and %s edges in graph.", G.number_of_nodes(), G.number_of_edges()
    )
    logger.info("Mapping air quality predictions to the road network.")
    G = update_cost(G, gdf, cost_attr="NO2_mean", weight_attr="length")
    logger.debug("Printing basic stats for the graph:")
    logger.debug(ox.stats.basic_stats(G))


def get_path_values(
    G: nx.MultiDiGraph,
    source_lat: float,
    source_long: float,
    target_lat: float,
    target_long: float,
):
    """
    G: networkx multidigraph
    source_lat: latitude of the source point
    source_long: longitude of the source point
    target_lat: latitude of the target point
    target_long: longitude of the target point
    """
    distances = []
    pollutions = []
    nx.set_edge_attributes(G, 0, "freq")
    for path in nx.all_simple_paths(
        G,
        ox.distance.get_nearest_node(G, (source_lat, source_long)),
        ox.distance.get_nearest_node(G, (target_lat, target_long)),
    ):
        distance = 0
        pollution = 0
        for i in range(0, len(path) - 1):
            distance = distance + G.get_edge_data(path[i], path[i + 1])[0]["length"]
            pollution = pollution + G.get_edge_data(path[i], path[i + 1])[0]["gamma"]
        if distance < 1000 and pollution < 1000:
            for i in range(0, len(path) - 1):
                G[path[i]][path[i + 1]][0]["freq"] = (
                    G[path[i]][path[i + 1]][0]["freq"] + 1
                )
            distances.append(distance)
            pollutions.append(pollution)
    return (distances, pollution)


def main(  # pylint: disable=too-many-arguments
    secretfile: str,
    instance_id: str = typer.Option(
        "d5e691ef9a1f2e86743f614806319d93e30709fe179dfb27e7b99b9b967c8737",
        help="Id of the air quality trained model.",
    ),
    source_lat: float = 51.4920,
    source_long: float = -0.1225,
    start_time: Optional[str] = typer.Option(
        "2020-01-24T09:00:00",
        help="Beginning of air quality predictions (inclusive). ISO formatted string.",
    ),
    target_lat: float = 51.4960,
    target_long: float = -0.1200,
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
    logger = get_logger("Shortest path entrypoint")
    G: nx.MultiDiGraph = load_graph(
        secretfile,
        instance_id,
        source_lat,
        source_long,
        start_time,
        target_lat,
        target_long,
        upto_time,
        verbose,
        logger,
    )
    values = get_path_values(G, source_lat, source_long, target_lat, target_long)
    cmap = cm.ScalarMappable(
        norm=colors.Normalize(
            vmin=min([edge[2]["freq"] for edge in G.edges.data()]),
            vmax=max([edge[2]["freq"] for edge in G.edges.data()]),
        ),
        cmap=cm.inferno,
    )
    ox.plot_graph(
        G,
        edge_color=[
            cmap.to_rgba(cl) for cl in [edge[2]["freq"] for edge in G.edges.data()]
        ],
    )
    plt.scatter(values[0], values[1])
    plt.xlabel("distance")
    plt.ylabel("sum of pollution density")
    plt.show()


if __name__ == "__main__":
    typer.run(main)
