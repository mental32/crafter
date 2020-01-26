from asyncio import AbstractEventLoop
from typing import Optional

from websockets.server import serve as _websocket_serve


class WorldServer:
    def __init__(self, host: str, port: int, *, loop: Optional[AbstractEventLoop] = None):
        self._host = host
        self._port = port
        self._loop = loop

        self._websocket_server = None
        self._world = World(self)

    async def __aenter__(self):
        await self.serve(self._host, self._port)
        await self.generate_world()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    # Internal

    async def _ws_handler(self, websocket, _):
        async for message in websocket:
            print(message)

    async def generate_world(self):
        n = 160  # 1/2 width and height of world
        s = 1  # step size
        y = 0  # initial y height
 
        for x in range(-n, n + 1, s):
            for z in range(-n, n + 1, s):
                # create a layer stone an grass everywhere.
                self.world[(x, y - 2, z)] = DIRT
                self.world[(x, y - 3, z)] = STONE

                if x in (-n, n) or z in (-n, n):
                    # create outer walls.
                    for dy in range(-2, 3):
                        self.world[(x, y + dy, z)] = STONE

    # Event loop

    def tick(self, player: Player):
        await sleep(1 / TICKS_PER_SECOND)

        sector = sectorize(player.position)

        if sector != player.sector:
            # self.world.change_sectors(self.sector, sector)
            await player.socket.send(CHANGED_SECTORS)
            player.sector = sector

    # Public

    async def serve(self):
        self._websocket_server = server = await _websocket_serve(self._ws_handler)
        return server

    async def close(self):
        await self._websocket_server.close()
        await self._websocket_server.wait_closed()
