"""Tests for saving and loading files."""

from urbanroute.utils import FileManager


def test_save_load_graph(cache_dir, complete_4) -> None:
    """Test saving and loading graphs from file."""
    filename = "k4.gt"
    manager = FileManager(cache_dir)
    manager.save_graph_to_file(complete_4, filename=filename)
    assert (cache_dir / filename).exists()
    loaded_graph = manager.load_graph_from_file(filename=filename)
    assert loaded_graph.num_vertices() == complete_4.num_vertices()
    assert loaded_graph.num_edges() == complete_4.num_edges()
