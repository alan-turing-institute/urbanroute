"""Perform MOSPP on the graph"""
import heapq
import numpy as np
import math
from graph_tool.all import Vertex, EdgePropertyMap


def dominate(resource, other):
    return np.all(np.less_equal(resource, other)) and np.any(np.less(resource, other))


class Label:
    """The label class, contains the label predecessor of the label,
    resource costs, and the associated vertex"""

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
        return self.resource[0] > other.resource[0]

    def dominate(self, other):
        """Returns true iff this label dominates the other provided label"""
        return dominate(self.resource, other.resource)

    def __str__(self):
        return str((str(self.resource), str(int(self.assoc))))


def all_labels_stopping(labels, vertex_dict, target, minimum_resource, rerun_stopping):
    """Stop only after all labels have been examined"""
    return len(labels) == 0


def strict_a_star_stopping(labels):
    """Stopping condition inspired by A*, runs for every label removed, does full
    dominance checking with the destination labels"""
    pass


def lazy_a_star_stopping(labels, vertex_dict, target, minimum_resource, rerun_stopping):
    """The stopping condition inspired by A*, runs only occasionally, see
    Speeding up Martin's algorithm for multiple objective shortest path problems,
    2012, Demeyer et al"""
    if rerun_stopping and target in vertex_dict:
        for label in vertex_dict[target]:
            if dominate(label.resource, minimum_resource):
                return True
    return False


def mospp(
    source: Vertex,
    target: Vertex,
    cost_1: EdgePropertyMap,
    cost_2: EdgePropertyMap,
    stopping_condition=lazy_a_star_stopping,
):
    """Run MOSPP on graph. Returns list of routes, each route being a list of vertices"""
    labels = [Label(None, np.single([0, 0]), source)]
    # labels associated with each vertex
    vertex_dict = {}
    rerun_stopping = False
    minimum_resource = np.array([0.0, 0.0])

    while not stopping_condition(
        labels, vertex_dict, target, minimum_resource, rerun_stopping
    ):
        rerun_stopping = False
        # pick lexicographically smallest label if it isn't
        # already excluded
        current = heapq.heappop(labels)
        # we could be removing the element responsible for the current minimum
        if np.isclose(current.resource[0], minimum_resource[0], 0.5) or np.isclose(
            current.resource[1], minimum_resource[1], 0.5
        ):
            rerun_stopping = True
            minimum_resource[0] = math.inf
            minimum_resource[1] = math.inf
            resource_list = np.array([label.resource for label in labels])
            if np.size(resource_list) > 0:
                minimum_resource = np.min(resource_list, axis=0)
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
                    resource_list = np.single(
                        [label.resource for label in vertex_dict[out_edge.target()]]
                    )
                    if not np.any(
                        np.logical_and(
                            (resource_list < new_label.resource).any(axis=1),
                            (resource_list <= new_label.resource).all(axis=1),
                        )
                    ):
                        # keep the new label as it is not dominated
                        vertex_dict[out_edge.target()].append(new_label)
                        heapq.heappush(labels, new_label)
                        if new_label.resource[0] < minimum_resource[0]:
                            minimum_resource[0] = new_label.resource[0]
                        if new_label.resource[1] < minimum_resource[1]:
                            minimum_resource[1] = new_label.resource[1]
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
                    if new_label.resource[0] < minimum_resource[0]:
                        minimum_resource[0] = new_label.resource[0]
                    if new_label.resource[1] < minimum_resource[1]:
                        minimum_resource[1] = new_label.resource[1]
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
    return routes
