"""Test IO functions."""

from urbanroute.utils import from_dataframes


def test_from_dataframes(path_edge_df, path_vertex_df) -> None:
    """Test a graph can be loaded from dataframes."""
    G = from_dataframes(path_edge_df, path_vertex_df)
    assert G.num_edges() == G.num_vertices() - 1

    vertex_properties = ["lat", "lon"]
    edge_properties = ["NO2_mean", "length"]
    for p in vertex_properties:
        assert p in G.vertex_properties
    for e in edge_properties:
        assert e in G.edge_properties
