from . import Game

from pyglet.app import run as _pyglet_app_run


def main():
    with Game(width=800, height=600, caption="Minecraft"):
        _pyglet_app_run()


if __name__ == "__main__":
    main()
