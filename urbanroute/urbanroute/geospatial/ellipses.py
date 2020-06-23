import matplotlib.pyplot as plt
import math
from shapely.geometry import Point, Polygon
import shapely.affinity
from descartes import PolygonPatch
from typing import Tuple, List


def ellipse_bounding_box(source: Tuple[float, float], dest: Tuple[float, float], tau=1.1) -> List[Tuple[float,float]]:
    """
        Gives bounding box around source and destination nodes.
        
        Args:
            source, target: two points in longitude, latitude format
            tau: a constant to be multiplied by the distance between the source and target; the optimal path
                 is assumed to be smaller than this product.
        
        Returns: 
            A bounding box that surrounds the source and target,
            includes all paths of length at most: tau multiplied by the distance between the points.
            This inclusion is done by creating an implicit elipse that the source and dest are foci of."""
    theta = math.atan((dest[1]-source[1])/(dest[0]-source[0]))
    tau = 1.1
    distance = math.sqrt((dest[1]-source[1])**2 + (dest[0]-source[0])**2) * tau
    b = (dest[1]+source[1])/2
    a = (dest[0]+source[0])/2
    A = (tau/2) * math.sqrt((dest[1] - source[1])**2 + (dest[0] - source[0])**2)
    B = math.sqrt(A**2 - ((dest[1] - source[1])**2 + (dest[0] - source[0])**2)/4)
    return [(a + math.sqrt(A**2 * math.cos(theta)**2 + B ** 2 * math.sin(theta)**2),
                b + math.sqrt(A**2 * math.sin(theta)**2 + B ** 2 * math.cos(theta)**2)),
            (a + math.sqrt(A**2 * math.cos(theta)**2 + B ** 2 * math.sin(theta)**2),
                b - math.sqrt(A**2 * math.sin(theta)**2 + B ** 2 * math.cos(theta)**2)),
            (a - math.sqrt(A**2 * math.cos(theta)**2 + B ** 2 * math.sin(theta)**2),
                b - math.sqrt(A**2 * math.sin(theta)**2 + B ** 2 * math.cos(theta)**2)),
            (a - math.sqrt(A**2 * math.cos(theta)**2 + B ** 2 * math.sin(theta)**2),
                b + math.sqrt(A**2 * math.sin(theta)**2 + B ** 2 * math.cos(theta)**2))]

