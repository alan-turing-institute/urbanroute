"""Find the least cost path from source to target by minimising air pollution."""

from typing import Tuple, Optional
import logging
import time
import typer
import math
import numpy as np
from graph_tool.all import *
from fastapi import FastAPI
from cleanair.loggers import get_logger
from urbanroute.geospatial import update_cost, ellipse_bounding_box
from urbanroute.queries import HexGridQuery


APP = FastAPI()
logger = get_logger("Shortest path entrypoint")
logger.setLevel(logging.DEBUG)
logger.info("Loading graph of London...")
start = time.time()
G = load_graph("../graphs/London.gt")
logger.info("Graph loaded in %s seconds.", time.time() - start)
logger.info("%s nodes and %s edges in the graph.", G.num_vertices, G.num_edges)

# add position property, and add float versions of string edge attributes
pos = G.new_vertex_property("vector<double>")
floatLength = G.new_edge_property("double")
floatX = G.new_vertex_property("double")
floatY = G.new_vertex_property("double")
G.edge_properties["floatLength"] = floatLength
# pollution = G.new_edge_property("double")
# G.edge_properties["pollution"] = pollution
length = G.edge_properties["length"]
# mean = G.edge_properties["NO2_mean"]
x = G.vertex_properties["x"]
y = G.vertex_properties["y"]
for v in G.get_vertices():
    pos[v] = [float(x[v]), float(y[v])]
    floatX[v] = float(x[v])
    floatY[v] = float(y[v])
for e in G.edges():
    floatLength[e] = float(length[e])
    # pollution[e] = (float(mean[e])


class RouteVisitor(AStarVisitor):
    def __init__(self, target):
        self.target = target
        self.count = 0

    def examine_vertex(self, v):
        self.count = self.count + 1
        # we have examined too many vertices, running out of memory
        if self.count > 20000:
            # logger.log("The graph is too large")
            raise Exception("Search graph is too big")

    def edge_relaxed(self, e):
        # stop if the target vertex has been reached
        if e.target() == self.target:
            # logger.log("Stopped after examining %s vertices", self.count)
            raise StopSearch()


# set up numpy array of vertices with just the
V = G.get_vertices(vprops=[floatX, floatY])
V = np.delete(V, 0, 1)


def return_route(
    secretfile: str,
    instance_id,
    sourceCoord: Tuple[float, float],
    start_time: str,
    targetCoord: Tuple[float, float],
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

    start = time.time()
    # find vertices in the graph that are close enough to the start/target coordinates
    # any vertex within the minimum rectangle is sufficient
    minimum = 0.0009
    ll = np.array([sourceCoord[1] - minimum, sourceCoord[0] - minimum])
    ur = np.array([sourceCoord[1] + minimum, sourceCoord[0] + minimum])
    inidx = np.all(np.logical_and(ll <= V, V <= ur), axis=1)
    inbox = np.where(inidx == 1)
    source = None
    for v in inbox[0]:
        if (
            math.sqrt(
                np.sum(np.square(pos[v].a - np.array([sourceCoord[1], sourceCoord[0]])))
            )
            < minimum
        ):
            minimum = math.sqrt(
                np.sum(np.square(pos[v].a - np.array([sourceCoord[1], sourceCoord[0]])))
            )
            source = v
    minimum = 0.0009
    ll = np.array([targetCoord[1] - minimum, targetCoord[0] - minimum])
    ur = np.array([targetCoord[1] + minimum, targetCoord[0] + minimum])
    inidx = np.all(np.logical_and(ll <= V, V <= ur), axis=1)
    inbox = np.where(inidx == 1)
    target = None
    for v in inbox[0]:
        if (
            math.sqrt(
                np.sum(np.square(pos[v].a - np.array([targetCoord[1], targetCoord[0]])))
            )
            < minimum
        ):
            minimum = math.sqrt(
                np.sum(np.square(pos[v].a - np.array([targetCoord[1], targetCoord[0]])))
            )
            target = v

    # create box around the source and target vertices to eliminate points that are too far away
    box = ellipse_bounding_box(pos[source], pos[target])

    ll = np.array([box[3], box[1]])
    ur = np.array([box[2], box[0]])
    # Euclidean heuristic. If a vertex is not in the box, make its heuristic value infinite
    # so that it is never extended
    def distance_heuristic(v, target, pos):
        return (
            math.sqrt(np.sum(np.square(pos[v].a - pos[target].a)))
            if np.all(np.less(ll, pos[v].a)) and np.all(np.less(pos[v].a, ur))
            else math.inf
        )

    start = time.time()
    dist, pred = astar_search(
        G,
        weight=G.edge_properties["floatLength"],
        source=source,
        visitor=RouteVisitor(target),
        heuristic=lambda v: distance_heuristic(v, target, pos),
    )

    # backtrack through the graph
    route = []
    v = target
    while v != source:
        route.append(v)
        v = G.vertex(pred[v])
    route.append(v)
    print("Route calculated in", time.time() - start, "seconds")
    print(dist[target])
    return [{"x": x[r], "y": y[r]} for r in route]


def main(  # pylint: disable=too-many-arguments
    secretfile: str,
    instance_id: str = typer.Option(
        "d5e691ef9a1f2e86743f614806319d93e30709fe179dfb27e7b99b9b967c8737",
        help="Id of the air quality trained model.",
    ),
    source_lat: float = 51.510357,
    source_long: float = -0.116773,
    start_time: Optional[str] = typer.Option(
        "2020-01-24T09:00:00",
        help="Beginning of air quality predictions (inclusive). ISO formatted string.",
    ),
    target_lat: float = 51.529972,
    target_long: float = -0.127676,
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