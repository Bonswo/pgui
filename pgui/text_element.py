import pygame as pg
from .element import Element

class Text(Element):
    def __init__(self, **args):
        super().__init__(**args)

        self._cached_text = None
        self._text = None

        self._text = args.get('text', "NO TEXT")
        self.font = args.get('font', pg.Font())
        self.colour = args.get('colour', (0, 0, 0))
        self.text_surf: pg.Surface = self.font.render(self.text, True, self.colour, self.background)
        self.size = self.text_surf.get_size()

    @property
    def text(self): return self._text

    def draw(self, surf: pg.Surface):
        surf.blit(self.text_surf, self.position)
