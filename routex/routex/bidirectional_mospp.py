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


def construct_path(forwards_label, backwards_label, source, target):
    forward_section = []
    label_tracker = forwards_label
    v = label_tracker[2]
    while v != source:
        forward_section.append(v)
        label_tracker = label_tracker[1]
        v = label_tracker[2]
    forward_section.append(source)
    backward_section = []
    label_tracker = backwards_label
    v = label_tracker[2]
    while v != target:
        backward_section.append(v)
        label_tracker = label_tracker[1]
        v = label_tracker[2]
    backward_section.append(target)
    forward_section.reverse()
    return forward_section + backward_section


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
    resulting_paths = {}
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
            if current[
                2
            ] not in resulting_paths and current in vertex_labels_forwards.get(
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
                    added = add_label(
                        out_edge.target(),
                        vertex_labels_forwards,
                        labels_forwards,
                        new_label,
                    )
                    if added and out_edge.target() in vertex_labels_backwards:
                        resulting_paths[out_edge.target()] = []
                        for label in vertex_labels_backwards[out_edge.target()]:
                            resulting_paths[out_edge.target()].append(
                                construct_path(new_label, label, source, target,)
                            )
            direction = "backwards"
        if direction == "backwards":
            # pick lexicographically smallest label if it isn't
            # already excluded
            current = heapq.heappop(labels_backwards)
            # don't expand dominated labels
            if current[
                2
            ] not in resulting_paths and current in vertex_labels_backwards.get(
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
                    added = add_label(
                        in_edge.source(),
                        vertex_labels_backwards,
                        labels_backwards,
                        new_label,
                    )
                    if added and in_edge.source() in vertex_labels_forwards:
                        resulting_paths[in_edge.source()] = []
                        for label in vertex_labels_forwards[in_edge.source()]:
                            resulting_paths[in_edge.source()].append(
                                construct_path(label, new_label, source, target,)
                            )
            direction = "forwards"
    routes = []
    route = []
    for _, value in resulting_paths.items():
        for x in value:
            route = []
            for y in x:
                route.append(int(y))
            routes.append(route)
    return routes
