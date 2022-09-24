from pymunk import Vec2d
import random
from . import animation
from engine.render import Renderer
from .snowball import Snowball

from dataclasses import dataclass


@dataclass(slots=True)
class Box:
    pos: Vec2d
    size: int


@dataclass(slots=True)
class SnowTile:
    tex_id: int
    box: Box
    active: int = True
    

def circle_aabb_coll(center: Vec2d, radius, pos: Vec2d, width, height):
    aabb_center = pos + Vec2d(width / 2, height / 2)
    distance = pos - center


class SnowGrid:
    CELL_SIZE = 64
    INV_CELL_SIZE = 1 / CELL_SIZE

    def __init__(self, arena_size):
        self.snow_size = 8
        self.snow_dim = (int(arena_size[0] / self.snow_size), int(arena_size[1] / self.snow_size))
        num_snow_types = 8
        self.snow_textures = animation.load_textures('src/imgs', 'Snow', num_snow_types)
        self.snow_tiles: list[list[SnowTile]] = [[0] * self.snow_dim[0] for _ in range(self.snow_dim[0])]
        for x in range(self.snow_dim[0]):
            for y in range(self.snow_dim[1]):
                self.snow_tiles[x][y] = SnowTile(random.randint(0, num_snow_types - 1), Box(Vec2d(x, y), 8))

        self.width = int(arena_size[0] / self.CELL_SIZE)
        self.height = int(arena_size[1] / self.CELL_SIZE)
        self.hash_table = [0] * self.width * self.height
        for i in range(len(self.hash_table)):
            self.hash_table[i] = []

    def _position_to_key(self, pos: Vec2d):
        key = int(pos.x * self.INV_CELL_SIZE) + int(pos.y * self.INV_CELL_SIZE) * self.width
        return key

    def _key_to_position(self, key):
        x_pos = key % self.width
        y_pos = key // self.width
        return (x_pos, y_pos)

    def update_snow(self, snowball: Snowball):
        pass

    def draw(self, renderer: Renderer):
        for x in range(self.snow_dim[0]):
            for y in range(self.snow_dim[1]):
                curr_tile = self.snow_tiles[x][y]
                if curr_tile.active:
                    curr_tex = self.snow_textures[curr_tile.tex_id]
                    pos = (x * self.snow_size, y * self.snow_size)
                    renderer.draw_texture(curr_tex, pos)