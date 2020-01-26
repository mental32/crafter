import time
import random
from math import atan2, sin, cos, degrees, radians
from typing import Tuple
from queue import Queue, Empty
from threading import Thread
from collections import deque
from itertools import chain
from concurrent.futures import ThreadPoolExecutor

import pyglet
from pyglet import image
from pyglet.window import key, mouse, Window
from pyglet.gl import (
    GL_CULL_FACE,
    GL_DEPTH_TEST,
    GL_DONT_CARE,
    GL_FILL,
    GL_FOG,
    GL_FOG_COLOR,
    GL_FOG_END,
    GL_FOG_HINT,
    GL_FOG_MODE,
    GL_FOG_START,
    GL_FRONT_AND_BACK,
    GL_LINE,
    GL_LINEAR,
    GL_LINES,
    GL_MODELVIEW,
    GL_NEAREST,
    GL_PROJECTION,
    GL_QUADS,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    glClearColor,
    glColor3d,
    glDisable,
    glEnable,
    GLfloat,
    glFogf,
    glFogfv,
    glFogi,
    glHint,
    glLoadIdentity,
    glMatrixMode,
    glOrtho,
    glPolygonMode,
    glRotatef,
    glTexParameteri,
    glTranslatef,
    gluPerspective,
    glViewport,
)

from .texture import BRICK, SAND, GRASS, STONE

from .world import World
from .utils import normalize, sectorize, timer, cube_vertices
from .player import Player
from .constants import (
    GRAVITY,
    JUMP_SPEED,
    FACES,
    PLAYER_HEIGHT,
    TERMINAL_VELOCITY,
    WALKING_SPEED,
    FLYING_SPEED,
    TICKS_PER_SEC,
)


class Game(Window):
    # Whether or not the window exclusively captures the mouse.
    __exclusive_mouse: bool = False

    # Which sector the player is currently in.
    sector = None

    # The crosshairs at the center of the screen.
    reticle = None

    def __init__(
        self,
        *args,
        server_target: Union[GameServer, str],
        loop: Optional[AbstractEventLoop] = None,
        **kwargs,
    ):
        Window.__init__(self, *args, **kwargs)

        self.loop = loop or get_event_loop()

        if not isinstance(server_target, (GameServer, str)):
            raise TypeError("server_target argument must be a GameServer or str.")

        self.executor = ThreadPoolExecutor()

        self.texture_group = TextureGroup(image.load(TEXTURE_PATH).get_texture())

        self.player = Player(self)

        # The label that is displayed in the top left of the canvas.atan2
        self.label = pyglet.text.Label(
            "",
            font_name="Arial",
            font_size=18,
            x=10,
            y=self.height - 10,
            anchor_x="left",
            anchor_y="top",
            color=(0, 0, 0, 255),
        )

    # Event handling

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Called when a mouse button is pressed. See pyglet docs for button amd modifier mappings."""
        if self.__exclusive_mouse:
            self.player.on_mouse_press(x, y, button, modifiers)
        else:
            self.set_exclusive_mouse(True)

    def on_mouse_motion(self, x: int, y: int, dx: float, dy: float):
        """Called when the player moves the mouse."""
        if self.__exclusive_mouse:
            self.player.on_mouse_motion(x, y, dx, dy)

    def on_key_press(self, symbol, modifiers):
        """Called when the player presses a key."""
        if symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
            return

        self.player.on_key_press(symbol, modifiers)
        self.player.socket

    def on_key_release(self, symbol, modifiers):
        """Called when the player releases a key."""
        self.player.on_key_release(symbol, modifiers)

    def on_resize(self, width, height):
        """Called when the window is resized to a new `width` and `height`."""
        self.label.y = height - 10

        if self.reticle:
            self.reticle.delete()

        x, y = self.width // 2, self.height // 2
        n = 10

        vertex = (x - n, y, x + n, y, x, y - n, x, y + n)
        self.reticle = pyglet.graphics.vertex_list(4, ("v2i", vertex))

    def on_draw(self):
        self.clear()
        # self._draw_3d()
        self._draw_2d()

    def _draw_3d(self):
        self.set_3d()

        glColor3d(1, 1, 1)
        self.world.batch.draw()

        vector = self.player.get_sight_vector()
        block = self.world.hit_test(self.player.position, vector)[0]
        if block:
            x, y, z = block
            vertex_data = cube_vertices(x, y, z, 0.51)
            glColor3d(0, 0, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ("v3f/static", vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def _draw_2d(self):
        self.set_2d()

        # Draw the label in the top left of the screen.
        x, y, z = self.player.position

        self.label.text = (
            f"{pyglet.clock.get_fps()!s} "
            f"({x}, {y}, {z}) "
            f"{len(self.world.shown)} / {len(self.world.blocks)}"
        )

        self.label.draw()

        # Draw the crosshairs in the center of the screen.
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)

    # Other

    def set_2d(self):
        """Configure OpenGL to draw in 2d."""
        width, height = self.get_size()

        glDisable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        """Configure OpenGL to draw in 3d."""
        width, height = self.get_size()

        glEnable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, cos(radians(x)), 0, sin(radians(x)))
        x, y, z = self.position
        glTranslatef(-x, -y, -z)
