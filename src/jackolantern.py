import math
import pymunk
from pymunk import Vec2d
from enum import Enum

from engine.render import Renderer
from .animation import AnimatedSprite, AnimationState
from . import animation

class JackOLantern(pymunk.Circle):
    RADIUS = 20
    MASS = 10
    
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

    animation_state = None
    
    def __init__(self, pos: Vec2d):
        body = pymunk.Body(self.MASS, float('inf'), body_type=pymunk.Body.KINEMATIC)
        body.position = pos

        super().__init__(body, self.RADIUS)
        self.friction = 0.5

        self.base_position = pos
        self.time = 0
        
        self.input = Vec2d.zero()
        
        if JackOLantern.animation_state == None:
            left_textures = animation.load_textures("src/imgs", "PumpSpin", 8)
            left_sprites = AnimatedSprite(left_textures, 1 / 12)

            JackOLantern.animation_state = AnimationState((self.STATE, self.DIRECTION))
            JackOLantern.animation_state.add_sprite(left_sprites, (self.State.WALKING, self.Direction.LEFT))

            JackOLantern.animation_state.set_state(self.STATE, self.State.WALKING)
            JackOLantern.animation_state.set_state(self.DIRECTION, self.Direction.LEFT)
        
        self.animation_state = JackOLantern.animation_state.get_copy()

        temp_sprite = left_sprites.textures[0]
        self.position_offset = Vec2d(temp_sprite.width / 2, 20)

        self.time = 0
        self.curr_direction = self.Direction.LEFT

    def update(self, dt):
        self.time += dt
        x = math.cos(self.time) * 10 
        y = math.sin(self.time) * 10
        self.body.position = Vec2d(x, y) + Vec2d(*self.base_position)
        self.animation_state.set_state(self.DIRECTION, self.curr_direction)
        self.animation_state.update(dt)
    
    def draw(self, renderer: Renderer):
        renderer.draw_circle((255, 140, 0), self.body.position, self.RADIUS)
        self.animation_state.get_sprite().draw(renderer, self.body.position, offset=-self.position_offset)