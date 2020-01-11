from pyglet.app import run as _pyglet_app_run

from crafter import Game


def main():
    window = Game(width=800, height=600, caption="Minecraft")
    window.setup()
    _pyglet_app_run()


if __name__ == "__main__":
    main()
