from itertools import chain
from typing import Tuple, List

from pyglet.gl import (
    glColor3d,
    glPolygonMode,
    GL_LINE,
    GL_QUADS,
    GL_FILL,
    GL_FRONT_AND_BACK,
)


from .utils cimport cube_vertices

TextureVerticies = Tuple[int, int, int, int, int, int, int, int]


def verticies(x: int, y: int, n: int = 4) -> TextureVerticies:
    """Return the bounding vertices of the texture square."""
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return (dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m)


class Texture:
    x: TextureVerticies
    y: TextureVerticies
    z: Tuple[TextureVerticies, TextureVerticies, TextureVerticies, TextureVerticies]

    def __init__(
        self, top: Tuple[int, int], bottom: Tuple[int, int], side: Tuple[int, int]
    ):
        self.x = verticies(*top)
        self.y = verticies(*bottom)
        self.z = verticies(*side) * 4

    def __iter__(self):
        return chain(self.x, self.y, self.z)


GRASS = Texture((1, 0), (0, 1), (0, 0))
SAND = Texture((1, 1), (1, 1), (1, 1))
BRICK = Texture((2, 0), (2, 0), (2, 0))
STONE = Texture((2, 1), (2, 1), (2, 1))
