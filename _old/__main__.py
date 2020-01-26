import asyncio

from pyglet.app import run as _pyglet_app_run

from . import WorldServer, Game

def _launch_window(server: WorldServer):
    with Game(width=800, height=600, caption="Minecraft", server=server):
        _pyglet_app_run()

async def _launch_game(server: WorldServer):
    async with server:
        await loop.run_in_executor(None, launch, server)

@click.command()
@click.option("-r", "--resources", type=Path, default=Path("./resources/"))
def main(resources: Path):
    loop = asyncio.get_event_loop()

    server = WorldServer("localhost", 7898, loop=loop)

    asyncio.run(_launch_game(server))

if __name__ == "__main__":
    asyncio.run(main())
