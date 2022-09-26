from engine.texture import Texture
from engine.render import Renderer
from pathlib import Path
from enum import Enum


class AnimSprite:
    
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
class AnimState:

    def __init__(self, identifiers: list[str]):
        self.state_sprites: dict[str, AnimSprite] = {}
        self.states: dict[str, Enum] = {}
        for identifier in identifiers:
            self.states[identifier] = None

        self.last_sprite: AnimSprite = None
        self.curr_sprite: AnimSprite = None

        self.last_state: str = None
        self.curr_state: str = None

    def add(self, sprite: AnimSprite, values: list[Enum]):
        values = [str(v.value) for v in values]
        string = ','.join(values)
        self.state_sprites[string] = sprite

    def set_state(self, identifier: str, value: Enum):
        self.states[identifier] = value
        self.last_state = self.curr_state
        self.curr_state = list(self.states.values())[0]
        if None not in self.states.values():
            self._update_sprite()

    def get_state(self, identifier: str):
        return self.states[identifier]

    def _update_sprite(self):
        values = [str(v.value) for v in self.states.values()]
        self.curr_sprite = self.state_sprites[','.join(values)]

        if self.last_sprite != None and self.last_sprite != self.curr_sprite:
            if self.last_state != self.curr_state:
                self.curr_sprite.reset()
            else:
                self.curr_sprite.reset(self.last_sprite.time)
        
    def update(self, dt):
        self._update_sprite()

        self.curr_sprite.update(dt)

        self.last_sprite = self.curr_sprite

    def get_sprite(self):
        return self.curr_sprite

    def get_copy(self):
        copy = AnimState(deepcopy(list(self.states.keys())))
        copy.states = deepcopy(self.states)
        copy.state_sprites = deepcopy(self.state_sprites)
        return copy