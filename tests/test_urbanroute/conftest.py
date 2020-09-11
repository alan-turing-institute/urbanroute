"""Fixtures for the urbanroute module."""

from __future__ import annotations
from typing import TYPE_CHECKING
import pytest
from graph_tool.generation import complete_graph

if TYPE_CHECKING:
    from pathlib import Path
    from graph_tool import Graph


@pytest.fixture(scope="function")
def cache_dir(tmp_path_factory) -> Path:
    """Create a temporary directory."""
    return tmp_path_factory.mktemp(".tmp")


@pytest.fixture(scope="function")
def complete_4() -> Graph:
    """Generate a complete graph on 4 nodes."""
    return complete_graph(4)
