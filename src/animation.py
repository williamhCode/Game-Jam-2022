from engine.texture import Texture
from engine.render import Renderer
from pathlib import Path
from enum import Enum


class AnimatedSprite:
    
    def __init__(self, textures: list[Texture], frame_time, flipped=False):
        self.textures = textures
        self.frame_time = frame_time
        self.flipped = flipped

        self.time = 0
        self.curr_frame = 0
        self.total_frames = len(textures)

    def _calc_curr_frame(self):
        self.curr_frame = int(self.time / self.frame_time)
        if (self.curr_frame == self.total_frames):
            self.time = self.time % self.frame_time
            self.curr_frame = 0

    def reset(self, time_offset=0):
        self.time = time_offset
        self._calc_curr_frame()

    def update(self, dt):
        self.time += dt
        self._calc_curr_frame()

    def draw(self, renderer: Renderer, position, rotation=0, offset=(0, 0)):
        curr_texture = self.textures[self.curr_frame]
        renderer.draw_texture(curr_texture, position, rotation, offset, self.flipped)


from copy import deepcopy
class AnimationState:

    def __init__(self, identifiers: list[str]):
        self.stateSprites: dict[str, AnimatedSprite] = {}
        self.states: dict[str, Enum] = {}
        for identifier in identifiers:
            self.states[identifier] = None

        self.lastSprite: AnimatedSprite = None
        self.currSprite: AnimatedSprite = None

    def add_sprite(self, sprite: AnimatedSprite, values: list[Enum]):
        values = [str(v.value) for v in values]
        string = ','.join(values)
        self.stateSprites[string] = sprite

    def set_state(self, identifier: str, value: Enum):
        self.states[identifier] = value

    def get_state(self, identifier: str):
        return self.states[identifier]

    def update(self, dt):
        values = [str(v.value) for v in self.states.values()]
        self.currSprite = self.stateSprites[','.join(values)]

        if (self.lastSprite != self.currSprite):
            if (self.lastSprite != None):
                self.currSprite.reset(self.lastSprite.time)

        self.currSprite.update(dt)

        self.lastSprite = self.currSprite

    def get_sprite(self):
        return self.currSprite

    def get_copy(self):
        copy = AnimationState(list(self.states.keys()))
        copy.states = deepcopy(self.states)
        copy.stateSprites = self.stateSprites
        return copy