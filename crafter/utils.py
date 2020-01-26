import time
from typing import List, Union
from functools import lru_cache

from .typing import FltVec3, IntVec3

# from ..constants import SECTOR_SIZE
SECTOR_SIZE = 16

def timer(func):
    def timed(*args, **kwargs):
        start = time.monotonic()
        rv = func(*args, **kwargs)
        diff = time.monotonic() - start
        if diff >= 0.1:
            print(f"{func!r} took {diff}")
        return rv
    return timed

# fmt: off
@lru_cache(maxsize=0x10000)
def cube_vertices(x: int, y: int, z: int, n: int) -> List[int]:
    """Return the vertices of the cube at position x, y, z with size 2*n."""
    x_sub_n = x - n
    x_add_n = x + n

    y_sub_n = y - n
    y_add_n = y + n

    z_sub_n = z - n
    z_add_n = z + n

    return [
        x_sub_n, y_add_n, z_sub_n, x_sub_n, y_add_n, z_add_n, x_add_n, y_add_n, z_add_n, x_add_n, y_add_n, z_sub_n,  # top
        x_sub_n, y_sub_n, z_sub_n, x_add_n, y_sub_n, z_sub_n, x_add_n, y_sub_n, z_add_n, x_sub_n, y_sub_n, z_add_n,  # bottom
        x_sub_n, y_sub_n, z_sub_n, x_sub_n, y_sub_n, z_add_n, x_sub_n, y_add_n, z_add_n, x_sub_n, y_add_n, z_sub_n,  # left
        x_add_n, y_sub_n, z_add_n, x_add_n, y_sub_n, z_sub_n, x_add_n, y_add_n, z_sub_n, x_add_n, y_add_n, z_add_n,  # right
        x_sub_n, y_sub_n, z_add_n, x_add_n, y_sub_n, z_add_n, x_add_n, y_add_n, z_add_n, x_sub_n, y_add_n, z_add_n,  # front
        x_add_n, y_sub_n, z_sub_n, x_sub_n, y_sub_n, z_sub_n, x_sub_n, y_add_n, z_sub_n, x_add_n, y_add_n, z_sub_n,  # back
    ]
# fmt: on

@lru_cache(maxsize=0x400)
def normalize(pos: FltVec3):
    """Accepts `position` of arbitrary precision and returns the block containing that position.

    Parameters
    ----------
    position : :class:`FltVec3`

    Returns
    -------
    normal : :class:`IntVec3`
    """
    assert len(pos) == 3
    assert isinstance(pos[0], float)
    return tuple([round(value) for value in pos])

@lru_cache(maxsize=0x400)
def sectorize(pos: Union[IntVec3, FltVec3], sector_size: int = SECTOR_SIZE):
    """Returns a tuple representing the sector for the given position.

    Parameters
    ----------
    pos : Union[IntVec3, FltVec3]
        block position to use.

    Returns
    -------
    sector : :class:`IntVec3`
        Co-ordinates of sector corner.
    """
    if isinstance(pos[0], float):
        x, y, z, = normalize(pos)
    else:
        x, y, z, = pos

    x, y, z = (
        x // sector_size,
        y // sector_size,
        z // sector_size,
    )

    return (x, 0, z)
