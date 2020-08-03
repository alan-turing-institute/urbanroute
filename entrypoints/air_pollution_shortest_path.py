"""Find the least cost path from source to target by minimising air pollution."""

from typing import Tuple, Optional
import logging
import time
import typer
import math
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
print("Loading graph of London...")
start = time.time()
G = load_graph("../graphs/London.gt")
print("Graph loaded in", time.time() - start, "seconds")
logger.info("%s nodes and %s edges in the graph.", G.num_vertices, G.num_edges)
G.list_properties()
pos = G.new_vertex_property("vector<double>")
x = G.vertex_properties["x"]
y = G.vertex_properties["y"]
for v in G.get_vertices():
    pos[v] = [float(x[v]), float(y[v])]


class RouteVisitor(AStarVisitor):
    def __init__(self, target):
        self.target = target
        self.count = 0

    def examine_vertex(self, v):
        self.count = self.count + 1
        print(self.count)
        if self.count > 3000:
            print(self.count)
            print("The graph is too large")
            raise Exception("Search graph is too big")

    def edge_relaxed(self, e):
        if e.target() == self.target:
            print("stop", self.count)
            raise StopSearch()


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
    start = time.time()
    source = G.vertex(1)
    target = G.vertex(301859)
    # target = G.vertex(3)
    box = ellipse_bounding_box(pos[source], pos[target])

    def contains(x, y):
        return y < box[0] and y > box[1] and x > box[3] and x < box[2]

    # if a vertex is not in the box, make its heuristic value infinite
    def distance_heuristic(v, target, pos):
        math.sqrt(sum((pos[v].a - pos[target].a) ** 2)) if contains(
            float(x[v]), float(y[v])
        ) else math.inf

    dist, pred = astar_search(
        G,
        weight=G.edge_properties["length"],
        source=source,
        visitor=RouteVisitor(target),
        heuristic=lambda v: distance_heuristic(v, target, pos),
    )
    route = []
    v = target
    while v != source:
        route.append(v)
        v = G.vertex(pred[v])
    # print([{"x": x[r], "y": y[r]} for r in route])
    print("Route calculated in", time.time() - start, "seconds")
    return [{"x": x[r], "y": y[r]} for r in route]


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
