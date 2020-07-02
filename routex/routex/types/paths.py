"""Types for paths."""

from typing import List, Tuple
from .node import Node

Path = List[Node]
DisjointPaths = Tuple[Path, Path]
