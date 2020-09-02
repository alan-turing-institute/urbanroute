"""Test case useful for benchmarking mospp performance"""
from graph_tool.all import load_graph
from routex import mospp

G = load_graph("../../tests/test_graphs/Trafalgar.gt")
pos = G.new_vertex_property("vector<double>")
float_length = G.new_edge_property("double")
float_x = G.new_vertex_property("double")
float_y = G.new_vertex_property("double")
G.edge_properties["float_length"] = float_length
pollution = G.new_edge_property("double")
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

source = 253
target = 3043
# lazy stop should give same result as stopping only when all labels are done
mospp(G.vertex(source), G.vertex(target), float_length, pollution)
