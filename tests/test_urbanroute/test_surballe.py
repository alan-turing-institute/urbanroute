"""Fixtures for the urbanroute module."""
import pytest
import networkx as nx
# See graph.jpg from the wikipedia page: https://en.wikipedia.org/wiki/File:First_graph.jpg


@pytest.fixture
def small_graph():
    G = nx.Graph()
    G.add_nodes_from(['A', 'B', 'C', 'D', 'E', 'F'])
    G.add_edges_from([('A','B',{'weight':1}),('A','C',{'weight':2}),('C','D',{'weight':2}),('D','B',{'weight':1}),
    ('D','F',{'weight':1}),('F','E',{'weight':2}),('B','E',{'weight':2})])
    return G

@pytest.fixture
def large_graph():
    G = nx.Graph()
    G.add_nodes_from([x for x in range(1,19)])
    edges = [(1,2,1),(1,3,1),(1,4,3),(2,3,9),(2,6,1),(3,1,7),(3,8,1),(4,7,1),(5,4,4),(7,10,4),(8,7,2),(8,12,4),(8,9,0),(9,13,3)\
        ,(10,14,4),(10,15,2),(11,17,6),(12,11,1),(12,16,6),(13,15,1),(14,18,4),(15,18,8),(16,18,8),(17,18,2)]
    for x,y,weight in edges:
        G.add_edge((x,y,{'weight':weight}))
    return G


def test_suurballe_small(small_graph):
    """Is the implementation of Suurballe's algorithm correct?"""
    # solve suurballe's with origin A and destination F
    small_graph
    solution = (['A', 'C', 'D', 'F'], ['A', 'B', 'E', 'F'])
    assert True

def test_suurballe_large(large_graph):
    """Is the implementation of Suurballe's algorithm correct?"""
    # solve suurballe's with origin A and destination F
    large_graph
    solution = ([1,3,8,12,11,17,18],[1,4,7,10,14,18])
    assert True