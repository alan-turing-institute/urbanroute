"""Perform A* on the graph"""
from graph_tool.all import AStarVisitor, astar_search, StopSearch


class RouteVisitor(AStarVisitor):
    """Custom functions for our A* implementation"""

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


def astar(G, source, target, edge_attribute: str, heuristic, pos):
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
        weight=G.edge_properties[edge_attribute],
        source=source,
        visitor=RouteVisitor(target),
        heuristic=lambda v: heuristic(v, target, pos),
    )[1]

    # backtrack through the graph to the source
    route = []
    v = target
    while v != source:
        route.append(v)
        v = G.vertex(pred[v])
    route.append(v)
    return route
