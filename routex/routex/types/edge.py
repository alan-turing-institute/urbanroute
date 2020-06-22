"""Types for edges."""

from typing import Tuple
from .node import Node

Edge = Tuple(Node, Node)
Key = int
MultiEdge = Tuple(Node, Node, Key)
