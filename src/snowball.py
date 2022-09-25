from engine.render import Renderer
from engine.texture import Texture
from . import funcs

import pymunk
from pymunk import Vec2d
import math


def radius_to_volume(radius):
    return (4 / 3) * math.pi * radius ** 3


def volume_to_radius(volume):
    return (3 * volume / (4 * math.pi)) ** (1 / 3)


class Snowball(pymunk.Body):
    sprites = None

    circle_base: pymunk.Circle

    def __init__(self, pos, radius, mass):
        super().__init__(mass, float('inf'), body_type=pymunk.Body.DYNAMIC)
        self.position = pos

        self.circle_base = pymunk.Circle(self, radius)
        self.circle_base.friction = 2.0
        self.circle_base.elasticity = 0.0

        self.volume = radius_to_volume(radius)
        self.local_density = mass / self.volume

        if Snowball.sprites == None:
            Snowball.sprites = funcs.load_textures("src/imgs", "SnowBall", 1)

        self.sprites = Snowball.sprites

        self.main_sprite = self.sprites[0]
        self._resize_sprite()

    def _resize_sprite(self):
        ball_radius = self.circle_base.radius * 1.4
        self.main_sprite.resize(ball_radius * 2, ball_radius * 2)

    def apply_force(self, force: Vec2d):
        self.apply_force_at_local_point(force, (0, 0))

    def increase_volume(self, amount):
        self.volume += amount
        new_radius = volume_to_radius(self.volume)
        self.mass = self.volume * self.local_density
        self.circle_base.unsafe_set_radius(new_radius)
        self._resize_sprite()

    def update(self, dt):
        self.velocity -= self.velocity * 0.9 * dt

    def draw(self, renderer: Renderer):
        renderer.draw_circle(
            (20, 20, 20, 100), self.position, self.circle_base.radius, 0)

        ball_pos = self.position - Vec2d(self.main_sprite.width / 2, self.main_sprite.height * 0.32)
        renderer.draw_texture(self.main_sprite, ball_pos, 0)
