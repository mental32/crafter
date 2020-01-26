from typing import Tuple, Set, Optional

from ..typing import IntVec3
from . import GameServer


class World:
    def __init__(self, server: GameServer):
        self.server = server
        self.blocks: Dict = {}

    # Public

    def hit_test(self, pos: IntVec3, vector: IntVec3, max_distance: int = 8) -> Optional[Tuple[IntVec3, IntVec3]]:
        """Line of sight search from current position.


        If a block is intersected it is returned, along with
        the block previously in the line of sight.
        If no block is found, return None, None.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.
        """
        m = 8
        x, y, z = pos
        dx, dy, dz = vector

        previous = None
        for _ in range(max_distance * m):
            key = normalize((x, y, z))

            if key != previous and key in self.blocks:
                return key, previous

            previous = key
            x, y, z = (
                x + dx / m,
                y + dy / m,
                z + dz / m,
            )

        return None

    def exposed(self, pos: IntVec3) -> bool:
        """Check if a given block at `pos` is not surrounded on all 6 sides."""
        x, y, z, = pos
        return any((x + dx, y + dy, z + dz) not in self.blocks for dx, dy, dz in FACES)

    async def add_block(self, pos: IntVec3, texture: Texture):
        """Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        """
        assert pos not in self.blocks

        self.blocks[position] = texture
        self.sectors[sectorize(position)] += [position]

    async def remove_block(self, pos: IntVec3):
        """Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        """
        del self.blocks[position]
        self.sectors[sectorize(position)].remove(position)

    async def change_sectors(self, before: IntVec3, after: IntVec3) -> Tuple[Set[IntVec3], Set[IntVec3]]:
        """Move from sector `before` to sector `after`.

        A sector is a contiguous x, y sub-region of world.
        Sectors are used to speed up world rendering.
        """
        befores = set()
        afters = set()

        bx, by, bz = before
        ax, by, az = after

        bounds = range(-4, 5)

        for dx in bounds:
            for dz in bounds:
                if dx ** 2 + dz ** 2 > 25:
                    continue

                befores.add((bx + dx, by, bz + dz))
                afters.add((ax + dx, ay, az + dz))

        show = afters - befores
        hide = befores - afters

        return show, hide
