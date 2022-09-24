import pygame
import math
import pymunk

import engine
from engine.render import Renderer
from engine.texture import Texture

from src.snowball import Snowball
from src.player import Player


def main():
    # initialize -------------------------------------------------- #
    pygame.init()

    # specify opengl version
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 4)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 1)
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

    # create window
    WIN_SIZE = (720, 480)
    pygame.display.set_mode((WIN_SIZE), pygame.DOUBLEBUF | pygame.OPENGL)

    renderer = Renderer()
    renderer.set_clear_color((100, 100, 100, 255))

    renderer.set_size(*WIN_SIZE)

    # game objects init ---------------------------------------- #
    space = pymunk.Space()

    snowball = Snowball((100, 100), 50, 50)
    space.add(snowball, snowball.body)
    player = Player((50, 0))
    space.add(player, player.body)

    # game loop -------------------------------------------------- #
    clock = engine.timer.Timer()

    running = True
    while running:
        # timing -------------------------------------------------- #
        dt = clock.tick(60)

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

        space.step(dt)

        # blit -------------------------------------------------- #
        renderer.begin()
        renderer.clear()

        snowball.draw(renderer)
        player.draw(renderer)

        renderer.end()

        # flip screen
        pygame.display.flip()


if __name__ == "__main__":
    main()
    pygame.quit()
