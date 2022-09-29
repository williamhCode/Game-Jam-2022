from __future__ import annotations
from engine.render import Renderer
from engine.texture import Texture
from . import funcs
from .constants import CollType

import pymunk
from pymunk import Vec2d
import math
import pygame


def radius_to_volume(radius):
    return (4 / 3) * math.pi * radius ** 3


def volume_to_radius(volume):
    return (3 * volume / (4 * math.pi)) ** (1 / 3)


class Snowball(pymunk.Body):
    sprites = None

    shape: pymunk.Circle

    def __init__(self, space: pymunk.Space, pos, radius, mass):
        super().__init__(mass, float('inf'), body_type=pymunk.Body.DYNAMIC)
        self.position = pos

        self.shape = pymunk.Circle(self, radius)
        self.shape.friction = 2.0
        self.shape.elasticity = 0.5
        space.add(self.shape, self)
        self.shape.collision_type = CollType.SNOWBALL.value

        self.init_radius = radius
        self.volume = radius_to_volume(radius)
        self.local_density = mass / self.volume

        if Snowball.sprites == None:
            Snowball.sprites = funcs.load_textures("src/imgs", "SnowBall", 3)

        self.sprites = Snowball.sprites

        self.main_sprite = self.sprites[0]
        self.frozen_sprite = self.sprites[2]
        self._resize_sprite()

        self.is_frozen = False
        self.freeze_hitpoints = 0

        self.is_dead = False

        self.freeze_sound = pygame.mixer.Sound("src/music/icecubefreezesball.wav")

    def _resize_sprite(self):
        ball_radius = self.shape.radius * 1.4
        for sprite in self.sprites:
            sprite.resize(ball_radius * 2, ball_radius * 2)

    def apply_impulse(self, impulse: float, position: Vec2d):
        direction = (self.position - position).normalized()
        self.apply_impulse_at_local_point(direction * impulse, (0, 0))
        if self.velocity.length > 1500:
            self.velocity = self.velocity.normalized() * 1500

    def unfreeze(self, hitpoints):
        self.freeze_hitpoints -= hitpoints
        if self.freeze_hitpoints <= 0:
            self.is_frozen = False
            self.freeze_hitpoints = 0

    def freeze(self):
        self.freeze_sound.play()
        self.is_frozen = True
        self.velocity = Vec2d.zero()
        self.freeze_hitpoints = 15000

    def change_volume(self, amount):
        self.volume += amount
        if self.volume < 0:
            self.volume = radius_to_volume(self.init_radius)
        new_radius = volume_to_radius(self.volume)
        self.mass = self.volume * self.local_density
        self.shape.unsafe_set_radius(new_radius)
        self._resize_sprite()

    def kill(self, space: pymunk.Space):
        space.remove(self.shape, self) 
        self.is_dead = True
        
    def update(self, dt):
        if self.is_frozen:
            self.velocity = Vec2d.zero()
        else:
            self.velocity -= self.velocity * 0.9 * dt

    def draw(self, renderer: Renderer):
        renderer.draw_circle(
            (20, 20, 20, 100), self.position, self.shape.radius, 0)

        ball_pos = self.position - Vec2d(self.main_sprite.width / 2, self.main_sprite.height * 0.32)
        if self.is_frozen:
            renderer.draw_texture(self.frozen_sprite, ball_pos, color=(255, 255, 255, 400))
        else:
            renderer.draw_texture(self.main_sprite, ball_pos)
