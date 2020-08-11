"""
    Given a coordinate, find the closest vertex in the graph quickly
"""
import numpy as np
import math


def coord_match(V, target_coord: np.array, pos):
    """
    Given a coordinate, find the closest vertex in the graph quickly
    Args:
        V: nx2 matrix, where n is the number of vertices. Each row is the x, y position of the vertex associated with that row
        target_coord: the coordinate in lat, long format
        pos: the definition of distance in our graph; typically x is long and y is lat
    
    Returns:
        closest vertex, target
    """
    minimum = 0.0009
    # find all points within a box around the coordinate
    lower_left = np.array([target_coord[1] - minimum, target_coord[0] - minimum])
    upper_right = np.array([target_coord[1] + minimum, target_coord[0] + minimum])
    indices = np.all(np.logical_and(lower_left <= V, V <= upper_right), axis=1)
    inside_box = np.where(indices == 1)
    target = None
    for v in inside_box[0]:
        if (
            math.sqrt(
                np.sum(
                    np.square(pos[v].a - np.array([target_coord[1], target_coord[0]]))
                )
            )
            < minimum
        ):
            minimum = math.sqrt(
                np.sum(
                    np.square(pos[v].a - np.array([target_coord[1], target_coord[0]]))
                )
            )
            target = v
    return target
