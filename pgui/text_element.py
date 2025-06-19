import pygame as pg
from .element import Element

class Text(Element):
    def __init__(self, **args):
        super().__init__(**args)

        self._cached_text = None
        self._text = None

        self._text = args.get('text', "NO TEXT")
        self.font: pg.Font = args.get('font', pg.Font())
        self.colour = args.get('colour', (0, 0, 0))
        self.text_surf: pg.Surface = self.font.render(self.text, True, self.colour)
        self.size = self.text_surf.get_size()

    @property
    def text(self): return self._text

    def draw(self, surf: pg.Surface):
        if self.surface is None:
            raise RuntimeError(f"Tried to draw to empty txt surf")
        self.surface.blit(self.text_surf, (self.padding[0], self.padding[2]))
        super().draw(surf)
