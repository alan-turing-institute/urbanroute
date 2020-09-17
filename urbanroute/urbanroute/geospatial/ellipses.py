"""
    Use the ellipse bounding box method in order to bound two points.
    An Optimum Vehicular Path Solution with Multi-heuristics, Feng Lu and Yanning Guan
"""
import math
from typing import Tuple, List, Optional


def ellipse_bounding_box(
    source: Tuple[float, float], target: Tuple[float, float], tau: Optional[float] = 1.1
) -> List[float]:
    """
    Gives bounding box around source and targetination nodes.
    See: An Optimum Vehicular Path Solution with Multi-heuristics, Feng Lu and Yanning Guan


    Args:
        source, target: two points in longitude, latitude format
        tau: a constant to be multiplied by the distance between the source and target;
        the optimal path is assumed to be smaller than this product.

    Returns:
        A bounding box that surrounds the source and target, in north, south, east, west format,
        includes all paths of length at most: tau multiplied by the distance between the points.
        This inclusion is done by creating an implicit ellipse
        that the source and target are foci of.
    """
    if (target[0] - source[0]) == 0:
        theta = math.pi / 2
    else:
        theta = math.atan((target[1] - source[1]) / (target[0] - source[0]))
    center_latitude = (target[1] + source[1]) / 2
    center_longitude = (target[0] + source[0]) / 2
    # here we define an ellipse with the source and target points as foci
    major_axis = (tau / 2) * math.sqrt(
        (target[1] - source[1]) ** 2 + (target[0] - source[0]) ** 2
    )
    minor_axis = math.sqrt(
        major_axis ** 2
        - ((target[1] - source[1]) ** 2 + (target[0] - source[0]) ** 2) / 4
    )
    return [
        center_latitude
        + math.sqrt(
            major_axis ** 2 * math.sin(theta) ** 2
            + minor_axis ** 2 * math.cos(theta) ** 2
        ),
        center_latitude
        - math.sqrt(
            major_axis ** 2 * math.sin(theta) ** 2
            + minor_axis ** 2 * math.cos(theta) ** 2
        ),
        center_longitude
        + math.sqrt(
            major_axis ** 2 * math.cos(theta) ** 2
            + minor_axis ** 2 * math.sin(theta) ** 2
        ),
        center_longitude
        - math.sqrt(
            major_axis ** 2 * math.cos(theta) ** 2
            + minor_axis ** 2 * math.sin(theta) ** 2
        ),
    ]
