"""The biobjective label setting algorithm for MOSPP, see
Speeding up Martin's algorithm for multiple objective shortest path problems, 2012, Demeyer et al"""
from .mospp import *

"""Perform MOSPP on the graph"""
import heapq
import numpy as np
import math
from graph_tool.all import Vertex, EdgePropertyMap
from routex import add_label


def stopping_condition_bidirectional(
    labels, vertex_labels, target, minimum_resource, rerun_stopping
):
    pass


def bidirectional_mospp(
    source: Vertex, target: Vertex, cost_1: EdgePropertyMap, cost_2: EdgePropertyMap,
):
    """Run MOSPP on graph. Returns list of routes, each route being a list of vertices"""

    labels_forwards = [((0, 0), None, source)]
    labels_backwards = [((0, 0), None, target)]
    skip = 1000
    # labels associated with each vertex
    vertex_labels_forwards = {source: [labels_forwards[0]]}
    vertex_labels_backwards = {target: [labels_backwards[0]]}
    rerun_stopping = False
    direction = "forwards"
    minimum_resource_forwards = [math.inf, math.inf]
    minimum_resource_backwards = [math.inf, math.inf]
    resulting_paths = []
    while (
        labels_forwards and labels_backwards
    ) and not stopping_condition_bidirectional(
        labels_forwards,
        labels_backwards,
        target,
        minimum_resource_forwards,
        rerun_stopping,
    ):
        # we could be removing the element responsible for the current minimum
        skip -= 1
        if skip == 0:
            rerun_stopping = True
            skip = 1000
        else:
            rerun_stopping = False
        if direction == "forwards":
            # pick lexicographically smallest label if it isn't
            # already excluded
            current = heapq.heappop(labels_forwards)
            # don't expand dominated labels
            if current[2] != target and current in vertex_labels_forwards.get(
                current[2], []
            ):
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
                    add_label(
                        out_edge.target(),
                        vertex_labels_forwards,
                        labels_forwards,
                        new_label,
                    )
            direction = "backwards"
        if direction == "backwards":
            # pick lexicographically smallest label if it isn't
            # already excluded
            current = heapq.heappop(labels_backwards)
            # don't expand dominated labels
            if current[2] != source and current in vertex_labels_backwards.get(
                current[2], []
            ):
                for in_edge in current[2].in_edges():
                    # create the new label with updated resource values
                    new_label = (
                        (
                            current[0][0] + cost_1[in_edge] + 0.001,
                            current[0][1] + cost_2[in_edge] + 0.001,
                        ),
                        current,
                        in_edge.source(),
                    )
                    add_label(
                        in_edge.source(),
                        vertex_labels_backwards,
                        labels_backwards,
                        new_label,
                    )
            direction = "forwards"
