import pygame
import pymunk

import math
import time
import random

import engine
from engine.render import Renderer
from engine.texture import Texture

from src.camera import Camera2D
from src.snowball import Snowball
from src.player import Player
from src.jackolantern import JackOLantern
from src.icecube import IceCube
from src.hole import Hole
from src.snow import SnowGrid


def main():
    # initialize -------------------------------------------------- #
    pygame.init()

    # specify opengl version
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 4)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 1)
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

    # create window
    WIN_SIZE = (1280, 720)
    pygame.display.set_mode((WIN_SIZE), pygame.DOUBLEBUF | pygame.OPENGL)

    renderer = Renderer()
    # renderer.set_clear_color((100, 100, 100, 255))
    renderer.set_clear_color((200, 200, 200, 255))

    renderer.set_size(*WIN_SIZE)

    camera = Camera2D(*WIN_SIZE)

    # game objects init ---------------------------------------- #
    ARENA_SIZE = (3840, 2160)

    grass_size = 64
    GRASS_DIM = (int(ARENA_SIZE[0] / grass_size), int(ARENA_SIZE[1] / grass_size))
    grass_texture = Texture.from_path('src/imgs/Grass.png')

    snow_grid = SnowGrid(ARENA_SIZE)

    space = pymunk.Space()
    space.collision_bias = (1.0 - 0.5) ** 60

    snowball = Snowball((100, 100), 5, 0.05)
    space.add(snowball.circle_base, snowball)
    player = Player((50, 0))
    space.add(player.poly, player)

    jackolantern = JackOLantern((800, 600))
    space.add(jackolantern.circle, jackolantern)
    icecube = IceCube((300, 300))
    space.add(icecube.circle, icecube)
    hole = Hole((500, 500))
    space.add(hole.poly, hole)

    font = pygame.font.SysFont('Comic Sans MS', 30)

    # game loop -------------------------------------------------- #
    clock = engine.timer.Timer()

    running = True
    while running:
        # timing -------------------------------------------------- #
        dt = clock.tick()

        framerate = clock.get_fps()
        pygame.display.set_caption(f"Running at {framerate :.2f} fps.")

        # check events -------------------------------------------------- #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # update -------------------------------------------------- #
        keys = pygame.key.get_pressed()

        input = pymunk.Vec2d.zero()
        if keys[pygame.K_UP]:
            input += 0, 1
        if keys[pygame.K_DOWN]:
            input -= 0, 1
        if keys[pygame.K_RIGHT]:
            input += 1, 0
        if keys[pygame.K_LEFT]:
            input -= 1, 0

        player.move(input)
        player.update(dt)

        camera.look_at(player.position)

        snowball.update(dt)
        snow_grid.update_snow(snowball)
        jackolantern.update(dt)
        icecube.update(dt)
        hole.update(dt)

        iterations = 5
        for _ in range(iterations):
            space.step(dt / iterations)

        # blit -------------------------------------------------- #
        # surf = font.render('stuff', False, (0, 0, 0))
        # font_texture = Texture.from_pygame_surface(surf)

        renderer.begin(camera.get_transform())
        renderer.clear()

        # render grass
        for x in range(GRASS_DIM[0]):
            for y in range(GRASS_DIM[1]):
                pos = (x * grass_size, y * grass_size)
                renderer.draw_texture(grass_texture, pos)
        
        snow_grid.draw(renderer, camera)

        hole.draw(renderer)

        player.draw(renderer)
        snowball.draw(renderer)
        jackolantern.draw(renderer)
        icecube.draw(renderer)

        renderer.end()

        # flip screen
        pygame.display.flip()


if __name__ == "__main__":
    main()
    pygame.quit()
