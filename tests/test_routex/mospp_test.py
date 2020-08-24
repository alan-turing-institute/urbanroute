import pytest
import json
from graph_tool.all import load_graph, Graph
from routex import mospp

with open("./tests/test_routex/large_solution.json", "r") as read_file:
    data = json.load(read_file)


def test_mospp_large():
    G = load_graph("./tests/test_graphs/Trafalgar.gt")
    G.list_properties()
    vcolor = G.new_vertex_property("string")
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
        vcolor[v] = "red"
        pos[v] = [float(x[v]), float(y[v])]
        float_x[v] = float(x[v])
        float_y[v] = float(y[v])
        number[v] = str(G.vertex_index[v])
    for e in G.edges():
        float_length[e] = float(length[e])
        pollution[e] = float(mean[e]) * float(length[e])

    source = 253
    target = 3043
    vcolor[source] = "blue"
    vcolor[target] = "blue"

    solution = []
    for route in data["solution"]:
        solution.append(list(reversed(route)))

    assert [
        [G.vertex_index[r] for r in route]
        for route in mospp(G.vertex(source), G.vertex(target), float_length, pollution)
    ] == solution


def test_mospp_small():
    G = Graph()
    G.add_vertex(1)
    G.add_vertex(2)
    G.add_vertex(3)
    G.add_vertex(4)
    c1 = G.new_edge_property("int")
    c2 = G.new_edge_property("int")
    e1 = G.add_edge(1, 3)
    e2 = G.add_edge(3, 4)
    e3 = G.add_edge(1, 2)

