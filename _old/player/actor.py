from pyglet.window import key, mouse

# Convenience list of num keys.
NUM_KEYS = [
    key._1,
    key._2,
    key._3,
    key._4,
    key._5,
    key._6,
    key._7,
    key._8,
    key._9,
    key._0,
]


class Actor(State):
    """An actor is responsible for reacting to events."""

    def __init__(self):
        super().__init__()

    # Event handlers

    async def on_key_press(self, symbol: int, modifiers: int):
        """Called when the player presses a key."""
        if symbol == key.W:
            self.strafe[0] -= 1

        elif symbol == key.S:
            self.strafe[0] += 1

        elif symbol == key.A:
            self.strafe[1] -= 1

        elif symbol == key.D:
            self.strafe[1] += 1

        elif symbol == key.SPACE and self.dy == 0:
            self.dy = JUMP_SPEED

        elif symbol == key.TAB:
            self.flying = not self.flying

        elif symbol in NUM_KEYS:
            index = (symbol - NUM_KEYS[0]) % len(self.inventory)
            self.block = self.inventory[index]

    async def on_key_release(self, symbol: int, modifiers: int):
        """Called when the player releases a key."""
        if symbol == key.W:
            self.strafe[0] += 1

        elif symbol == key.S:
            self.strafe[0] -= 1

        elif symbol == key.A:
            self.strafe[1] += 1

        elif symbol == key.D:
            self.strafe[1] -= 1

    async def on_mouse_motion(self, x: int, y: int, dx: float, dy: float):
        """Called when the player moves the mouse."""
        m = 0.15
        x, y = self.rotation
        x, y = x + dx * m, y + dy * m
        y = max(-90, min(90, y))
        self.rotation = (x, y)

    async def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == mouse.LEFT:
            vector = self.get_sight_vector()
            block, previous = self.game.world.hit_test(self.position, vector)

            if block and self.game.world.blocks[block] != STONE:
                self.game.world.remove_block(block)
