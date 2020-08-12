"""Find the least cost path from source to target by minimising air pollution."""

from typing import Tuple, List, Dict
import logging
import time
import math
import typer
import numpy as np
from fastapi import FastAPI
from graph_tool.all import load_graph
from routex import astar
from cleanair.loggers import get_logger
from urbanroute.geospatial import ellipse_bounding_box, coord_match


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
float_length = G.new_edge_property("double")
float_x = G.new_vertex_property("double")
float_y = G.new_vertex_property("double")
G.edge_properties["float_length"] = float_length
# pollution = G.new_edge_property("double")
# mean = G.edge_properties["NO2_mean"]
length = G.edge_properties["length"]
x = G.vertex_properties["x"]
y = G.vertex_properties["y"]
for v in G.get_vertices():
    pos[v] = [float(x[v]), float(y[v])]
    float_x[v] = float(x[v])
    float_y[v] = float(y[v])
for e in G.edges():
    float_length[e] = float(length[e])
    # pollution[e] = (float(mean[e])

# set up numpy array of vertices with just the
vertices = G.get_vertices(vprops=[float_x, float_y])
vertices = np.delete(vertices, 0, 1)


def return_route(
    source_coord: Tuple[float, float],
    target_coord: Tuple[float, float],
    attribute: str,
) -> List[Dict[str, str]]:
    """
    Find the least polluted path.
    secretfile: Path to the database secretfile.
    instance_id: Id of the air quality trained model.
    source: (source latitude, source longitude) for source point.
    target: (target latitude, target longitude) for target point.
    verbose: enable debug logging.
    """
    # find vertices in the graph that are close enough to the start/target coordinates
    # any vertex within the minimum rectangle is sufficient
    source = coord_match(vertices, source_coord, pos)
    target = coord_match(vertices, target_coord, pos)
    # create box around the source and target vertices to eliminate points
    # that are (probably) too far away to be part of a shortest path
    box = ellipse_bounding_box(pos[source], pos[target])

    lower_left = np.array([box[3], box[1]])
    upper_right = np.array([box[2], box[0]])
    # Euclidean heuristic. If a vertex is not in the box, make its heuristic value infinite
    # so that it is never extended
    def distance_heuristic(v, target, pos):
        return (
            math.sqrt(np.sum(np.square(pos[v].a - pos[target].a)))
            if np.all(np.less(lower_left, pos[v].a))
            and np.all(np.less(pos[v].a, upper_right))
            else math.inf
        )

    route = astar(G, source, target, attribute, distance_heuristic, pos)
    return [{"x": x[r], "y": y[r]} for r in route]


def main(  # pylint: disable=too-many-arguments
    source_lat: float = 51.510357,
    source_long: float = -0.116773,
    target_lat: float = 51.529972,
    target_long: float = -0.127676,
) -> List[Dict[str, str]]:
    """
    sourceLat: latitude of the source point.
    sourceLong: longitude of the source point.
    targetLat: latitude of the target point.
    targetLong: longitude of the target point.
    """
    return return_route(
        (source_lat, source_long), (target_lat, target_long), "float_length",
    )


if __name__ == "__main__":
    typer.run(main)


@APP.get("/route/")
async def get_route(
    source_lat: float, source_long: float, target_lat: float, target_long: float
) -> List[Dict[str, str]]:
    """
    API route to get route from A to B.
    sourceLat: latitude of the source point.
    sourceLong: longitude of the source point.
    targetLat: latitude of the target point.
    targetLong: longitude of the target point.
    """
    return return_route(
        (source_lat, source_long), (target_lat, target_long), "float_length",
    )
