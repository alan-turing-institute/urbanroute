SETUP="from graph_tool.all import load_graph, graphviz_draw
from routex import mospp, astar
import numpy as np
from haversine import haversine
from urbanroute.geospatial import (
    ellipse_bounding_box,
    coord_match,
    remove_leaves,
    remove_paths,
    remove_self_edges,remove_parallel,remove_edges
)

G = load_graph('../../tests/test_graphs/Trafalgar.gt')
print(G.num_vertices(), 'nodes and', G.num_edges(), 'edges in the graph.')
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


inside = G.new_vertex_property('bool')
del_list = G.new_vertex_property('bool')
for v in G.vertices():
    del_list[v] = True

# set up numpy array of vertices with just the position
vertices = G.get_vertices(vprops=[float_x, float_y])
vertices = np.delete(vertices, 0, 1)

source = 3000
target = 3043"
ELLIPTICAL="box = ellipse_bounding_box(pos[source], pos[target], tau=1.00)

lower_left = np.array([box[3], box[1]])
upper_right = np.array([box[2], box[0]])
print(pos[source])
print(pos[target])
print(lower_left)
print(upper_right)
# Euclidean heuristic. If a vertex is not in the box, make its heuristic value infinite
# so that it is never extended
indices = np.all(
    np.logical_and(lower_left <= vertices, vertices <= upper_right), axis=1
)
# include the main delete list as a filter also
inside.a = np.logical_and(indices, del_list.a)
# preserve source and target
inside[source] = True
inside[target] = True
G.set_vertex_filter(inside)
print('Removed', len(np.where(inside==False)), 'node')
"
ALLREMOVALS="
remove_leaves(G, del_list)
remove_self_edges(G)
remove_parallel(G, float_length, pollution)
remove_edges(G, float_length, pollution)
remove_paths(G, del_list, pos, float_length, pollution)
del_list[source] = True
del_list[target] = True
print(G.num_vertices(), G.num_edges())
G.set_vertex_filter(del_list)
print(G.num_vertices(), G.num_edges())

"
#Path compression
echo "Path compression"
python3 -m timeit -n 3 -r 2 -s "$SETUP" "remove_paths(G, del_list, pos, float_length, pollution)"

#Removing leaves
echo "Remove leaves"
python3 -m timeit -n 3 -r 2 -s "$SETUP" "remove_leaves(G, del_list)"

#Removing self-edges
echo "Remove self-edges"
python3 -m timeit -n 3 -r 2 -s "$SETUP" "remove_self_edges(G)"

#Removing dominated parallel edges
echo "Remove dominated parallel edges"
python3 -m timeit -n 3 -r 2 -s "$SETUP" "remove_parallel(G, float_length, pollution)"

#Removing edges for which there are better paths of length 2
echo "Remove dominated edges"
python3 -m timeit -n 3 -r 2 -s "$SETUP" "remove_edges(G, float_length, pollution)"

#Elliptical node removal
echo "Elliptical node removal"
python3 -m timeit -n 3 -r 2 -s "$SETUP" "$ELLIPTICAL"

#Node removal with Dijkstra's/A*
echo "Node removal via Dijkstra"

#Basic martins (uses lexicographic order)
echo "Basic martins:"
python3 -m timeit -n 3 -r 2 -s "$SETUP" "mospp(G.vertex(source), G.vertex(target), float_length, pollution)"

#Check label equality as a domination
echo "Counting label equality as a domination:"
python3 -m timeit -n 3 -r 2 -s "$SETUP" "mospp(G.vertex(source), G.vertex(target), float_length, pollution, equality_dominates=True)"

#Don't visit path predecessors, looking at last 2 predecessors
echo "Don't visit last two path predecessors:"
python3 -m timeit -n 3 -r 2 -s "$SETUP" "mospp(G.vertex(source), G.vertex(target), float_length, pollution, predecessors=2)"

echo "Combine both of these optimisations"
python3 -m timeit -n 3 -r 2 -s "$SETUP" "mospp(G.vertex(source), G.vertex(target), float_length, pollution, equality_dominates=True, predecessors=2)"

echo "Combine both of these optimisations with maximum graph reduction"
python3 -m timeit -n 3 -r 2 -s "$SETUP$ALLREMOVALS" "mospp(G.vertex(source), G.vertex(target), float_length, pollution, equality_dominates=True, predecessors=2)"

echo "Bidirectional search with both of these optimisations:"
#Full stopping condition (removing labels based on Pareto dominance by target)
#Minimum stopping condition always
#Minimum stopping condition infrequently



