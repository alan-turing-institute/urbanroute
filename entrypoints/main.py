"""Find the least cost path from source to target by minimising air pollution."""

from typing import Tuple, List, Dict
import logging
import time
import typer
import numpy as np
from fastapi import FastAPI
from graph_tool.all import load_graph, EdgePropertyMap
from haversine import haversine
from cleanair.loggers import get_logger
from routex import astar, bidirectional_mospp
from urbanroute.geospatial import (
    ellipse_bounding_box,
    coord_match,
    remove_leaves,
    remove_paths,
)

APP = FastAPI()
logger = get_logger("Shortest path entrypoint")
logger.setLevel(logging.DEBUG)
logger.info("Loading graph of London...")
start = time.time()
G = load_graph("../graphs/Trafalgar.gt")
logger.info("Graph loaded in %s seconds.", time.time() - start)
logger.info("%s nodes and %s edges in the graph.", G.num_vertices, G.num_edges)

# add position property, and add float versions of string edge attributes
pos = G.new_vertex_property("vector<double>")
float_length = G.new_edge_property("double")
float_x = G.new_vertex_property("double")
float_y = G.new_vertex_property("double")
G.edge_properties["float_length"] = float_length
pollution = G.new_edge_property("double")
mean = G.edge_properties["NO2_mean"]
length = G.edge_properties["length"]
x = G.vertex_properties["x"]
y = G.vertex_properties["y"]
for v in G.get_vertices():
    pos[v] = [float(x[v]), float(y[v])]
    float_x[v] = float(x[v])
    float_y[v] = float(y[v])
for e in G.edges():
    float_length[e] = float(length[e])
    pollution[e] = float(mean[e]) * float(length[e])

inside = G.new_vertex_property("bool")
del_list = G.new_vertex_property("bool")
for v in G.vertices():
    del_list[v] = True

# do graph simplification
remove_leaves(G, del_list)
remove_paths(G, del_list, pos, length, pollution)

# set up numpy array of vertices with just the position
vertices = G.get_vertices(vprops=[float_x, float_y])
vertices = np.delete(vertices, 0, 1)


def return_a_star(
    source_coord: Tuple[float, float],
    target_coord: Tuple[float, float],
    attribute: EdgePropertyMap,
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
    indices = np.all(
        np.logical_and(lower_left <= vertices, vertices <= upper_right), axis=1
    )
    # include the main delete list as a filter also
    inside.a = np.logical_and(indices, del_list.a)
    # preserve source and target
    inside[source] = True
    inside[target] = True
    G.set_vertex_filter(inside)

    def distance_heuristic(v, target, pos):
        return haversine(
            (pos[v].a[0], pos[v].a[1]), (pos[target].a[0], pos[target].a[1]), unit="m"
        )

    route = astar(G, source, target, attribute, distance_heuristic, pos)
    return [{"x": x[r], "y": y[r]} for r in route]


def return_mospp(
    source_coord: Tuple[float, float], target_coord: Tuple[float, float]
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
    indices = np.all(
        np.logical_and(lower_left <= vertices, vertices <= upper_right), axis=1
    )
    # include the main delete list as a filter also
    inside.a = np.logical_and(indices, del_list.a)
    # preserve source and target
    inside[source] = True
    inside[target] = True
    G.set_vertex_filter(inside)
    # get route
    routes = bidirectional_mospp(
        G.vertex(source), G.vertex(target), float_length, pollution
    )
    return [[{"x": x[r], "y": y[r]} for r in route] for route in routes]


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
    return return_a_star(
        (source_lat, source_long), (target_lat, target_long), float_length
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
    return return_a_star(
        (source_lat, source_long), (target_lat, target_long), float_length
    )


@APP.get("/pollution/")
async def get_pollution(
    source_lat: float, source_long: float, target_lat: float, target_long: float
) -> List[Dict[str, str]]:
    """
    API route to get route from A to B.
    sourceLat: latitude of the source point.
    sourceLong: longitude of the source point.
    targetLat: latitude of the target point.
    targetLong: longitude of the target point.
    """
    return return_a_star(
        (source_lat, source_long), (target_lat, target_long), pollution
    )


@APP.get("/mospp/")
async def get_mospp(
    source_lat: float, source_long: float, target_lat: float, target_long: float
) -> List[Dict[str, str]]:
    """
    API route to get route from A to B.
    sourceLat: latitude of the source point.
    sourceLong: longitude of the source point.
    targetLat: latitude of the target point.
    targetLong: longitude of the target point.
    """
    return return_mospp((source_lat, source_long), (target_lat, target_long))
