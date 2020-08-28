"""The biobjective label setting algorithm for MOSPP, see
Speeding up Martin's algorithm for multiple objective shortest path problems, 2012, Demeyer et al"""
from .mospp import *

"""Perform MOSPP on the graph"""
import heapq
import numpy as np
import math
from graph_tool.all import Vertex, EdgePropertyMap

"""
class BidirectionalPath:
    def __init__(
        self,
        forwardLabel: Label,
        backwardLabel: Label,
        source: Vertex,
        destination: Vertex,
    ):
        self.forwardLabel = forwardLabel
        self.backwardLabel = backwardLabel
        self.resource = np.array(forwardLabel.resource) + np.array(
            backwardLabel.resource
        )
        labelTracker = backwardLabel
        v = backwardLabel.assoc
        backpath = [v]
        while v != destination:
            labelTracker = labelTracker.pred
            v = labelTracker.assoc
            backpath.append(v)

        labelTracker = forwardLabel
        v = forwardLabel.assoc
        forwardpath = []
        while v != source:
            labelTracker = labelTracker.pred
            v = labelTracker.assoc
            forwardpath.append(v)
        forwardpath.reverse()
        self.path = forwardpath + backpath


def biobjective_lazy_a_star_stopping(
    minimum_resource_forward, minimum_resource_backwards, results, rerun_stopping
):
    if rerun_stopping:
        for label in results:
            if dominate(
                label.resource,
                np.array(minimum_resource_forward)
                + np.array(minimum_resource_backwards),
            ):
                return True
    return False


def biobjective_mospp(
    source: Vertex,
    target: Vertex,
    cost_1: EdgePropertyMap,
    cost_2: EdgePropertyMap,
    stopping_condition=biobjective_lazy_a_star_stopping,
):"""
"""Run MOSPP on graph. Returns list of routes, each route being a list of vertices"""
"""labelsForward = [Label(None, np.array([0, 0]), source)]
labelsBackward = [Label(None, np.array([0, 0]), target)]
direction = "forward"
# labels associated with each vertex
vertex_dict_forward = {source: [labelsForward[0]]}
vertex_dict_backwards = {target: [labelsBackward[0]]}
rerun_stopping = False
minimum_resource_forward = [0, 0]
minimum_resource_backwards = [0, 0]
results = []
while not stopping_condition(
    minimum_resource_forward, minimum_resource_backwards, results, rerun_stopping
):
    rerun_stopping = False
    # pick lexicographically smallest label if it isn't
    # already excluded
    current = None
    if direction == "forward":
        current = heapq.heappop(labelsForward)
        print(current, direction)
        if (
            current.resource[0] == minimum_resource_forward[0]
            or current.resource[1] == minimum_resource_forward[1]
        ):
            rerun_stopping = True
            minimum_resource_forward[0] = math.inf
            minimum_resource_forward[1] = math.inf
            for x in labelsForward:
                if x.resource[0] < minimum_resource_forward[0]:
                    minimum_resource_forward[0] = x.resource[0]
                if x.resource[1] < minimum_resource_forward[1]:
                    minimum_resource_forward[1] = x.resource[1]
    else:
        current = heapq.heappop(labelsBackward)
        print(current, direction)
        if (
            current.resource[0] == minimum_resource_backwards[0]
            or current.resource[1] == minimum_resource_backwards[1]
        ):
            rerun_stopping = True
            minimum_resource_backwards[0] = math.inf
            minimum_resource_backwards[1] = math.inf
            for x in labelsBackward:
                if x.resource[0] < minimum_resource_backwards[0]:
                    minimum_resource_backwards[0] = x.resource[0]
                if x.resource[1] < minimum_resource_backwards[1]:
                    minimum_resource_backwards[1] = x.resource[1]
    # we could be removing the element responsible for the current minimum

    if not current.removed:
        if direction == "forward":
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
                if out_edge.target() in vertex_dict_forward:
                    # check if the new label is dominated
                    for vertex_label in vertex_dict_forward[out_edge.target()]:
                        if vertex_label.dominate(new_label):
                            break
                    else:
                        # keep the new label as it is not dominated
                        vertex_dict_forward[out_edge.target()].append(new_label)
                        heapq.heappush(labelsForward, new_label)
                        if new_label.resource[0] < minimum_resource_forward[0]:
                            minimum_resource_forward[0] = new_label.resource[0]
                        if new_label.resource[1] < minimum_resource_forward[1]:
                            minimum_resource_forward[1] = new_label.resource[1]
                        # remove labels that the new label dominates from the heap
                        for vertex_label in vertex_dict_forward[out_edge.target()]:
                            if new_label.dominate(vertex_label):
                                vertex_label.removed = True
                        # remove such labels from association with their vertex
                        vertex_dict_forward[out_edge.target()][:] = [
                            vertex_label
                            for vertex_label in vertex_dict_forward[
                                out_edge.target()
                            ]
                            if not vertex_label.removed
                        ]
                        if out_edge.target() in vertex_dict_backwards:
                            for label in vertex_dict_backwards[out_edge.target()]:
                                results.append(
                                    BidirectionalPath(
                                        new_label, label, source, target
                                    )
                                )
                else:
                    # no labels for this vertex yet, add the new label
                    vertex_dict_forward[out_edge.target()] = [new_label]
                    heapq.heappush(labelsForward, new_label)
                    if new_label.resource[0] < minimum_resource_forward[0]:
                        minimum_resource_forward[0] = new_label.resource[0]
                        rerun_stopping = True
                    if new_label.resource[1] < minimum_resource_forward[1]:
                        minimum_resource_forward[1] = new_label.resource[1]
                        rerun_stopping = True
                    if out_edge.target() in vertex_dict_backwards:
                        for label in vertex_dict_backwards[out_edge.target()]:
                            results.append(
                                BidirectionalPath(new_label, label, source, target)
                            )
        elif direction == "backward":
            for in_edge in current.assoc.in_edges():
                # create the new label with updated resource values
                new_label = Label(
                    current,
                    [
                        current.resource[0] + cost_1[in_edge],
                        current.resource[1] + cost_2[in_edge],
                    ],
                    in_edge.source(),
                )
                # check if other labels exist for this vertex
                if in_edge.source() in vertex_dict_backwards:
                    # check if the new label is dominated
                    for vertex_label in vertex_dict_backwards[in_edge.source()]:
                        if vertex_label.dominate(new_label):
                            break
                    else:
                        # keep the new label as it is not dominated
                        vertex_dict_backwards[in_edge.source()].append(new_label)
                        heapq.heappush(labelsBackward, new_label)
                        if new_label.resource[0] < minimum_resource_backwards[0]:
                            minimum_resource_backwards[0] = new_label.resource[0]
                        if new_label.resource[1] < minimum_resource_backwards[1]:
                            minimum_resource_backwards[1] = new_label.resource[1]
                        # remove labels that the new label dominates from the heap
                        for vertex_label in vertex_dict_backwards[in_edge.source()]:
                            if new_label.dominate(vertex_label):
                                vertex_label.removed = True
                        # remove such labels from association with their vertex
                        vertex_dict_backwards[in_edge.source()][:] = [
                            vertex_label
                            for vertex_label in vertex_dict_backwards[
                                in_edge.source()
                            ]
                            if not vertex_label.removed
                        ]
                        if out_edge.target() in vertex_dict_forward:
                            if in_edge.source() in vertex_dict_forward:
                                for label in vertex_dict_forward[in_edge.source()]:
                                    results.append(
                                        BidirectionalPath(
                                            label, new_label, source, target
                                        )
                                    )
                else:
                    # no labels for this vertex yet, add the new label
                    vertex_dict_backwards[in_edge.source()] = [new_label]
                    heapq.heappush(labelsBackward, new_label)
                    if new_label.resource[0] < minimum_resource_backwards[0]:
                        minimum_resource_backwards[0] = new_label.resource[0]
                        rerun_stopping = True
                    if new_label.resource[1] < minimum_resource_backwards[1]:
                        minimum_resource_backwards[1] = new_label.resource[1]
                        rerun_stopping = True
                    if in_edge.source() in vertex_dict_forward:
                        for label in vertex_dict_forward[in_edge.source()]:
                            results.append(
                                BidirectionalPath(label, new_label, source, target)
                            )
        if direction == "forward":
            direction = "backward"
        else:
            direction = "forward"
# begin backtracking
routes = []
for label in results:
    routes.append(label.path)
print(routes)
return routes
"""
