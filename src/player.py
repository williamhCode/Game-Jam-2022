import pymunk
from pymunk import Vec2d
from engine.render import Renderer


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
    SIZE = (50, 80)

    MASS = 10
    RADIUS = 30

    body: pymunk.Body

    def __init__(self, pos):
        body = pymunk.Body(self.MASS, float('inf'), body_type=pymunk.Body.DYNAMIC)
        body.position = pos

        super().__init__(body, self.RADIUS)

        self.input = Vec2d.zero()

    def move(self, input: Vec2d):
        self.input = input.normalized()

    def _apply_input(self, dt):
        if self.input == Vec2d.zero():
            self.body.velocity = move_towards(self.body.velocity, Vec2d.zero(), self.FRICTION * dt)
        else:
            self.body.velocity = move_towards(
                self.body.velocity, self.input * self.MAX_SPEED, self.ACCELERATION * dt)

    def update(self, dt):
        self._apply_input(dt)
        self.body.position += self.body.velocity * dt

    def draw(self, renderer: Renderer):
        # renderer.draw_rectangle(
        #     (0, 0, 0), (self.pos.x, self.pos.y), self.SIZE, fade=4, width=5)
        renderer.draw_circle(
            (200, 20, 20), self.body.position, self.radius, 0)

"""
    def __init__(self, pos):
        self.pos = vec2(pos)
        self.vel = vec2(0)
        self.input = vec2(0)

    def move(self, input):
        self.input = normalize(input)

    def _apply_input(self, dt):
        if self.input == vec2(0):
            self.vel = move_towards(self.vel, vec2(0), self.FRICTION * dt)
        else:
            self.vel = move_towards(
                self.vel, self.input * self.MAX_SPEED, self.ACCELERATION * dt)

    def update(self, dt):
        self._apply_input(dt)
        self.pos += self.vel * dt

    def draw(self, renderer: Renderer):
        renderer.draw_rectangle(
            (0, 0, 0), (self.pos.x, self.pos.y), self.SIZE, fade=4, width=5)
"""
