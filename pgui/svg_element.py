import pygame as pg
from .element import Element

class SVGElement(Element):
    def __init__(self, file, **args):
        super().__init__(**args)
        self._file = file
        self._cached_svg = None

    def draw(self, surf: pg.Surface):
        if not self.surface:
            raise RuntimeError(f"Tried to draw an element without a surface")

        if not self._cached_svg:
            self._cached_svg = pg.image.load_sized_svg(self._file, self.size - (sum(self.padding[:2]), sum(self.padding[2:])))

        self.surface.blit(self._cached_svg, (self.padding[0], self.padding[2]))

        super().draw(surf)
