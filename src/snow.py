from pymunk import Vec2d

import math
import random
from dataclasses import dataclass

from . import funcs
from engine.render import Renderer
from .snowball import Snowball
from .camera import Camera2D


@dataclass(slots=True)
class Box:
    pos: Vec2d
    size: int


@dataclass(slots=True)
class SnowTile:
    tex_id: int
    box: Box
    active: int = True


def circle_box_collision(center: Vec2d, radius, box: Box):
    box_center = box.pos + Vec2d(box.size / 2, box.size / 2)
    box_radius = box.size / 2

    return (center - box_center).length <= radius + box_radius


class SnowGrid:
    CELL_SIZE = 8
    INV_CELL_SIZE = 1 / CELL_SIZE

    def __init__(self, arena_size):
        self.width = int(arena_size[0] / self.CELL_SIZE)
        self.height = int(arena_size[1] / self.CELL_SIZE)

        num_snow_types = 8
        self.snow_textures = funcs.load_textures('src/imgs', 'Snow', num_snow_types)
        self.snow_tiles: list[list[SnowTile]] = [[0] * self.width for _ in range(self.width)]
        for x in range(self.width):
            for y in range(self.height):
                self.snow_tiles[x][y] = SnowTile(random.randint(
                    0, num_snow_types - 1), Box(Vec2d(x * self.CELL_SIZE, y * self.CELL_SIZE), 8))

    def update_snow(self, snowball: Snowball):
        circle = snowball.circle_base
        pos: Vec2d = snowball.position
        min_x = int(math.floor((pos.x - circle.radius) * self.INV_CELL_SIZE))
        max_x = int(math.floor((pos.x + circle.radius) * self.INV_CELL_SIZE))
        min_y = int(math.floor((pos.y - circle.radius) * self.INV_CELL_SIZE))
        max_y = int(math.floor((pos.y + circle.radius) * self.INV_CELL_SIZE))

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if x < 0 or x >= self.width or y < 0 or y >= self.height:
                    continue
                tile = self.snow_tiles[x][y]
                if tile.active and circle_box_collision(pos, circle.radius, tile.box):
                    tile.active = False
                    snowball.increase_volume(100)

    def draw(self, renderer: Renderer, camera: Camera2D):

        """
        var viewport = camera.GetViewport();
        int xStart = (int)Math.Floor(viewport.X / TILESIZE);
        int yStart = (int)Math.Floor(viewport.Y / TILESIZE);
        int xEnd = (int)Math.Ceiling((viewport.X + viewport.Width) / TILESIZE);
        int yEnd = (int)Math.Ceiling((viewport.Y + viewport.Height) / TILESIZE);

        xStart = Math.Max(xStart, 0);
        yStart = Math.Max(yStart, 0);
        xEnd = Math.Min(xEnd, WIDTH);
        yEnd = Math.Min(yEnd, HEIGHT);

        for (int row = xStart; row < xEnd; row++)
        {
            for (int col = yStart; col < yEnd; col++)
        """

        viewport = camera.get_viewport()
        x_start = int(math.floor(viewport.x / self.CELL_SIZE))
        y_start = int(math.floor(viewport.y / self.CELL_SIZE))
        x_end = int(math.ceil((viewport.x + viewport.width) / self.CELL_SIZE))
        y_end = int(math.ceil((viewport.y + viewport.height) / self.CELL_SIZE))

        x_start = max(x_start, 0)
        y_start = max(y_start, 0)
        x_end = min(x_end, self.width)
        y_end = min(y_end, self.height)

        for x in range(x_start, x_end):
            for y in range(y_start, y_end):
                curr_tile = self.snow_tiles[x][y]
                if curr_tile.active:
                    curr_tex = self.snow_textures[curr_tile.tex_id]
                    pos = (x * self.CELL_SIZE, y * self.CELL_SIZE)
                    renderer.draw_texture(curr_tex, pos)
