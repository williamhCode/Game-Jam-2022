from pathlib import Path
from engine.texture import Texture
import math


def load_textures(base_path: str, name: str, count):
    textures: list[Texture] = []
    for i in range(count):
        filename = name + str(i).zfill(4) + ".png"
        path = Path.joinpath(Path(base_path).resolve(), name, filename)
        textures.append(Texture.from_path(path))

    return textures


def generate_ellipse_points(radius_x, radius_y, num_points):
    points = []
    for i in range(num_points):
        angle = i * (2 * math.pi / num_points)
        x = radius_x * math.cos(angle)
        y = radius_y * math.sin(angle)
        points.append((x, y))

    return points
