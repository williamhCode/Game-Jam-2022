import math
import pymunk
from pymunk import Vec2d
from enum import Enum

from engine.render import Renderer
from .constants import CollType
from engine.texture import Texture


class Wall(pymunk.Body):
    SIZE = 128
    
    sprite = None

    shape: pymunk.Poly
    # position_offset = None
    
    def __init__(self, space: pymunk.Space, pos: Vec2d):
        super().__init__(0, float('inf'), body_type=pymunk.Body.STATIC)
        self.position = pos

        self.shape = pymunk.Poly.create_box(self, (self.SIZE, self.SIZE))
        self.shape.friction = 0.5
        self.shape.elasticity = 1.0
        space.add(self.shape, self)
        self.shape.collision_type = CollType.WALL.value

        if Wall.sprite == None:
            Wall.sprite = Texture.from_path("src/imgs/Block.png")
            Wall.position_offset = Vec2d(Wall.sprite.width / 2, 64)

        self.texture = Wall.sprite

    def update(self, dt):
        pass

    def draw(self, renderer: Renderer):
        # renderer.draw_lines(
        #     (200, 20, 20), [v + self.position for v in self.shape.get_vertices()], 3)
        renderer.draw_texture(self.texture, self.position - Wall.position_offset)
        