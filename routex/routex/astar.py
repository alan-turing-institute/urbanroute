from graph_tool.all import *


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


def astar(G, source, target, edge_attribute: str, heuristic, pos):
    # run A*
    dist, pred = astar_search(
        G,
        weight=G.edge_properties[edge_attribute],
        source=source,
        visitor=RouteVisitor(target),
        heuristic=lambda v: heuristic(v, target, pos),
    )

    # backtrack through the graph to the source
    route = []
    v = target
    while v != source:
        route.append(v)
        v = G.vertex(pred[v])
    route.append(v)
    return route
