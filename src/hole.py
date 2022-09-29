import math
import pymunk
from pymunk import Vec2d
from enum import Enum

from engine.render import Renderer
from engine.texture import Texture
from .player import Player
from . import funcs
from .constants import CollType

class Hole(pymunk.Body):
    WIDTH = 120
    HEIGHT = 58

    MASS = 10

    shape: pymunk.Poly
    
    def __init__(self, space: pymunk.Space, pos: Vec2d):
        super().__init__(self.MASS, float('inf'), body_type=pymunk.Body.KINEMATIC)
        self.position = pos
        self.shape = pymunk.Poly(self, funcs.generate_ellipse_points(self.WIDTH, self.HEIGHT, 20))
        self.shape.friction = 0.5
        space.add(self.shape, self)
        self.shape.collision_type = CollType.HOLE.value

        self.texture = Texture.from_path("src/imgs/Hole.png")
        self.position_offset = Vec2d(self.texture.width / 2, self.texture.height / 2)

        handler = space.add_wildcard_collision_handler(self.shape.collision_type)
        handler.begin = self.on_collision

    def on_collision(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data):
        shape = arbiter.shapes[1]
        if shape.collision_type != CollType.PLAYER_PUNT.value:
            body = shape.body
            body.kill(space)

        return True

    def update(self, dt):
        pass
    
    def draw(self, renderer: Renderer):
        # renderer.draw_lines(
        #     (200, 20, 20), [v + self.position for v in self.shape.get_vertices()], 3)
        renderer.draw_texture(self.texture, self.position - self.position_offset)
