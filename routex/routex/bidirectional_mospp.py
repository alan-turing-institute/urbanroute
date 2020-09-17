import heapq
import math
from graph_tool.all import Vertex, EdgePropertyMap
from .mospp import add_label

"""The biobjective label setting algorithm for MOSPP, see
Speeding up Martin's algorithm for multiple objective shortest path problems, 2012, Demeyer et al"""
"""Perform MOSPP on the graph"""


def stopping_condition_bidirectional(
    labels, vertex_labels, target, minimum_resource, rerun_stopping
):
    pass


def construct_path(forwards_label, backwards_label, source, target):
    # create the forwards path
    forward_section = []
    label_tracker = forwards_label
    v = label_tracker[2]
    while v != source:
        forward_section.append(int(v))
        label_tracker = label_tracker[1]
        v = label_tracker[2]
    forward_section.append(int(source))
    # need to reverse forwards path as traversed backwards
    forward_section.reverse()
    # create the backwards path
    backward_section = []
    label_tracker = backwards_label
    v = label_tracker[2]
    while v != target:
        backward_section.append(int(v))
        label_tracker = label_tracker[1]
        v = label_tracker[2]
    backward_section.append(int(target))
    return forward_section + backward_section


def test_pareto_optimal_bidirectional(label_set):
    for a in label_set:
        for b in label_set:
            if a != b and a[3] and b[3]:
                if a[0][0] <= b[0][0] and a[0][1] <= b[0][1]:
                    print("Counterexample", a[0], b[0])
                    return False
    return True


def bidirectional_mospp(
    source: Vertex,
    target: Vertex,
    cost_1: EdgePropertyMap,
    cost_2: EdgePropertyMap,
    equality_dominates=False,
    predecessors=0,
    skip=math.inf,
    cost_1_bound=math.inf,
    cost_2_bound=math.inf,
    cost_1_list=None,
    cost_2_list=None,
):
    """Run MOSPP on graph. Returns list of routes, each route being a list of vertices"""

    labels_forwards = [((0, 0), None, source)]
    labels_backwards = [((0, 0), None, target)]
    skip = 1000
    labels_expanded_count = 0
    domination_check_count = [0]
    # labels associated with each vertex
    vertex_labels_forwards = {source: [labels_forwards[0]]}
    vertex_labels_backwards = {target: [labels_backwards[0]]}
    rerun_stopping = False
    direction = "forwards"
    minimum_resource_forwards = [math.inf, math.inf]
    minimum_resource_backwards = [math.inf, math.inf]
    in_resulting_paths = {}
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
            # don't expand dominated labels or labels in frontier nodes
            if current[
                2
            ] not in in_resulting_paths and current in vertex_labels_forwards.get(
                current[2], []
            ):
                labels_expanded_count += 1
                for out_edge in current[2].out_edges():
                    # create the new label with updated resource values
                    new_label = (
                        (
                            current[0][0] + cost_1[out_edge],
                            current[0][1] + cost_2[out_edge],
                        ),
                        current,
                        out_edge.target(),
                    )
                    added = add_label(
                        out_edge.target(),
                        vertex_labels_forwards,
                        labels_forwards,
                        new_label,
                        equality_dominates,
                        domination_check_count,
                    )
                    # mark this node as a frontier node
                    if added and out_edge.target() in vertex_labels_backwards:
                        in_resulting_paths[out_edge.target()] = True
            direction = "backwards"
        if direction == "backwards":
            # pick lexicographically smallest label if it isn't
            # already excluded
            current = heapq.heappop(labels_backwards)
            # don't expand dominated labels or labels in frontier nodes
            if current[
                2
            ] not in in_resulting_paths and current in vertex_labels_backwards.get(
                current[2], []
            ):
                labels_expanded_count += 1
                for in_edge in current[2].in_edges():
                    # create the new label with updated resource values
                    new_label = (
                        (
                            current[0][0] + cost_1[in_edge],
                            current[0][1] + cost_2[in_edge],
                        ),
                        current,
                        in_edge.source(),
                    )
                    added = add_label(
                        in_edge.source(),
                        vertex_labels_backwards,
                        labels_backwards,
                        new_label,
                        equality_dominates,
                        domination_check_count,
                    )
                    # mark this node as a frontier node
                    if added and in_edge.source() in vertex_labels_forwards:
                        in_resulting_paths[in_edge.source()] = True
            direction = "forwards"

    print(labels_expanded_count, "labels expanded")
    print(domination_check_count, "domination checks")
    # performing backtracking
    solution_set = []
    routes = []

    def solution_dominates(a, b):
        return a[3] and b[3] and a[0][0] <= b[0][0] and a[0][1] <= b[0][1]

    # reconstruct path from meeting frontier of both searches
    for key, _ in in_resulting_paths.items():
        for forward_label in vertex_labels_forwards[key]:
            for backward_label in vertex_labels_backwards[key]:
                new_solution = [
                    (
                        forward_label[0][0] + backward_label[0][0],
                        forward_label[0][1] + backward_label[0][1],
                    ),
                    forward_label,
                    backward_label,
                    True,
                ]
                for solution in solution_set:
                    if solution_dominates(solution, new_solution):
                        break
                else:
                    for solution in solution_set:
                        if solution_dominates(new_solution, solution):
                            solution[3] = False
                    solution_set.append(new_solution)
    print(
        "Are all the solutions Pareto optimal?",
        test_pareto_optimal_bidirectional(solution_set),
    )
    solution_labels = []
    for solution in solution_set:
        # perform reconstruction
        if solution[3]:
            routes.append(construct_path(solution[1], solution[2], source, target))
            solution_labels.append(solution[0])
    solution_labels.sort()
    for s in solution_labels:
        print(s)
    print("Number of routes:", len(routes))
    return routes
