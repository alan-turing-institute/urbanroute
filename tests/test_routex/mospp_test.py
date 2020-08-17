import pytest
from graph_tool.all import load_graph
from routex import mospp


def test_mospp_large():
    G = load_graph("../../graphs/Trafalgar.gt")
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

    source = 69
    target = 570
    vcolor[source] = "blue"
    vcolor[target] = "blue"
    assert [
        [G.vertex_index[r] for r in route]
        for route in mospp(G.vertex(source), G.vertex(target), float_length, pollution)
    ] == [
        [
            570,
            555,
            2066,
            1686,
            826,
            1895,
            1850,
            2488,
            2723,
            2649,
            2651,
            2654,
            1286,
            2599,
            2569,
            851,
            2140,
            503,
            1987,
            1462,
            1244,
            652,
            263,
            1140,
            740,
            449,
            448,
            1338,
            2992,
            2000,
            1661,
            1901,
            1353,
            457,
            143,
            710,
            2967,
            3009,
            1544,
            160,
            2922,
            2283,
            669,
            676,
            2032,
            678,
            1259,
            2813,
            2816,
            318,
            320,
            319,
            69,
        ],
        [
            568,
            571,
            1520,
            566,
            2658,
            2661,
            2662,
            548,
            550,
            824,
            545,
            743,
            2542,
            2537,
            2514,
            2747,
            1073,
            185,
            2706,
            2826,
            2641,
            2702,
            2689,
            224,
            990,
            1326,
            2710,
            1171,
            1325,
            471,
            993,
            1381,
            2708,
            1421,
            2712,
            1483,
            1484,
            464,
            368,
            1815,
            1735,
            401,
            647,
            1733,
            2157,
            1053,
            3018,
            899,
            1803,
            375,
            179,
            180,
            173,
            319,
            69,
        ],
    ]

