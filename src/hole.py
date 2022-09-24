import math
import pymunk
from pymunk import Vec2d
from enum import Enum

from engine.render import Renderer
from engine.texture import Texture
from .animation import AnimatedSprite, AnimationState
from . import animation

class Hole(pymunk.Circle):
    RADIUS = 10
    MASS = 10

    body: pymunk.Body
    
    def __init__(self, pos: Vec2d):
        body = pymunk.Body(self.MASS, float('inf'), body_type=pymunk.Body.KINEMATIC)
        body.position = pos

        super().__init__(body, self.RADIUS)
        self.friction = 0.5

        self.texture = Texture.from_path("src/imgs/Hole.png")
        self.position_offset = Vec2d(self.texture.width / 2, self.texture.height / 2)

    def update(self, dt):
        pass
    
    def draw(self, renderer: Renderer):
        # renderer.draw_circle((160, 32, 240), self.body.position, self.RADIUS)
        renderer.draw_texture(self.texture, self.body.position - self.position_offset)