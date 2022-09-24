from engine.render import Renderer
import pymunk
from pymunk import Vec2d


class Snowball(pymunk.Circle):
    body: pymunk.Body
    
    def __init__(self, pos, radius, mass):
        body = pymunk.Body(mass, float('inf'))
        body.position = pos

        super().__init__(body, radius)
        self.friction = 0.5

    def apply_force(self, force: Vec2d):
        self.body.apply_force_at_local_point(force, (0, 0))

    def draw(self, renderer: Renderer):
        draw_pos = self.body.position + Vec2d(0, self.radius)
        renderer.draw_circle(
            (20, 20, 20), self.body.position, self.radius, 0, fade=self.radius / 5)
        renderer.draw_circle(
            (200, 200, 200), draw_pos, self.radius, 0)

