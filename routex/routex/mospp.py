"""Perform A* on the graph"""
import heapq
import numpy as np
from graph_tool.all import (
    Graph,
    Vertex,
    EdgePropertyMap,
    load_graph,
    graph_draw,
    graphviz_draw,
)


class Label:
    """The label class, contains predecessor of label, resource costs, and the associated vertex"""

    def __init__(self, pred, resource: np.ndarray, assoc: Vertex):
        self.pred = pred
        self.resource = resource
        self.assoc = assoc

    def __gt__(self, other):
        return self.resource > other.resource

    def dominate(self, other):
        return np.all(np.less_equal(self.resource, other.resource)) and np.any(
            np.less(self.resource, other.resource)
        )


G = load_graph("Trafalgar.gt")
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


"""g = Graph()
v1 = g.add_vertex()
v2 = g.add_vertex()
v3 = g.add_vertex()
v4 = g.add_vertex()

e1 = g.add_edge(v1, v2)
e2 = g.add_edge(v1, v3)
e3 = g.add_edge(v2, v4)
e4 = g.add_edge(v3, v4)
e5 = g.add_edge(v1, v4)
cost_1 = g.new_edge_property("int")
cost_1[e1] = 1
cost_1[e2] = 0
cost_1[e3] = 1
cost_1[e4] = 0
cost_1[e5] = 1

cost_2 = g.new_edge_property("int")
cost_2[e1] = 0
cost_2[e2] = 1
cost_2[e3] = 0
cost_2[e4] = 1
cost_2[e5] = 1
"""


def mospp(
    source: Vertex, target: Vertex, cost_1: EdgePropertyMap, cost_2: EdgePropertyMap
):
    labels = [Label(None, np.array([0, 0]), source)]
    vertex_dict = {}
    while len(labels) != 0:
        current = heapq.heappop(labels)
        for out_edge in current.assoc.out_edges():
            new_label = Label(
                current,
                [
                    current.resource[0] + cost_1[out_edge],
                    current.resource[1] + cost_2[out_edge],
                ],
                out_edge.target(),
            )
            if out_edge.target() in vertex_dict:
                discard = False
                for vertex_label in vertex_dict[out_edge.target()]:
                    if vertex_label.dominate(new_label):
                        print("dominates")
                        print(vertex_label.resource)
                        print(new_label.resource)
                        print("end")
                        discard = True
                for vertex_label in vertex_dict[out_edge.target()]:
                    if new_label.dominate(vertex_label):
                        print("dominates")
                        print(new_label.resource)
                        print(vertex_label.resource)
                        print("end")
                        vertex_dict[out_edge.target()].remove(vertex_label)

                if not discard:
                    vertex_dict[out_edge.target()].append(new_label)

            else:
                vertex_dict[out_edge.target()] = [new_label]
                heapq.heappush(labels, new_label)
    for key in vertex_dict:
        print(key, len(vertex_dict[key]))
    color = "green"
    for label in vertex_dict[target]:
        print(label.resource)
        v = target
        label_tracker = label
        while v != source:
            label_tracker = label_tracker.pred
            v = label_tracker.assoc
            if v != source and v != target:
                vcolor[v] = color
        color = "purple"


source = 69
target = 570
vcolor[source] = "blue"
vcolor[target] = "blue"
# mospp(v1, v4, cost_1, cost_2)
mospp(G.vertex(source), G.vertex(target), float_length, pollution)
graph_draw(G, pos, vertex_text=number, vertex_fill_color=vcolor)

