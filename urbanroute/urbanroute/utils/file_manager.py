"""Functions for saving and loading from files."""

from __future__ import annotations
from typing import TYPE_CHECKING
import matplotlib.pyplot as plt
from graph_tool.all import load_graph

if TYPE_CHECKING:
    from pathlib import Path
    from graph_tool import Graph
    import geopandas as gpd

OVERLAY_FILENAME = "london_no2_overlay.png"
GRAPH_FILENAME = "london_no2_graph.gt"

class FileManager:
    """Saving and loading files."""

    def __init__(self, root: Path) -> None:
        self.root = root
        # try make directory if it doesn't exist, but don't make parents
        self.root.mkdir(parents=False, exist_ok=True)

    def save_overlay_to_file(
        self, gdf: gpd.GeoDataFrame, filename: str = OVERLAY_FILENAME,
    ) -> None:
        """Given pollution geodataframe save to a png to be used as an overlay for the web app."""
        gdf.crs = "EPSG:4326"
        gdf.to_crs(epsg="3857")
        gdf.plot(column="NO2_mean")
        plt.axis("off")
        plt.savefig(
            self.root / filename,
            transparent=True,
            dpi=1000,
            cmap="inferno",
            bbox_inches="tight",
            pad_inches=0,
        )

    def save_graph_to_file(self, G: Graph, filename: str = GRAPH_FILENAME) -> None:
        """Save the graph to a file."""

        # NOTE "gt" is the recommended format for speed
        # see https://graph-tool.skewed.de/static/doc/quickstart.html#graph-i-o
        filepath = self.root / filename
        with filepath.open(mode="wb+") as graph_file:
            G.save(graph_file, fmt="gt")

    def load_graph_from_file(self, filename: str = GRAPH_FILENAME) -> Graph:
        """Load the graph from file."""
        return load_graph(self.root / filename)
