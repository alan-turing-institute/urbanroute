"""Functions that add vertices to the boolean filter to be ignored by graph algorithms"""
from haversine import haversine
from graph_tool.all import *
from routex import neighbour_distances, distances


def remove_leaves(G: Graph, del_list):
    """remove leaves (in-degree 0 or out-degree 0) from graph"""
    count = 0
    for v in G.vertices():
        # remove leaf nodes
        if v.out_degree() == 0 or v.in_degree() == 0:
            del_list[v] = False
            count += 0
    print("Removed", count, "leaves")


def remove_paths(G, del_list, pos, length, pollution):
    """remove vertices with in-degree 1 and out-degree 1"""
    new_edges = []
    count = 0
    for v in G.vertices():
        # remove nodes in paths so long as they are not more
        # than 50m away from either of their neighbours
        if v.out_degree() == 1 and v.in_degree() == 1:
            cut = True
            new_edge_length = 0
            new_edge_pollution = 0
            into = None
            outof = None
            for into in v.in_edges():
                if (
                    haversine(
                        (pos[v].a[0], pos[v].a[1]),
                        (pos[into.source()].a[0], pos[into.source()].a[1]),
                        unit="m",
                    )
                    > 50
                ):
                    cut = False
                new_edge_length = length[into]
                new_edge_pollution = pollution[into]

            for outof in v.out_edges():
                if (
                    haversine(
                        (pos[v].a[0], pos[v].a[1]),
                        (pos[outof.target()].a[0], pos[outof.target()].a[1]),
                        unit="m",
                    )
                    > 50
                ):
                    cut = False
                # calculate length of new edge
                new_edge_length = new_edge_length + length[outof]
                new_edge_pollution = new_edge_pollution + pollution[outof]

            if cut and (not into is None) and (not outof is None):
                e = (into.source(), outof.target(), new_edge_length, new_edge_pollution)
                new_edges.append(e)
                # remove vertex
                del_list[v] = False
                count += 1
    print("Removed", count, "vertices and the same number of edges")
    # create a new edge bridging the removed vertex
    for e in new_edges:
        new = G.add_edge(e[0], e[1])
        length[new] = e[2]
        pollution[new] = e[3]


def remove_self_edges(G: Graph):
    """Remove all self-edges from the graph"""
    edge_removal_list = []
    for v in G.vertices():
        for e in v.out_edges():
            if e.target() == e.source():
                edge_removal_list.append(e)
    print("Removed", len(edge_removal_list), "self-edges")
    for i in reversed(sorted(edge_removal_list)):
        G.remove_edge(i)


def remove_parallel(G: Graph, cost_1, cost_2):
    """Remove all dominated parallel-edges from the graph"""
    edge_removal_list = []
    for v in G.vertices():
        for u in v.out_neighbours():
            parallel_edges = G.edge(v, u, all_edges=True)
            for e in parallel_edges:
                for f in parallel_edges:
                    if (
                        e != f
                        and cost_1[e] >= cost_1[f]
                        and cost_2[e] >= cost_1[f]
                        and e not in edge_removal_list
                    ):
                        edge_removal_list.append(e)
    print("Removed", len(edge_removal_list), "parallel edges")
    for i in reversed(sorted(edge_removal_list)):
        G.remove_edge(i)


def remove_edges(G: Graph, cost_1, cost_2):
    edge_removal_list = []
    removals = 0
    for v in G.vertices():
        cost_1_distances = neighbour_distances(G, v, cost_1)
        cost_2_distances = neighbour_distances(G, v, cost_2)
        for e in v.out_edges():
            if (
                cost_1[e] > cost_1_distances[e.target()]
                and cost_2[e] > cost_2_distances[e.target()]
            ):
                edge_removal_list.append(e)

        # print("Removed", len(edge_removal_list), "edges")
        for e in reversed(sorted(edge_removal_list)):
            G.remove_edge(e)
        removals += len(edge_removal_list)
        edge_removal_list = []
    print("Removed", removals, "edges")


def remove_vertices(G: Graph, source, target, cost_1, cost_2, del_list):
    """Remove vertices with greater pollution than the least distance path or greater
    distance than the least pollution path"""
    cost_1_distances, cost_1_paths = distances(G, source, cost_1)
    cost_2_distances, cost_2_paths = distances(G, source, cost_2)
    cost_1_pollution = 0
    cost_2_distance = 0
    vertex_tracker = target
    vertex_tracker_previous = target
    while vertex_tracker != source:
        vertex_tracker_previous = int(vertex_tracker)
        vertex_tracker = int(cost_1_paths[vertex_tracker])
        cost_1_pollution += cost_2[G.edge(vertex_tracker, vertex_tracker_previous)]

    vertex_tracker = target
    while vertex_tracker != source:
        vertex_tracker_previous = int(vertex_tracker)
        vertex_tracker = int(cost_2_paths[vertex_tracker])
        cost_2_distance += cost_1[G.edge(vertex_tracker, vertex_tracker_previous)]

    count = 0
    for v in G.vertices():
        if (
            cost_1_distances[v] > cost_2_distance
            or cost_2_distances[v] > cost_1_pollution
        ):
            count += 1
            del_list[v] = False

    del_list[target] = True

    G.set_reversed(True)
    cost_1_distances, cost_1_paths = distances(G, target, cost_1)
    cost_2_distances, cost_2_paths = distances(G, target, cost_2)
    cost_1_pollution = 0
    cost_2_distance = 0
    vertex_tracker = source
    vertex_tracker_previous = source
    while vertex_tracker != target:
        vertex_tracker_previous = int(vertex_tracker)
        vertex_tracker = int(cost_1_paths[vertex_tracker])
        cost_1_pollution += cost_2[G.edge(vertex_tracker, vertex_tracker_previous)]

    vertex_tracker = source
    while vertex_tracker != target:
        vertex_tracker_previous = int(vertex_tracker)
        vertex_tracker = int(cost_2_paths[vertex_tracker])
        cost_2_distance += cost_1[G.edge(vertex_tracker, vertex_tracker_previous)]

    for v in G.vertices():
        if (
            cost_1_distances[v] > cost_2_distance
            or cost_2_distances[v] > cost_1_pollution
        ):
            if del_list[v]:
                count += 1
            del_list[v] = False
    G.set_reversed(False)

    print("Removed", count, "vertices")
    return (cost_1_pollution, cost_2_distance, cost_2_distances, cost_1_distances)
