"""Test case useful for benchmarking mospp performance"""
from graph_tool.all import load_graph
from routex import mospp, astar
from haversine import haversine
from urbanroute.geospatial import *

G = load_graph("../../tests/test_graphs/Trafalgar.gt")
pos = G.new_vertex_property("vector<double>")
float_length = G.new_edge_property("double")
float_x = G.new_vertex_property("double")
float_y = G.new_vertex_property("double")
G.edge_properties["float_length"] = float_length
pollution = G.new_edge_property("double")
scalarisation = G.new_edge_property("double")
mean = G.edge_properties["NO2_mean"]
length = G.edge_properties["length"]
x = G.vertex_properties["x"]
y = G.vertex_properties["y"]
number = G.new_vertex_property("string")
for v in G.get_vertices():
    pos[v] = [float(x[v]), float(y[v])]
    float_x[v] = float(x[v])
    float_y[v] = float(y[v])
    number[v] = str(G.vertex_index[v])
for e in G.edges():
    float_length[e] = float(length[e])
    pollution[e] = float(mean[e]) * float(length[e])
    weight = 0.99
    scalarisation[e] = weight * float_length[e] + (1 - weight) * pollution[e]


def distance_heuristic(v, target, pos):
    return 0


del_list = G.new_edge_property("bool")
source = 253
target = 3043
remove_leaves(G, del_list)
remove_self_edges(G)
remove_parallel(G, float_length, pollution)
remove_edges(G, float_length, pollution)
remove_paths(G, del_list, pos, length, pollution)
del_list[source] = True
del_list[target] = True
print(G.num_vertices(), G.num_edges())
G.set_vertex_filter(del_list)
print(G.num_vertices(), G.num_edges())
# lazy stop should give same result as stopping only when all labels are done
mospp(
    G.vertex(source),
    G.vertex(target),
    float_length,
    pollution,
    equality_dominates=True,
    predecessors=2,
)
"""vertices = [
    int(v) for v in (astar(G, source, target, scalarisation, distance_heuristic, pos))
]
vertices.reverse()
print(vertices)
distance = sum(
    [
        float_length[G.edge(vertices[i], vertices[i + 1])]
        for i in range(0, len(vertices) - 1)
    ]
)
print(distance)
pollution = sum(
    [
        pollution[G.edge(vertices[i], vertices[i + 1])]
        for i in range(0, len(vertices) - 1)
    ]
)
print(pollution)
print(pollution / (distance + pollution))
"""
