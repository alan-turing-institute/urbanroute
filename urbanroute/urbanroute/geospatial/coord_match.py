"""
    Given a coordinate, find the closest vertex in the graph quickly
"""
import math
import numpy as np


def coord_match(vertices, target_coord: np.array, pos, minimum=0.0009):
    """
    Given a coordinate, find the closest vertex in the graph quickly
    Args:
        vertices: nx2 matrix, where n is the number of vertices. Each row is the x, y
        position of the vertex associated with that row
        target_coord: the coordinate in lat, long format
        pos: the definition of distance in our graph; typically x is long and y is lat
        minimum: the inital bounding box around the coord; the closest match is expected
                 to be within this distance of the coordinate
    Returns:
        closest vertex, target
    """
    # find all points within a box around the coordinate
    lower_left = np.array([target_coord[1] - minimum, target_coord[0] - minimum])
    upper_right = np.array([target_coord[1] + minimum, target_coord[0] + minimum])
    indices = np.all(
        np.logical_and(lower_left <= vertices, vertices <= upper_right), axis=1
    )
    inside_box = np.where(indices == 1)
    target = None
    # use euclidean distance to pick the closest point within the box
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
