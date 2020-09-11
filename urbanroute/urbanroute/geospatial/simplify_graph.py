"""Functions that add vertices to the boolean filter to be ignored by graph algorithms"""
from haversine import haversine
from graph_tool.all import Graph


def remove_leaves(G: Graph, del_list):
    """remove leaves (in-degree 0 or out-degree 0) from graph"""
    for v in G.vertices():
        # remove leaf nodes
        if v.out_degree() == 0 or v.in_degree() == 0:
            del_list[v] = False


def remove_paths(G, del_list, pos, length, pollution):
    """remove vertices with in-degree 1 and out-degree 1"""
    new_edges = []
    for v in G.vertices():
        del_list[v] = True
        # remove leaf nodes
        if v.out_degree() == 0 or v.in_degree() == 0:
            del_list[v] = False
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

    # create a new edge bridging the removed vertex
    for e in new_edges:
        new = G.add_edge(e[0], e[1])
        length[new] = e[2]
        pollution[new] = e[3]
