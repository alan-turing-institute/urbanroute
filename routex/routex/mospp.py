"""Perform MOSPP on the graph"""
import heapq
import numpy as np
from graph_tool.all import Vertex, EdgePropertyMap


class Label:
    """The label class, contains the label predecessor of the label, resource costs, and the associated vertex"""

    def __init__(self, pred, resource: np.ndarray, assoc: Vertex):
        # predecessor label
        self.pred = pred
        # array of resource values
        self.resource = resource
        # associated vertex
        self.assoc = assoc
        # true if it has been excluded
        self.removed = False

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
    # labels associated with each vertex
    vertex_dict = {}
    while len(labels) != 0:
        # pick lexicographically smallest label if it isn't
        # already excluded
        current = heapq.heappop(labels)
        if not current.removed:
            for out_edge in current.assoc.out_edges():
                # create the new label with updated resource values
                new_label = Label(
                    current,
                    [
                        current.resource[0] + cost_1[out_edge],
                        current.resource[1] + cost_2[out_edge],
                    ],
                    out_edge.target(),
                )
                # check if other labels exist for this vertex
                if out_edge.target() in vertex_dict:
                    # check if the new label is dominated
                    for vertex_label in vertex_dict[out_edge.target()]:
                        if vertex_label.dominate(new_label):
                            break
                    else:
                        # keep the new label as it is not dominated
                        vertex_dict[out_edge.target()].append(new_label)
                        heapq.heappush(labels, new_label)
                        # remove labels that the new label dominates from the heap
                        for vertex_label in vertex_dict[out_edge.target()]:
                            if new_label.dominate(vertex_label):
                                vertex_label.removed = True
                        # remove such labels from association with their vertex
                        vertex_dict[out_edge.target()][:] = [
                            vertex_label
                            for vertex_label in vertex_dict[out_edge.target()]
                            if not vertex_label.removed
                        ]
                else:
                    # no labels for this vertex yet, add the new label
                    vertex_dict[out_edge.target()] = [new_label]
                    heapq.heappush(labels, new_label)
    print(target)
    print(source)
    # begin backtracking
    routes = []
    route = []
    for label in vertex_dict[target]:
        route.append(target)
        v = target
        # keep track of our current label
        label_tracker = label
        while v != source:
            label_tracker = label_tracker.pred
            v = label_tracker.assoc
            route.append(v)
        route.reverse()
        routes.append(route)
        route = []
    print([[int(r) for r in route] for route in routes])
    return routes
