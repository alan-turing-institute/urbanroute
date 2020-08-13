"""Perform A* on the graph"""
import heapq
import numpy as np
from graph_tool.all import Graph, Vertex, EdgePropertyMap


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


g = Graph()
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


def mospp(
    source: Vertex, target: Vertex, cost_1: EdgePropertyMap, cost_2: EdgePropertyMap
):
    labels = [Label(None, np.array([0, 0]), source)]
    vertex_dict = {}
    while len(labels) != 0:
        current = heapq.heappop(labels)
        for out_edge in current.assoc.out_edges():
            new_label = Label(
                current.assoc,
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
                        pass
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
    for label in vertex_dict[target]:
        print(label.resource)


mospp(v1, v4, cost_1, cost_2)
