import random
import pymunk
from pymunk import Vec2d
from enum import Enum

from engine.render import Renderer
from .animation import AnimatedSprite, AnimationState
from . import animation

class IceCube(pymunk.Circle):
    RADIUS = 20
    MASS = 10
    SPEED = 40
    
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
        
        self.input = Vec2d.zero()

        if IceCube.animation_state == None:
            back_sprites = AnimatedSprite(
                animation.load_textures("src/imgs/Ice Cubes", "Back", 8), 1 / 12)
            front_sprites = AnimatedSprite(
                animation.load_textures("src/imgs/Ice Cubes", "Front", 8), 1 / 12)
            left_textures = animation.load_textures("src/imgs/Ice Cubes", "Side", 8)
            left_sprites = AnimatedSprite(left_textures, 1 / 12)
            right_sprites = AnimatedSprite(left_textures, 1 / 12, flipped=True)
            
            IceCube.animation_state = AnimationState((self.STATE, self.DIRECTION))
            IceCube.animation_state.add_sprite(back_sprites, (self.State.WALKING, self.Direction.UP))
            IceCube.animation_state.add_sprite(front_sprites, (self.State.WALKING, self.Direction.DOWN))
            IceCube.animation_state.add_sprite(right_sprites, (self.State.WALKING, self.Direction.RIGHT))
            IceCube.animation_state.add_sprite(left_sprites, (self.State.WALKING, self.Direction.LEFT))

            IceCube.animation_state.set_state(self.STATE, self.State.WALKING)
            IceCube.animation_state.set_state(self.DIRECTION, self.Direction.DOWN)
        
        self.animation_state = IceCube.animation_state.get_copy()

        temp_sprite = front_sprites.textures[0]
        self.position_offset = Vec2d(temp_sprite.width / 2, 20)

        self.time = 0
        self.curr_direction = self.Direction.DOWN

    def update(self, dt):  
        if (self.time > random.random() * 2 + 4):
            self.curr_direction = random.choice(list(self.Direction))
            self.time = 0

        input = Vec2d.zero()
        if (self.curr_direction == self.Direction.UP):
            input += 0, 1
        elif (self.curr_direction == self.Direction.DOWN):
            input += 0, -1
        elif (self.curr_direction == self.Direction.RIGHT):
            input += 1, 0
        elif (self.curr_direction == self.Direction.LEFT):
            input += -1, 0
        self.body.velocity = input * self.SPEED

        self.animation_state.set_state(self.DIRECTION, self.curr_direction)
        self.animation_state.update(dt)

        self.time += dt
        
    def draw(self, renderer: Renderer):
        renderer.draw_circle((219, 241, 253), self.body.position, self.RADIUS)
        self.animation_state.get_sprite().draw(renderer, self.body.position, offset=-self.position_offset)