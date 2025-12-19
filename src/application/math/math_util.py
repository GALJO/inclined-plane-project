from application.math.scalar import Scalar
from infrastructure.config.config import CONFIG


def translate_abs(x: Scalar | float, y: Scalar | float) -> tuple[Scalar | float, Scalar | float]:
    """
    Absolutely translates point in coordinate system starting in bottom-left screen corner
    to point in pygame coordinate system and vice versa. [x, y] vector changes sense, direction and value.
    :param x: point x-coordinate
    :param y: point y-coordinate
    :returns: (x, y) - translated coordinate
    :rtype: tuple[float, float]
    """
    return x, y * -1 + CONFIG.resolution[1]


def translate(x: Scalar | float, y: Scalar | float) -> tuple[Scalar | float, Scalar | float]:
    """
    Relatively translates point in coordinate system starting in bottom-left screen corner
    to point in pygame coordinate system and vice versa. [x, y] vector changes only sense and direction.
    :param x: vector x-coordinate
    :param y: vector y-coordinate
    :returns: (x, y) - translated coordinate
    :rtype: tuple[float, float]
    """
    return x, y * (-1)
