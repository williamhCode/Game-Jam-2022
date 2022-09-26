import math
import pymunk
from pymunk import Vec2d
from enum import Enum
import random
import pygame

from engine.render import Renderer
from .animation import AnimSprite, AnimState
from . import funcs
from .snowball import Snowball
from .constants import CollType

class JackOLantern(pymunk.Body):
    WIDTH = 50
    HEIGHT = 40
    MASS = 10
    
    STATE = "state"
    DIRECTION = "direction"
    
    class State(Enum):
        IDLE = 1
        WALKING = 2

    class Direction(Enum):
        UP = 1
        DOWN = 2
        RIGHT = 3
        LEFT = 4

    shape: pymunk.Poly

    animation_state = None
    position_offset = None
    
    def __init__(self, space: pymunk.Space, pos: Vec2d):
        super().__init__(self.MASS, float('inf'), body_type=pymunk.Body.KINEMATIC)
        self.position = pos

        self.shape = pymunk.Poly(self, funcs.generate_ellipse_points(self.WIDTH, self.HEIGHT, 20))
        self.shape.friction = 0.5
        space.add(self.shape, self)
        self.shape.collision_type = CollType.JACKOLANTERN.value

        self.base_position = pos
        self.time = 0
        
        self.input = Vec2d.zero()
        
        if JackOLantern.animation_state == None:
            left_textures = funcs.load_textures("src/imgs", "PumpSpin", 8)
            left_sprites = AnimSprite(left_textures, 1 / 12)

            JackOLantern.animation_state = AnimState((self.STATE, self.DIRECTION))
            JackOLantern.animation_state.add(left_sprites, (self.State.WALKING, self.Direction.LEFT))

        
            temp_sprite = left_sprites.textures[0]
            JackOLantern.position_offset = Vec2d(temp_sprite.width / 2, 45)

        self.animation_state = JackOLantern.animation_state.get_copy()
        self.position_offset = JackOLantern.position_offset

        self.animation_state.set_state(self.STATE, self.State.WALKING)
        self.animation_state.set_state(self.DIRECTION, self.Direction.LEFT)

        self.time = random.random() * 100
        self.curr_direction = self.Direction.LEFT

        handler = space.add_wildcard_collision_handler(self.shape.collision_type)
        handler.begin = self.on_collision

        self.hurt_sound = pygame.mixer.Sound("src/music/pumpkinhurtssnow.wav")

    def on_collision(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data):
        body = arbiter.shapes[1].body
        if isinstance(body, Snowball):
            body: Snowball
            body.apply_impulse(3000, self.position)
            body.change_volume(-23000)
            self.hurt_sound.play()

        return True

    def update(self, dt):
        self.time += dt
        x = math.cos(self.time * 2) * 100
        y = math.sin(self.time * 2) * 100
        self.position = Vec2d(x, y) + Vec2d(*self.base_position)
        self.animation_state.set_state(self.DIRECTION, self.curr_direction)
        self.animation_state.update(dt)

    def draw(self, renderer: Renderer):
        # renderer.draw_lines(
        #     (200, 20, 20), [v + self.position for v in self.shape.get_vertices()], 3)
        self.animation_state.get_sprite().draw(renderer, self.position, offset=-self.position_offset)
        
