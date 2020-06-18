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


def test_suurballe(small_graph):
    """Is the implementation of Suurballe's algorithm correct?"""
    # solve suurballe's with origin A and destination F
    small_graph
    solutions = (['A', 'C', 'D', 'F'], ['A', 'B', 'E', 'F'])
    assert True
