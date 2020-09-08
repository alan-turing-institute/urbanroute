SETUP="from graph_tool.all import load_graph
from routex import mospp, astar
from haversine import haversine

G = load_graph('../../tests/test_graphs/Trafalgar.gt')
pos = G.new_vertex_property('vector<double>')
float_length = G.new_edge_property('double')
float_x = G.new_vertex_property('double')
float_y = G.new_vertex_property('double')
G.edge_properties['float_length'] = float_length
pollution = G.new_edge_property('double')
scalarisation = G.new_edge_property('double')
mean = G.edge_properties['NO2_mean']
length = G.edge_properties['length']
x = G.vertex_properties['x']
y = G.vertex_properties['y']
number = G.new_vertex_property('string')
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


source = 253
target = 3043"
#Path compression
#Removing leaves
#Removing self-edges
#Removing dominated parallel edges
#Removing edges for which there are better paths
#Elliptical node removal
#Node removal with Dijkstra's/A*

#Basic martins (uses lexicographic order)
python3 -m timeit -n 5 -s "$SETUP" "mospp(G.vertex(source), G.vertex(target), float_length, pollution)"

#Check label equality as a domination
python3 -m timeit -n 5 -s "$SETUP" "mospp(G.vertex(source), G.vertex(target), float_length, pollution, equality_dominates=True)"

#Don't visit path predecessors, looking at last 2 predecessors
python3 -m timeit -n 5 -s "$SETUP" "mospp(G.vertex(source), G.vertex(target), float_length, pollution, predecessors=2)"

#Full stopping condition (removing labels based on Pareto dominance by target)
#Minimum stopping condition always
#Minimum stopping condition infrequently
#Bidirectional search


