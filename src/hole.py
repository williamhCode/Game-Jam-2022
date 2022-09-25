import math
import pymunk
from pymunk import Vec2d
from enum import Enum

from engine.render import Renderer
from engine.texture import Texture
from .animation import AnimatedSprite, AnimationState
from . import funcs

class Hole(pymunk.Body):
    WIDTH = 120
    HEIGHT = 58

    MASS = 10

    poly: pymunk.Poly
    
    def __init__(self, pos: Vec2d):
        super().__init__(self.MASS, float('inf'), body_type=pymunk.Body.KINEMATIC)
        self.position = pos

        self.poly = pymunk.Poly(self, funcs.generate_ellipse_points(self.WIDTH, self.HEIGHT, 20))
        self.poly.friction = 0.5

        self.texture = Texture.from_path("src/imgs/Hole.png")
        self.position_offset = Vec2d(self.texture.width / 2, self.texture.height / 2)

    def update(self, dt):
        pass
    
    def draw(self, renderer: Renderer):
        renderer.draw_lines(
            (200, 20, 20), [v + self.position for v in self.poly.get_vertices()], 3)
        renderer.draw_texture(self.texture, self.position - self.position_offset)