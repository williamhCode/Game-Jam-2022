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
from src.wall import Wall

def reset_level():
    global snow_grid, space, snowball, player, jackolanterns, icecubes, holes, objects

    ARENA_SIZE = (3840, 2160)
    snow_grid = SnowGrid(ARENA_SIZE)

    space = pymunk.Space()
    space.collision_bias = (1.0 - 0.5) ** 60

    snowball = Snowball(space, (1920, 1080), 5, 0.05)
    player = Player(space, (1920, 1080 - 50))

    jackolanterns = [
        JackOLantern(space, (600, 500)),
        JackOLantern(space, (2600, 450)),
        JackOLantern(space, (3300, 700)),
        JackOLantern(space, (2000, 2000))
    ]

    icecubes = []
    for x in range(15):
        pos = (random.randint(0, 3840), random.randint(0, 2160))
        icecubes.append(IceCube(space, pos, x))

    holes = [
        Hole(space, (400, 1200)),
        Hole(space, (3400, 1500)),
    ]

    objects = [snowball, player] + jackolanterns + icecubes 
    
    for x in range(6):
        pos = (128 * (9 + x) - 64, 2160 - 128 * 3 - 64)
        objects.append(Wall(space, pos))
    for x in range(6):
        pos = (128 * (9 + x) - 64, 128 * 2 - 64)
        objects.append(Wall(space, pos))
    for x in range(4):
        pos = (128 * (12 + x) - 64, 2160 - 128 * 6 - 64)
        objects.append(Wall(space, pos))
    for x in range(4):
        pos = (128 * (17 + x) - 64, 2160 - 128 * 6 - 64)
        objects.append(Wall(space, pos))
    for x in range(4):
        pos = (128 * (12 + x) - 64, 128 * 5 - 64)
        objects.append(Wall(space, pos))
    for x in range(7):
        pos = (128 * (24 + x) - 64, 128 * 10 - 64)
        objects.append(Wall(space, pos))
    for x in range(6):
        pos = (128 * (25 + x) - 64, 128 * 14 - 64)
        objects.append(Wall(space, pos))
    for y in range(3):
        pos = (128 * 9 - 64, 2160 - 128 * (y + 4) - 64)
        objects.append(Wall(space, pos))
    for y in range(3):
        pos = (128 * 9 - 64, 128 * (y + 3) - 64)
        objects.append(Wall(space, pos))
    objects.append(Wall(space, (128 * 12 - 64, 128 * 10 - 64)))
    objects.append(Wall(space, (128 * 12 - 64, 128 * 6 - 64)))
        

    for i in range(3840 // 128 + 2):
        pos = (i * 128 - 64, -64)
        objects.append(Wall(space, pos))
    for i in range(3840 // 128 + 2):
        pos = (i * 128 - 64, 2160 + 64)
        objects.append(Wall(space, pos))
    for j in range(2160 // 128 + 2):
        pos = (-64, j * 128 - 64)
        objects.append(Wall(space, pos))
    for j in range(2160 // 128 + 2):
        pos = (3840 + 64, j * 128 - 64)
        objects.append(Wall(space, pos))

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
    pygame.display.set_mode((WIN_SIZE), pygame.DOUBLEBUF | pygame.OPENGL, vsync=1)

    renderer = Renderer()
    renderer.set_clear_color((200, 200, 200, 255))

    renderer.set_size(*WIN_SIZE)

    camera = Camera2D(*WIN_SIZE)
    camera.zoom = 1

    # 0 = start screen, 1 = game, 2 = end screen 
    mode = 0
    time = 0

    # start screen init ---------------------------------------- #
    title_gui_texture = Texture.from_path('src/imgs/TitleGui.png')
    title_nogui_texture = Texture.from_path('src/imgs/TitleNoGui.png')

    # end screen init ------------------------------------------ #
    end_texture = Texture.from_path('src/imgs/End.png')
    snowball_texture = Texture.from_path('src/imgs/Snowball/SnowBall0000.png')
    snowball_texture.resize(snowball_texture.width * 2, snowball_texture.height * 2)

    # game objects init ---------------------------------------- #
    timer_window_texture = Texture.from_path('src/imgs/TimerWindow.png')
    timer_window_texture.resize(timer_window_texture.width * 0.5, timer_window_texture.height * 0.5)

    reset_level()

    # grass_size = 64
    # GRASS_DIM = (int(ARENA_SIZE[0] / grass_size), int(ARENA_SIZE[1] / grass_size))
    # grass_texture = Texture.from_path('src/imgs/Grass.png')

    ground_texture = Texture.from_path('src/imgs/Ground.png')

    pygame.mixer.music.load('src/music/LevelMusic.wav')
    end_sound = pygame.mixer.Sound('src/music/endsound.wav')

    font = pygame.font.SysFont('Comic Sans MS', 30)
    font_big = pygame.font.SysFont('Comic Sans MS', 50)

    # game loop -------------------------------------------------- #
    clock = engine.timer.Timer()
    score = 0

    pygame.display.set_caption("Snowball Shovler")
    pygame.display.set_icon(pygame.image.load('src/imgs/Icon.png'))

    running = True
    while running:
        # timing -------------------------------------------------- #
        dt = clock.tick()

        # framerate = clock.get_fps()

        # check events -------------------------------------------------- #
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_RETURN:
                    if mode == 0:
                        mode = 1
                        time = 0
                        pygame.mixer.music.play(loops=-1)
                    elif mode == 2:
                        mode = 0
                        reset_level()

        if mode == 0:
            renderer.begin()
            renderer.clear()
            renderer.draw_texture(title_nogui_texture, (0, 0))
            renderer.draw_texture(title_gui_texture, (0, 0))
            renderer.end()
        elif mode == 1:
            time += dt
            if time > 60 * 3 or player.is_dead or snowball.is_dead:
                mode = 2
                time = 0
                pygame.mixer.music.stop()
                score = snowball.volume / 1000
                end_sound.play()
                snowball.position = (640, 280 + snowball.shape.radius)
                snowball.velocity = (0, 0)

            # update -------------------------------------------------- #
            keys = pygame.key.get_pressed()

            move_vec = pymunk.Vec2d.zero()
            if keys[pygame.K_UP]:
                move_vec += 0, 1
            if keys[pygame.K_DOWN]:
                move_vec -= 0, 1
            if keys[pygame.K_RIGHT]:
                move_vec += 1, 0
            if keys[pygame.K_LEFT]:
                move_vec -= 1, 0
            
            punt = keys[pygame.K_SPACE]

            player.input(move_vec, punt)
            # print(player.position)

            camera.look_at(player.position)

            for obj in objects:
                if hasattr(obj, 'is_dead'):
                    if obj.is_dead:
                        objects.remove(obj)
                    
            for obj in objects:
                obj.update(dt)

            snow_grid.update_snow(snowball)

            iterations = 2
            for _ in range(iterations):
                space.step(dt / iterations)

            # blit -------------------------------------------------- #
            renderer.begin(camera.get_transform())
            renderer.clear()

            # render grass
            # for x in range(GRASS_DIM[0]):
            #     for y in range(GRASS_DIM[1]):
            #         pos = (x * grass_size, y * grass_size)
            #         renderer.draw_texture(grass_texture, pos)
            renderer.draw_texture(ground_texture, (0, 0))
            
            snow_grid.draw(renderer, camera)

            for hole in holes:
                hole.draw(renderer)

            y_sorted = sorted(objects, key=lambda obj: obj.position.y, reverse=True)
            for obj in y_sorted:
                obj.draw(renderer)

            renderer.end()

            # draw gui -------------------------------------------------- #
            renderer.begin()

            renderer.draw_texture(timer_window_texture, (15, 620))
            surf = font.render(f'Time: {(60 * 3 - time):.0f}', True, (0, 0, 0))
            font_texture = Texture.from_pygame_surface(surf)
            renderer.draw_texture(font_texture, (50, 640))

            renderer.end()

        elif mode == 2:
            renderer.begin()
            renderer.clear()

            surf = font_big.render(f'Score: {score:.0f}', True, (0, 0, 0))
            font_texture = Texture.from_pygame_surface(surf)
            renderer.draw_texture(end_texture, (0, 0))
            snowball.draw(renderer)
            renderer.draw_texture(font_texture, (530, 130))

            renderer.end()

        # flip screen
        pygame.display.flip()


if __name__ == "__main__":
    import os
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    main()
    pygame.quit()
