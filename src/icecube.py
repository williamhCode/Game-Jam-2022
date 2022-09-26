import random
import pymunk
from pymunk import Vec2d
from enum import Enum

from engine.render import Renderer
from .animation import AnimSprite, AnimState
from . import funcs
from .snowball import Snowball
from .constants import CollType


class IceCube(pymunk.Body):
    MASS = 10
    SPEED = 40

    WIDTH = 42
    HEIGHT = 32
    
    STATE = "state"
    DIRECTION = "direction"
    
    class State(Enum):
        WALKING = 1

    class Direction(Enum):
        UP = 1
        DOWN = 2
        RIGHT = 3
        LEFT = 4

    shape: pymunk.Circle
    animation_state = None
    position_offset = None
    
    def __init__(self, space: pymunk.Space, pos: Vec2d, coll_value):
        super().__init__(self.MASS, float('inf'), body_type=pymunk.Body.DYNAMIC)
        self.position = pos
        self.shape = pymunk.Poly(self, funcs.generate_ellipse_points(self.WIDTH, self.HEIGHT, 20))
        self.shape.friction = 0.5
        space.add(self.shape, self)
        self.shape.collision_type = CollType.ICE_CUBE.value + coll_value

        self.base_position = pos
        
        self.input = Vec2d.zero()

        if IceCube.animation_state == None:
            back_sprites = AnimSprite(
                funcs.load_textures("src/imgs/IceCubes", "Back", 8), 1 / 12)
            front_sprites = AnimSprite(
                funcs.load_textures("src/imgs/IceCubes", "Front", 8), 1 / 12)
            left_textures = funcs.load_textures("src/imgs/IceCubes", "Side", 8)
            left_sprites = AnimSprite(left_textures, 1 / 12)
            right_sprites = AnimSprite(left_textures, 1 / 12, flipped=True)
            
            IceCube.animation_state = AnimState((self.STATE, self.DIRECTION))
            IceCube.animation_state.add(back_sprites, (self.State.WALKING, self.Direction.UP))
            IceCube.animation_state.add(front_sprites, (self.State.WALKING, self.Direction.DOWN))
            IceCube.animation_state.add(right_sprites, (self.State.WALKING, self.Direction.RIGHT))
            IceCube.animation_state.add(left_sprites, (self.State.WALKING, self.Direction.LEFT))

            temp_sprite = front_sprites.textures[0]
            IceCube.position_offset = Vec2d(temp_sprite.width / 2, 45)
        
        self.animation_state = IceCube.animation_state.get_copy()

        self.animation_state.set_state(self.STATE, self.State.WALKING)
        self.animation_state.set_state(self.DIRECTION, self.Direction.DOWN)

        self.position_offset = IceCube.position_offset

        self.time = 0
        self.curr_direction = self.Direction.DOWN

        self.is_dead = False

        handler = space.add_wildcard_collision_handler(self.shape.collision_type)
        handler.begin = self.on_collision
    
    def on_collision(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data):
        body = arbiter.shapes[1].body
        if isinstance(body, Snowball):
            body: Snowball
            body.freeze()
            self.is_dead = True
            space.remove(self.shape, self)

        return True

    def kill(self, space):
        space.remove(self.shape, self)
        self.is_dead = True

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
        self.velocity = input * self.SPEED

        self.animation_state.set_state(self.DIRECTION, self.curr_direction)
        self.animation_state.update(dt)

        self.time += dt
        
    def draw(self, renderer: Renderer):
        # renderer.draw_lines(
        #     (200, 20, 20), [v + self.position for v in self.shape.get_vertices()], 3)
        self.animation_state.get_sprite().draw(renderer, self.position, offset=-self.position_offset)
