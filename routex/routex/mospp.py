"""Perform MOSPP on the graph"""
import heapq
import numpy as np
import math
from graph_tool.all import Vertex, EdgePropertyMap


def dominate(resource, other):
    return np.all(np.less_equal(resource, other)) and np.any(np.less(resource, other))


def stopping_condition(labels, vertex_labels, target, minimum_resource, rerun_stopping):
    """The stopping condition inspired by A*, runs only occasionally, see
    Speeding up Martin's algorithm for multiple objective shortest path problems,
    2012, Demeyer et al"""
    if rerun_stopping and target in vertex_labels:
        """if not np.any(
                        np.logical_and(
                            (resource_list < minimum_resource).any(axis=1),
                            (resource_list <= new_label[0]).all(axis=1),
                        )
                    )"""
        for label in vertex_labels[target]:
            if dominate(label[0], minimum_resource):
                return True
    return False


def add_label(target_vertex, vertex_labels, labels, new_label):
    # check if other labels exist for this vertex
    if target_vertex in vertex_labels:
        # check if the new label is dominated
        # list of resources of all the labels of the vertex
        resource_list = np.single([label[0] for label in vertex_labels[target_vertex]])
        # check domination
        if not np.any((resource_list < new_label[0]).all(axis=1)):
            # remove labels that this new label dominates from the vertex labels
            remove_list = (resource_list > new_label[0]).all(axis=1)
            vertex_labels[target_vertex] = [
                value
                for index, value in enumerate(vertex_labels[target_vertex])
                if not remove_list[index]
            ]
            # add the new label as it is not dominated
            vertex_labels[target_vertex].append(new_label)
            heapq.heappush(labels, new_label)
            return True
    else:
        # no labels for this vertex yet, add the new label
        vertex_labels[target_vertex] = [new_label]
        heapq.heappush(labels, new_label)
        return True
    return False


def mospp(
    source: Vertex, target: Vertex, cost_1: EdgePropertyMap, cost_2: EdgePropertyMap,
):
    """Run MOSPP on graph. Returns list of routes, each route being a list of vertices"""

    labels = [((0, 0), None, source)]
    skip = 1000
    # labels associated with each vertex
    vertex_labels = {source: [labels[0]]}
    rerun_stopping = False
    minimum_resource = [math.inf, math.inf]

    while labels and not stopping_condition(
        labels, vertex_labels, target, minimum_resource, rerun_stopping
    ):
        rerun_stopping = False
        # pick lexicographically smallest label if it isn't
        # already excluded
        current = heapq.heappop(labels)
        # we could be removing the element responsible for the current minimum
        skip -= 1
        if skip == 0:
            rerun_stopping = True
            resource_list = np.array([label[0] for label in labels])
            if np.size(resource_list) > 0:
                minimum_resource = np.min(resource_list, axis=0)
            else:
                minimum_resource[0] = math.inf
                minimum_resource[1] = math.inf
            skip = 1000
        # don't expand dominated labels
        if current[2] != target and current in vertex_labels.get(current[2], []):
            for out_edge in current[2].out_edges():
                # create the new label with updated resource values
                new_label = (
                    (
                        current[0][0] + cost_1[out_edge] + 0.001,
                        current[0][1] + cost_2[out_edge] + 0.001,
                    ),
                    current,
                    out_edge.target(),
                )
                add_label(out_edge.target(), vertex_labels, labels, new_label)

    # begin backtracking
    routes = []
    route = []
    for label in vertex_labels[target]:
        route.append(target)
        v = target
        # keep track of our current label
        label_tracker = label
        while v != source:
            label_tracker = label_tracker[1]
            v = label_tracker[2]
            route.append(v)
        route.reverse()
        routes.append(route)
        route = []
    return routes
