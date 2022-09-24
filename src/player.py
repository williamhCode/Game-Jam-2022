import pymunk
from pymunk import Vec2d
from enum import Enum

from engine.render import Renderer
from engine.texture import Texture
from .animation import AnimatedSprite, AnimationState
from . import animation


def move_towards(curr: Vec2d, target: Vec2d, force: float):
    diff = target - curr
    change = diff.normalized() * force
    # clamp value based to the difference
    change = diff if diff.get_length_sqrd() < change.get_length_sqrd() else change
    return curr + change


class Player(pymunk.Circle):
    MAX_SPEED = 200
    ACCELERATION = 500
    FRICTION = 500

    MASS = 10
    RADIUS = 25

    STATE = "player_state"
    DIRECTION = "direction"

    class State(Enum):
        IDLE = 1
        WALKING = 2
        SHOVELING = 3

    class Direction(Enum):
        UP = 1
        DOWN = 2
        RIGHT = 3
        LEFT = 4

    body: pymunk.Body

    def __init__(self, pos):
        # physics
        body = pymunk.Body(self.MASS, float('inf'), body_type=pymunk.Body.DYNAMIC)
        body.position = pos

        super().__init__(body, self.RADIUS)
        self.friction = 0.5

        # variables
        self.input = Vec2d.zero()

        back_sprites = AnimatedSprite(
            animation.load_textures("src/imgs/Player", "Back", 8), 1 / 12)
        front_sprites = AnimatedSprite(
            animation.load_textures("src/imgs/Player", "Front", 8), 1 / 12)
        right_textures = animation.load_textures("src/imgs/Player", "Side", 8)
        right_sprites = AnimatedSprite(right_textures, 1 / 12)
        left_sprites = AnimatedSprite(right_textures, 1 / 12, flipped=True)
        
        self.animation_state = AnimationState((self.STATE, self.DIRECTION))
        self.animation_state.add_sprite(back_sprites, (self.State.WALKING, self.Direction.UP))
        self.animation_state.add_sprite(front_sprites, (self.State.WALKING, self.Direction.DOWN))
        self.animation_state.add_sprite(right_sprites, (self.State.WALKING, self.Direction.RIGHT))
        self.animation_state.add_sprite(left_sprites, (self.State.WALKING, self.Direction.LEFT))

        self.animation_state.set_state(self.STATE, self.State.WALKING)
        self.animation_state.set_state(self.DIRECTION, self.Direction.DOWN)

        temp_sprite = front_sprites.textures[0]
        width = 128, 192
        self.position_offset = Vec2d(temp_sprite.width / 2, 20)

    def move(self, input: Vec2d):
        self.input = input.normalized()
        if (input.y == 1):
            self.animation_state.set_state(self.DIRECTION, self.Direction.UP)
        elif (input.y == -1):
            self.animation_state.set_state(self.DIRECTION, self.Direction.DOWN)
        elif (input.x == 1):
            self.animation_state.set_state(self.DIRECTION, self.Direction.RIGHT)
        elif (input.x == -1):
            self.animation_state.set_state(self.DIRECTION, self.Direction.LEFT)

    def _apply_input(self, dt):
        if self.input == Vec2d.zero():
            self.body.velocity = move_towards(self.body.velocity, Vec2d.zero(), self.FRICTION * dt)
        else:
            self.body.velocity = move_towards(
                self.body.velocity, self.input * self.MAX_SPEED, self.ACCELERATION * dt)

    def update(self, dt):
        self._apply_input(dt)
        self.body.position += self.body.velocity * dt
        self.animation_state.update(dt)

    def draw(self, renderer: Renderer):
        renderer.draw_circle(
            (200, 20, 20), self.body.position, self.radius, 0)

        self.animation_state.get_sprite().draw(renderer, self.body.position, offset=-self.position_offset)

