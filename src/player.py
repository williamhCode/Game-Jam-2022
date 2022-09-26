import pymunk
from pymunk import Vec2d
from enum import Enum
import math
from dataclasses import dataclass
import pygame

from engine.render import Renderer
from engine.texture import Texture
from .animation import AnimSprite, AnimState
from . import funcs
from .constants import CollType
from . import snowball


def move_towards(curr: Vec2d, target: Vec2d, force: float):
    diff = target - curr
    change = diff.normalized() * force
    # clamp value based to the difference
    change = diff if diff.get_length_sqrd() < change.get_length_sqrd() else change
    return curr + change


class Player(pymunk.Body):
    MAX_SPEED = 200
    ACCELERATION = 1000
    FRICTION = 2000

    MASS = 10
    WIDTH = 28
    HEIGHT = 20

    MAX_CHARGE_TIME = 20

    STATE = "state"
    DIR = "direction"

    class State(Enum):
        IDLE = 1
        WALKING = 2
        PUNTING = 3
        CHARGING = 4

    class Dir(Enum):
        UP = 1
        DOWN = 2
        RIGHT = 3
        LEFT = 4

    shape: pymunk.Poly

    def __init__(self, space: pymunk.Space, pos):
        super().__init__(self.MASS, float('inf'), body_type=pymunk.Body.DYNAMIC)
        self.position = pos
        self.shape = pymunk.Poly(self, funcs.generate_ellipse_points(self.WIDTH, self.HEIGHT, 20))
        self.shape.friction = 2.0
        self.shape.elasticity = 0.0

        # variables
        self.move_vec = Vec2d.zero()

        # sprites
        self.anim_state = AnimState((self.STATE, self.DIR))

        back_sprites = AnimSprite(funcs.load_textures("src/imgs/Player", "Back", 8), 1 / 12)
        front_sprites = AnimSprite(funcs.load_textures("src/imgs/Player", "Front", 8), 1 / 12)
        right_textures = funcs.load_textures("src/imgs/Player", "Side", 8)
        right_sprites = AnimSprite(right_textures, 1 / 12)
        left_sprites = AnimSprite(right_textures, 1 / 12, flipped=True)
        self.anim_state.add(back_sprites, (self.State.WALKING, self.Dir.UP))
        self.anim_state.add(front_sprites, (self.State.WALKING, self.Dir.DOWN))
        self.anim_state.add(right_sprites, (self.State.WALKING, self.Dir.RIGHT))
        self.anim_state.add(left_sprites, (self.State.WALKING, self.Dir.LEFT))

        pback_textures = funcs.load_textures("src/imgs/Player", "PuntBack", 8)
        pback_sprites = AnimSprite(pback_textures, 1 / 12)
        pfront_textures = funcs.load_textures("src/imgs/Player", "PuntFront", 8)
        pfront_sprites = AnimSprite(pfront_textures, 1 / 12)
        pright_textures = funcs.load_textures("src/imgs/Player", "PuntSide", 8)
        pright_sprites = AnimSprite(pright_textures, 1 / 12)
        pleft_sprites = AnimSprite(pright_textures, 1 / 12, flipped=True)
        self.anim_state.add(pback_sprites, (self.State.PUNTING, self.Dir.UP))
        self.anim_state.add(pfront_sprites, (self.State.PUNTING, self.Dir.DOWN))
        self.anim_state.add(pright_sprites, (self.State.PUNTING, self.Dir.RIGHT))
        self.anim_state.add(pleft_sprites, (self.State.PUNTING, self.Dir.LEFT))

        self.anim_state.add(AnimSprite(pback_textures[0:1], 1), (self.State.CHARGING, self.Dir.UP))
        self.anim_state.add(AnimSprite(pfront_textures[0:1], 1), (self.State.CHARGING, self.Dir.DOWN))
        self.anim_state.add(AnimSprite(pright_textures[0:1], 1), (self.State.CHARGING, self.Dir.RIGHT))
        self.anim_state.add(AnimSprite(pright_textures[0:1], 1, flipped=True), (self.State.CHARGING, self.Dir.LEFT))

        iback_textures = [Texture.from_path("src/imgs/Player/IdleBack.png")]
        ifront_textures = [Texture.from_path("src/imgs/Player/IdleFront.png")]
        iside_textures = [Texture.from_path("src/imgs/Player/IdleSide.png")]
        self.anim_state.add(AnimSprite(iback_textures, 1), (self.State.IDLE, self.Dir.UP))
        self.anim_state.add(AnimSprite(ifront_textures, 1), (self.State.IDLE, self.Dir.DOWN))
        self.anim_state.add(AnimSprite(iside_textures, 1), (self.State.IDLE, self.Dir.RIGHT))
        self.anim_state.add(AnimSprite(iside_textures, 1, flipped=True), (self.State.IDLE, self.Dir.LEFT))

        # ---------------- #
        self.anim_state.set_state(self.STATE, self.State.WALKING)
        self.anim_state.set_state(self.DIR, self.Dir.DOWN)

        temp_sprite = front_sprites.textures[0]
        self.position_offset = Vec2d(temp_sprite.width / 2, 52)

        # ---------------- #
        self.punt_sound = pygame.mixer.Sound("src/music/playerpunt.wav")
        self.push_sound = pygame.mixer.Sound("src/music/snowpush.wav")

        # ---------------- #
        self.charging = False
        self.charge_time = 0
        self.punting = False
        self.punt_time = 0
        self.is_hitting = False
        self.has_hit = False
        self.prev_trigger = False
        
        self.punt_shape = pymunk.Circle(self, 50)
        space.add(self.shape, self.punt_shape, self)
        self.shape.collision_type = CollType.PLAYER.value
        self.punt_shape.collision_type = CollType.PLAYER_PUNT.value

        handler = space.add_wildcard_collision_handler(self.punt_shape.collision_type)
        handler.begin = self.on_collision
        handler.separate = self.on_separate
        self.is_touching_snowball = False
        self.snowball_ref = None

        self.is_dead = False

    def on_collision(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data):
        body = arbiter.shapes[1].body
        if isinstance(body, snowball.Snowball):
            body: snowball.Snowball
            self.snowball_ref = body
            self.is_touching_snowball = True

        return False

    def on_separate(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data):
        body = arbiter.shapes[1].body
        if isinstance(body, snowball.Snowball):
            body: snowball.Snowball
            self.is_touching_snowball = False

    def _reset_punting(self):
        self.punting = False
        self.punt_time = 0
        self.charge_time = 0
        self.charging = False
        self.anim_state.set_state(self.STATE, self.State.WALKING)

    def input(self, move: Vec2d, trigger: bool):
        self.move_vec = Vec2d.zero()

        if trigger and not self.prev_trigger:
            self._reset_punting()
            self.charging = True
            self.anim_state.set_state(self.STATE, self.State.CHARGING)
        elif not trigger and self.charging:
            self.punt_sound.play()
            self.has_hit = False
            dir = self.anim_state.get_state(self.DIR)
            offsets = (
                Vec2d(0, 1),
                Vec2d(0, -0.5),
                Vec2d(1, 0),
                Vec2d(-1, 0)
            )
            self.punt_shape.unsafe_set_offset(offsets[dir.value - 1] * 80)
            self.charging = False
            self.punting = True
            self.anim_state.set_state(self.STATE, self.State.PUNTING)
        elif not self.charging and not self.punting:
            self.move_vec = move.normalized()

        self.prev_trigger = trigger

    def _apply_input(self, dt):
        if self.move_vec == Vec2d.zero():
            self.velocity = move_towards(self.velocity, Vec2d.zero(), self.FRICTION * dt)
        else:
            self.velocity = move_towards(
                self.velocity, self.move_vec * self.MAX_SPEED, self.ACCELERATION * dt)

    def _hit_snowball(self, dt):
        if self.is_touching_snowball and self.is_hitting:
            impulse = self.charge_time * 12000 + 2000
            if self.snowball_ref.is_frozen:
                self.snowball_ref.unfreeze(impulse)
            else: 
                self.snowball_ref.apply_impulse(impulse, self.position)
            self.is_hitting = False
            self.has_hit = True

    def kill(self, space: pymunk.Space):
        space.remove(self.shape, self.punt_shape, self)
        self.is_dead = True

    def update(self, dt):
        if self.charging:
            self.charge_time += dt
            if self.charge_time > self.MAX_CHARGE_TIME:
                self.charge_time = self.MAX_CHARGE_TIME
        elif self.punting:
            self.punt_time += dt
            if self.punt_time >= 1 / 12 and self.punt_time < 6 / 12 and not self.has_hit:
                self.is_hitting = True
            else:
                self.is_hitting = False
            if self.punt_time > 8 / 12:
                self.punt_time = 0
                self.punting = False
                self.anim_state.set_state(self.STATE, self.State.WALKING)
        else:
            if self.move_vec.y == 1:
                self.anim_state.set_state(self.DIR, self.Dir.UP)
            elif self.move_vec.y == -1:
                self.anim_state.set_state(self.DIR, self.Dir.DOWN)
            elif self.move_vec.x == 1:
                self.anim_state.set_state(self.DIR, self.Dir.RIGHT)
            elif self.move_vec.x == -1:
                self.anim_state.set_state(self.DIR, self.Dir.LEFT)

            if self.move_vec != Vec2d.zero():
                self.anim_state.set_state(self.STATE, self.State.WALKING)
            else:
                self.anim_state.set_state(self.STATE, self.State.IDLE)

        self._apply_input(dt)
        self._hit_snowball(dt)
        self.position += self.velocity * dt
        self.anim_state.update(dt)

    def draw(self, renderer: Renderer):
        # renderer.draw_lines(
        #     (200, 20, 20), [v + self.position for v in self.shape.get_vertices()], 3)
        # if self.is_hitting:
        # renderer.draw_circle((200, 20, 20), self.position + self.punt_shape.offset, self.punt_shape.radius, 3)

        self.anim_state.get_sprite().draw(renderer, self.position, offset=-self.position_offset)

