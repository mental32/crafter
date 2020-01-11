from typing import List
from functools import lru_cache

from .constants import SECTOR_SIZE

# fmt: off
cdef list cube_vertices(x: int, y: int, z: int, n: int):
    """Return the vertices of the cube at position x, y, z with size 2*n."""
    return [
        x - n, y + n, z - n, x - n, y + n, z + n, x + n, y + n, z + n, x + n, y + n, z - n,  # top
        x - n, y-n, z - n, x + n, y-n, z - n, x + n, y-n, z + n, x - n, y-n, z + n,  # bottom
        x - n, y-n, z - n, x - n, y-n, z + n, x - n, y + n, z + n, x - n, y + n, z - n,  # left
        x + n, y-n, z + n, x + n, y-n, z - n, x + n, y + n, z - n, x + n, y + n, z + n,  # right
        x - n, y-n, z + n, x + n, y-n, z + n, x + n, y + n, z + n, x - n, y + n, z + n,  # front
        x + n, y-n, z - n, x - n, y-n, z - n, x - n, y + n, z - n, x + n, y + n, z - n,  # back
    ]
# fmt: on

@lru_cache
def normalize(position):
    """ Accepts `position` of arbitrary precision and returns the block
    containing that position.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    block_position : tuple of ints of len 3

    """
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return (x, y, z)

@lru_cache
def sectorize(position):
    """ Returns a tuple representing the sector for the given `position`.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    sector : tuple of len 3

    """
    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return (x, 0, z)

