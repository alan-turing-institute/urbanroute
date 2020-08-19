"""Perform MOSPP on the graph"""
import heapq
import numpy as np
from graph_tool.all import Vertex, EdgePropertyMap


class Label:
    """The label class, contains predecessor of label, resource costs, and the associated vertex"""

    def __init__(self, pred, resource: np.ndarray, assoc: Vertex):
        self.pred = pred
        self.resource = resource
        self.assoc = assoc

    def __gt__(self, other):
        return self.resource > other.resource

    def dominate(self, other):
        """Returns true iff this label dominates the other provided label"""
        return np.all(np.less_equal(self.resource, other.resource)) and np.any(
            np.less(self.resource, other.resource)
        )


def mospp(
    source: Vertex, target: Vertex, cost_1: EdgePropertyMap, cost_2: EdgePropertyMap
):
    """Run MOSPP on graph. Returns list of routes, each route being a list of vertices"""
    labels = [Label(None, np.array([0, 0]), source)]
    vertex_dict = {}
    while len(labels) != 0:
        current = heapq.heappop(labels)
        for out_edge in current.assoc.out_edges():
            new_label = Label(
                current,
                [
                    current.resource[0] + cost_1[out_edge],
                    current.resource[1] + cost_2[out_edge],
                ],
                out_edge.target(),
            )
            if out_edge.target() in vertex_dict:
                discard = False
                for vertex_label in vertex_dict[out_edge.target()]:
                    if vertex_label.dominate(new_label):
                        discard = True
                for vertex_label in vertex_dict[out_edge.target()]:
                    if new_label.dominate(vertex_label):
                        vertex_dict[out_edge.target()].remove(vertex_label)

                if not discard:
                    vertex_dict[out_edge.target()].append(new_label)
                    heapq.heappush(labels, new_label)
            else:
                vertex_dict[out_edge.target()] = [new_label]
                heapq.heappush(labels, new_label)
    routes = []
    route = []
    route.append(target)
    for label in vertex_dict[target]:
        v = target
        label_tracker = label
        while v != source:
            label_tracker = label_tracker.pred
            v = label_tracker.assoc
            route.append(v)
        routes.append(route)
        route = []
    print(routes)
    return routes
