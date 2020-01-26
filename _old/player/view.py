from typing import Dict

from pyglet.graphics import TextureGroup, Batch
from pyglet.gl import GL_QUADS

from ..typing import IntVec3
from ..texture import GRASS, SAND, BRICK, STONE
from ..constants import FACES
from ..utils import sectorize, normalize, cube_vertices


class View:
    """A view into the world, this is a players camera."""
    def __init__(self, game, texture_group: TextureGroup):
        self.game = game
        self.loop = game.loop

        self.texture_group = texture_group
        self.batch = Batch()

        self.shown: Dict[IntVec3, Tuple[Texture, VertextList]] = {}

    # Public

    async def check_neighbors(self, pos: IntVec3):
        """Check all blocks surrounding `position` and ensure their visual state is current.

        This means hiding blocks that are not exposed and ensuring that
        all exposed blocks are shown. Usually used after a block is added or removed.
        """
        x, y, z, = pos

        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)

            try:
                self.blocks[key]
            except KeyError:
                continue

            if self.exposed(key) and key not in self.shown:
                await self.show_block(key)

            elif key in self.shown:
                await self.hide_block(key)

    async def show_block(self, pos: IntVec3):
        """Show the block at the given `position`.

        Parameters
        ----------
        pos : tuple of len 3
            The (x, y, z) position of the block to show.
        """
        texture = self.blocks[position]

        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(texture)

        vertex_list = await self.loop.run_in_executor(
            self.game.executor,
            self.batch.add,
            24,
            GL_QUADS,
            self.group,
            ("v3f/static", vertex_data),
            ("t2f/static", texture_data),
        )

        assert isinstance(vertex_list, VertextList)

        self.shown[position] = (texture, vertex_list)

    async def hide_block(self, pos: IntVec3):
        """Hide the block at the given `position`.

        Hiding does not remove the block from the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        """
        _, vertex_list = self.shown.pop(pos)
        await self.loop.run_in_executor(self.game.executor, vertex_list.delete)

    async def filter_map_sector(
        self,
        pred: Callable[[IntVec3], bool],
        func: Callable[[IntVec3], ...],
        sector: IntVec3,
    ):
        """Apply a filter and then map over a sectors blocks."""
        sector = self.sectors[sector]
        tasks = {func(pos) for pos in sector if pred(pos)}
        await gather(*tasks)

    async def change_sectors(self, show: Set[IntVec3], hide: Set[IntVec3]):
        def should_show(pos: IntVec3) -> bool:
            return pos not in self.shown and self.exposed(position) 

        def should_hide(pos: IntVec3) -> bool:
            return pos in self.shown

        for sector in show:
            await self.filter_map_sector(should_show, self.show_block, sector)

        for sector in hide:
            await self.filter_map_sector(should_hide, self.hide_block, sector)
