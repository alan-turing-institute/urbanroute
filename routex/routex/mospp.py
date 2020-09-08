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


def dominatesList(resources, otherResource):
    return np.any(
        np.logical_and(
            (resources <= otherResource).all(axis=1),
            (resources < otherResource).any(axis=1),
        )
    )


def dominatesListNoEquality(resources, otherResource):
    return np.any((resources <= otherResource).all(axis=1))


def add_label(target_vertex, vertex_labels, labels, new_label):
    # check if other labels exist for this vertex
    if target_vertex in vertex_labels:
        # check if the new label is dominated
        # list of resources of all the labels of the vertex
        resource_list = np.single([label[0] for label in vertex_labels[target_vertex]])
        # check domination
        if not np.any(
            np.logical_and(
                (resource_list <= new_label[0]).all(axis=1),
                (resource_list < new_label[0]).any(axis=1),
            )
        ):
            # remove labels that this new label dominates from the vertex labels
            remove_list = (resource_list >= new_label[0]).all(axis=1)
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


def checkIfPredecessor(vertex, label):
    labeltracker = label
    count = 0
    while labeltracker[1] != None:
        count += 1
        if count > 2:
            break
        labeltracker = labeltracker[1]
        if vertex == labeltracker[2]:
            return True
    return False


def mospp(
    source: Vertex, target: Vertex, cost_1: EdgePropertyMap, cost_2: EdgePropertyMap
):
    """Run MOSPP on graph. Returns list of routes, each route being a list of vertices"""
    x_process = []
    y_process = []
    labels = [((0, 0), None, source, set({}))]
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
            for out_edge in current[2].out_edges():
                # we're not interested in visiting any predecessors
                if not checkIfPredecessor(out_edge.target(), current):
                    # create the new label with updated resource values
                    new_label = (
                        (
                            current[0][0] + cost_1[out_edge],
                            current[0][1] + cost_2[out_edge],
                        ),
                        current,
                        out_edge.target(),
                        set({})
                        # current[3].copy()
                    )
                    new_label[3].add(out_edge.target())
                    add_label(out_edge.target(), vertex_labels, labels, new_label)
                    """if out_edge.target() == target:
                        x_process.append(new_label[0][0])
                        y_process.append(new_label[0][1])"""
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
    # plt.scatter(
    #   [r[0][0] for r in vertex_labels[target]],
    #   [r[0][1] for r in vertex_labels[target]],
    # )

    """fig, ax = plt.subplots()
    xdata, ydata = [], []
    (ln,) = plt.plot([], [], "ro")
    print(x_process)
    print(y_process)

    def init():
        ax.set_xlim(25, 45)
        ax.set_ylim(25, 45)
        return (ln,)

    def update(frame):
        xdata.append(frame)
        ydata.append(np.sin(frame))
        ln.set_data(x_process[: int(frame)], y_process[: int(frame)])
        return (ln,)

    ani = FuncAnimation(
        fig,
        update,
        frames=np.linspace(0, 10000, 10000),
        init_func=init,
        blit=True,
        interval=200,
    )
    plt.show()
    print([r[0][1] / (r[0][0] + r[0][1]) for r in vertex_labels[target]])"""
    return routes
