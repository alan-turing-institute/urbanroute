"""Perform A* on the graph"""
from typing import Tuple
from graph_tool.all import (
    AStarVisitor,
    astar_search,
    StopSearch,
    Graph,
    EdgePropertyMap,
)
import numpy as np


class RouteVisitor(AStarVisitor):
    """Custom functions for our A* implementation"""

    def __init__(self, target: int):
        self.target = target
        self.count = 0

    def edge_relaxed(self, e: Tuple[int, int]):
        # stop if the target vertex has been reached
        if e.target() == self.target:
            # logger.log("Stopped after examining %s vertices", self.count)
            raise StopSearch()


def astar(
    G: Graph,
    source: int,
    target: int,
    edge_attribute: EdgePropertyMap,
    heuristic,
    pos: np.ndarray,
) -> np.ndarray:
    """
    Perform A* with given heuristic
    Args:
        G: graph
        source: start vertex
        target: end vertex (search terminates here)
        edge_attribute: the edge attribute that defines the cost of an edge
        heuristic: a function that underestimates the distance from any vertex to the target
        pos: positional attribute for vertices
    Returns: a list of vertices from the source to the target
    """
    # run A*
    pred = astar_search(
        G,
        weight=edge_attribute,
        source=source,
        visitor=RouteVisitor(target),
        heuristic=lambda v: heuristic(v, target, pos),
    )[1]

    # backtrack through the graph to the source
    route = []
    v = target
    while v != source:
        if v == pred[v]:
            raise Exception("The start is not connected to the target")
        route.append(v)
        v = G.vertex(pred[v])
    route.append(v)
    return route
