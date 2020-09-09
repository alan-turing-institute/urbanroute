"""Perform MOSPP on the graph"""
import heapq
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from graph_tool.all import Vertex, EdgePropertyMap


def stopping_condition(vertex_labels, target, minimum_resource):
    """The stopping condition inspired by A*, runs only occasionally, see
    Speeding up Martin's algorithm for multiple objective shortest path problems,
    2012, Demeyer et al"""
    if target in vertex_labels:
        for label in vertex_labels[target]:
            if np.all(np.less_equal(label[0], minimum_resource)) and np.any(
                np.less(label[0], minimum_resource)
            ):
                return True
    return False


def add_label(
    target_vertex,
    vertex_labels,
    labels,
    new_label,
    equality_dominates,
    domination_check_count,
):
    # check if other labels exist for this vertex
    if target_vertex in vertex_labels:
        # check if the new label is dominated
        # list of resources of all the labels of the vertex
        resource_list = np.single([label[0] for label in vertex_labels[target_vertex]])
        # check domination
        if equality_dominates:
            comparison = resource_list <= new_label[0]
            domination_check_count[0] += len(resource_list)
            if not np.any(comparison.all(axis=1)):
                # remove labels that this new label dominates from the vertex labels
                remove_list = (np.logical_not(comparison)).all(axis=1)
                domination_check_count[0] += len(resource_list)
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
            domination_check_count[0] += len(resource_list)
            if not np.any(
                np.logical_and(
                    (resource_list <= new_label[0]).all(axis=1),
                    (resource_list < new_label[0]).any(axis=1),
                )
            ):
                domination_check_count[0] += len(resource_list)
                # remove labels that this new label dominates from the vertex labels
                remove_list = np.logical_and(
                    (resource_list >= new_label[0]).all(axis=1),
                    (resource_list > new_label[0]).any(axis=1),
                )
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


def checkIfPredecessor(vertex, label, predecessors):
    label_tracker = label
    count = 0
    while label_tracker[1] is not None:
        count += 1
        if count > predecessors:
            break
        label_tracker = label_tracker[1]
        if vertex == label_tracker[2]:
            return True
    return False


def mospp(
    source: Vertex,
    target: Vertex,
    cost_1: EdgePropertyMap,
    cost_2: EdgePropertyMap,
    equality_dominates=False,
    predecessors=0,
):
    """Run MOSPP on graph. Returns list of routes, each route being a list of vertices"""
    labels_expanded_count = 0
    domination_check_count = [0]
    labels = [((0, 0), None, source)]
    # labels associated with each vertex
    vertex_labels = {source: [labels[0]]}
    skip = 1000
    while labels:
        # we could be removing the element responsible for the current minimum
        skip -= 1
        if skip == 0:
            skip = 1000
            resource_list = np.array([label[0] for label in labels])
            if np.size(resource_list) > 0:
                minimum_resource = np.min(resource_list, axis=0)
            else:
                minimum_resource[0] = math.inf
                minimum_resource[1] = math.inf
            if stopping_condition(vertex_labels, target, minimum_resource):
                break
        # pick lexicographically smallest label if it isn't
        # already excluded
        current = heapq.heappop(labels)
        # don't expand dominated labels, and don't go to previous vertex
        if current[2] != target and current in vertex_labels.get(current[2], []):
            labels_expanded_count += 1
            for out_edge in current[2].out_edges():
                # we're not interested in visiting any predecessors
                if not checkIfPredecessor(out_edge.target(), current, predecessors):
                    # create the new label with updated resource values
                    new_label = (
                        (
                            current[0][0] + cost_1[out_edge],
                            current[0][1] + cost_2[out_edge],
                        ),
                        current,
                        out_edge.target(),
                    )
                    add_label(
                        out_edge.target(),
                        vertex_labels,
                        labels,
                        new_label,
                        equality_dominates,
                        domination_check_count,
                    )
    print(labels_expanded_count, "labels expanded")
    print(domination_check_count, "domination checks")
    # begin backtracking
    routes = []
    route = []
    for label in vertex_labels[target]:
        route.append(target)
        # keep track of our current label
        label_tracker = label
        while label_tracker[2] != source:
            label_tracker = label_tracker[1]
            route.append(label_tracker[2])
        route.reverse()
        routes.append(route)
        route = []
    print("Number of routes:", len(routes))
    return routes
