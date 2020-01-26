from asyncio import AbstractEventLoop, get_event_loop
from typing import Optional

import pyglet
from pyglet import image, clock
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

from .utils import timer


__all__ = ("Game",)


class Game(Window):
    # Whether or not the window exclusively captures the mouse.
    __mouse_is_exclusive: bool = False

    # Which sector the player is currently in.
    sector = None

    # The crosshairs at the center of the screen.
    reticle = None

    def __init__(
        self, *args, loop: Optional[AbstractEventLoop] = None, **kwargs,
    ):
        Window.__init__(self, *args, **kwargs)

        self.loop = loop or get_event_loop()

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

        clock.schedule_interval(self.tick, 0.012)

    @timer
    def __enter__(self):
        # Set the color of "clear", i.e. the sky, in rgba.
        glClearColor(0.5, 0.69, 1.0, 1)

        # Enable culling (not rendering) of back-facing facets -- facets that aren't
        # visible to you.
        glEnable(GL_CULL_FACE)

        # Set the texture minification/magnification function to GL_NEAREST (nearest
        # in Manhattan distance) to the specified texture coordinates. GL_NEAREST
        # "is generally faster than GL_LINEAR, but it can produce textured images
        # with sharper edges because the transition between texture elements is not
        # as smooth."
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        # Enable fog. Fog "blends a fog color with each rasterized pixel fragment's
        # post-texturing color."
        glEnable(GL_FOG)

        # Set the fog color.
        glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))

        # Say we have no preference between rendering speed and quality.
        glHint(GL_FOG_HINT, GL_DONT_CARE)

        # Specify the equation used to compute the blending factor.
        glFogi(GL_FOG_MODE, GL_LINEAR)

        # How close and far away fog starts and ends. The closer the start and end,
        # the denser the fog in the fog range.
        glFogf(GL_FOG_START, 20.0)
        glFogf(GL_FOG_END, 60.0)
        return self

    def __exit__(self, *_):
        pass

    # Helpers

    def _draw_2d(self):
        self.set_2d()

        # Draw the label in the top left of the screen.
        # x, y, z = self.player.position
        x, y, z, = (*self.get_location(), 0)

        self.label.text = (
            f"{pyglet.clock.get_fps()!s} "
            f"({x}, {y})"
            # f"({x}, {y}, {z}) "
            # f"{len(self.world.shown)} / {len(self.world.blocks)}"
        )


        # Draw the crosshairs in the center of the screen.
 
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

    # Ticker

    def tick(self, dt):
        self._draw_2d()

    # Event handlers

    def set_exclusive_mouse(self, exclusive: bool):
        super().set_exclusive_mouse(exclusive)
        self.__exclusive_mouse = exclusive

    def on_draw(self):
        self.clear()
        self.label.draw()
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)
        # self._draw_2d()

    def on_resize(self, width, height):
        """Called when the window is resized to a new `width` and `height`."""
        self.label.y = height - 10

        if self.reticle:
            self.reticle.delete()

        x, y = self.width // 2, self.height // 2
        n = 10

        vertex = (x - n, y, x + n, y, x, y - n, x, y + n)
        self.reticle = pyglet.graphics.vertex_list(4, ("v2i", vertex))
