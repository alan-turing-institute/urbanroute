"""Fixtures for the urbanroute module."""

from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
import pandas as pd
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
    G = complete_graph(4)
    five = G.new_edge_property("int", val=5)
    G.edge_properties["five"] = five
    return G


PATH_LENGTH = 5


@pytest.fixture(scope="function")
def path_edge_df() -> pd.DataFrame:
    """Dataframe of path edges."""
    return pd.DataFrame(
        dict(
            startnode=np.arange(PATH_LENGTH),
            endnode=np.arange(1, PATH_LENGTH + 1),
            NO2_mean=np.random.rand(PATH_LENGTH),
            length=np.random.rand(PATH_LENGTH),
        )
    )


@pytest.fixture(scope="function")
def path_vertex_df() -> pd.DataFrame:
    """Dataframe of path vertices."""
    return pd.DataFrame(
        dict(
            node=np.arange(PATH_LENGTH + 1),
            lat=np.random.rand(PATH_LENGTH + 1),
            lon=np.random.rand(PATH_LENGTH + 1),
        )
    )
