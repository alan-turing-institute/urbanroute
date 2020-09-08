import numpy as np
import random
from graph_tool.all import lattice, graph_draw
from routex import mospp


G = lattice([20, 20])

c1 = G.new_edge_property("double")
c2 = G.new_edge_property("double")
for e in G.edges():
    c1[e] = 0.5 + random.random()
    c2[e] = 0.5 + random.random()
# graph_draw(G)
vertices = []
for v in G.vertices():
    vertices.append(v)
mospp(G.vertex(0), G.vertex(399), c1, c2)

