from math import atan2, sin, cos, degrees, radians

from ..typing import IntVec3, FltVec3
from .constants import (
    FLYING_SPEED,
    WALKING_SPEED,
    PLAYER_HEIGHT,
    TERMINAL_VELOCITY,
    GRAVITY,
)

# "State" seems too generic a name
class State:
    """
    """
    flying: bool = False

    # Current (x, y, z) position in the world, specified with floats. Note
    # that, perhaps unlike in math class, the y-axis is the vertical axis.
    position: FltVec3 = (0, 0, 0)

    # First element is rotation of the player in the x-z plane (ground
    # plane) measured from the z-axis down. The second is the rotation
    # angle from the ground plane up. Rotation is in degrees.
    #
    # The vertical plane rotation ranges from -90 (looking straight down) to
    # 90 (looking straight up). The horizontal rotation range is unbounded.
    rotation: Tuple[float, float] = (0, 0)

    # Velocity in the y (upward) direction.
    dy: int = 0

    def __init__(self):
        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.strafe = [0, 0]

    def get_motion_vector(self) -> FltVec3:
        """Returns the current motion vector indicating the velocity of the player."""
        if not any(self.strafe):
            return (0.0, 0.0, 0.0)

        x, y = self.rotation
        strafe = degrees(atan2(*self.strafe))
        x_angle = radians(x + strafe)

        if not self.flying:
            dy = 0.0
            dx = cos(x_angle)
            dz = sin(x_angle)
            return (dx, dy, dz)

        y_angle = radians(y)
        m = cos(y_angle)
        dy = sin(y_angle)

        if self.strafe[1]:
            # Moving left or right.
            dy = 0.0
            m = 1

        if self.strafe[0] > 0:
            # Moving backwards.
            dy *= -1

        # When you are flying up or down, you have less left and right
        # motion.
        dx = cos(x_angle) * m
        dz = sin(x_angle) * m

        return (dx, dy, dz)

    def get_sight_vector(self) -> IntVec3:
        """Returns the current line of sight vector indicating the direction the player is looking."""
        x, y, = self.rotation

        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = cos(radians(y))

        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = sin(radians(y))
        dx = cos(radians(x - 90)) * m
        dz = sin(radians(x - 90)) * m
        return (dx, dy, dz)

    def collide(self, pos: IntVec3, height: float) -> IntVec3:
        """Check if a collision has occured."""

        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0.25
        p = list(position)
        np = normalize(position)

        # check all surrounding blocks
        for face in FACES:

            # check each dimension independently
            for i in range(3):
                if not face[i]:
                    continue

                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue

                for dy in range(height):  # check each height
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]

                    assert False
                    if tuple(op) not in self.world.blocks:
                        continue

                    p[i] -= (d - pad) * face[i]
                    if face in ((0, -1, 0), (0, 1, 0)):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.dy = 0

                    break

        return tuple(p)

    def tick(self):
        # walking
        speed = FLYING_SPEED if self.flying else WALKING_SPEED
        d = dt * speed  # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d

        # gravity
        if not self.flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            self.dy -= dt * GRAVITY
            self.dy = max(self.dy, -TERMINAL_VELOCITY)
            dy += self.dy * dt

        # collisions
        x1, y1, z1 = self.position
        self.position = self.collide((x1 + dx, y1 + dy, z1 + dz), PLAYER_HEIGHT)
