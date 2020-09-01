"""The biobjective label setting algorithm for MOSPP, see
Speeding up Martin's algorithm for multiple objective shortest path problems, 2012, Demeyer et al"""
from .mospp import *

"""Perform MOSPP on the graph"""
import heapq
import numpy as np
import math
from graph_tool.all import Vertex, EdgePropertyMap
from routex import *


def bidirectional_mospp(
    source: Vertex, target: Vertex, cost_1: EdgePropertyMap, cost_2: EdgePropertyMap,
):
    """Run MOSPP on graph. Returns list of routes, each route being a list of vertices"""

    labels = [((0, 0), None, source)]
    skip = 1000
    # labels associated with each vertex
    vertex_labels = {source: [labels[0]]}
    rerun_stopping = False
    minimum_resource = [0.0, 0.0]

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
            minimum_resource[0] = math.inf
            minimum_resource[1] = math.inf
            resource_list = np.array([label[0] for label in labels])
            if np.size(resource_list) > 0:
                minimum_resource = np.min(resource_list, axis=0)
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
                add_label(out_edge, vertex_labels, labels, new_label)

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
