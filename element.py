import pygame as pg
from typing import Optional

# Config consts
horizontal = 0
vertical = 1
start = 0
end = 1
center = 2
stretch = 3
space_between = 3
space_around = 4

class Element():
    def __init__(self, **args):
        # defaults
        self.horizontal: bool = True # Stack items horizontally
        self.parent: Element | None = None
        ## Sizing
        self.size: pg.Vector2 = pg.Vector2(0, 0)
        self.sizing: int = 0 # fixed = 0, grow > 0, fit/shrink = -1
        self.min_width: float = 0
        self.max_width: float = float('inf')
        self.min_height: float = 0
        self.max_height: float = float('inf')
        self.padding: list[int] = [0, 0, 0, 0]
        ## Positioning
        self.position: pg.Vector2 = pg.Vector2(0, 0) # Topleft pos of the element
        self.align: int = start # Start, end, center, stretch
        self.justify: int = start # Start, end, center, space_between, space_around
        self.children: list[Element] = []
        self.child_gap: int = 0
        ## Graphic
        self.visible = True
        self.background = (0, 0, 0, 0)

        # Override defaults
        self.__dict__ |= args

        self.width, self.height = self.size # Make sure size respects min/max constraints

        # Set childrens' parent
        for child in self.children:
            child.parent = self

        # Cache the element's texture
        ## Created when updated
        self.surface: pg.Surface | None = None

    def is_leaf(self):
        return len(self.children) == 0

    def add_child(self, c: "Element", position: int = -1):
        if not position in range(-1, len(self.children)):
            raise ValueError(f"{position} position out of range of children")

        self.children.insert(position, c)

    def draw(self, surf: pg.Surface):
        if self.surface is None:
            raise ValueError("Element is missing texture")

        surf.blit(self.surface, self.position)

    # Width getter/setter
    @property
    def width(self): return self.size.x
    @width.setter
    def width(self, value): self.size.x = pg.math.clamp(value, self.min_width, self.max_width)

    # Height getter/setter
    @property
    def height(self): return self.size.y
    @height.setter
    def height(self, value): self.size.y = pg.math.clamp(value, self.min_height, self.max_height)

    # Edge getters/setters
    @property
    def left(self): return self.position.x
    @left.setter
    def left(self, value): self.position.x = value

    @property
    def top(self): return self.position.y
    @top.setter
    def top(self, value): self.position.y = value

    @property
    def right(self): return self.position.x + self.size.x
    @right.setter
    def right(self, value): self.position.x = value - self.size.x

    @property
    def bottom(self): return self.position.y + self.size.y
    @bottom.setter
    def bottom(self, value): self.position.y = value - self.size.y

    @property
    def center(self): return self.position + 0.5 * self.size
    @center.setter
    def center(self, value):
        self.position = value - 0.5 * self.size

    @property
    def centerx(self): return self.position.x + 0.5 * self.size.x
    @centerx.setter
    def centerx(self, value):
        self.position.x = value - 0.5 * self.size.x

    @property
    def centery(self): return self.position.y + 0.5 * self.size.y
    @centery.setter
    def centery(self, value):
        self.position.y = value - 0.5 * self.size.y

def make_surface_r(e: Element):
    """Recursively make the elements' textures"""
    e.surface = pg.Surface(e.size)
    e.surface.fill(e.background)

    for child in e.children:
        make_surface_r(child)

def draw_r(e: Element, surf: pg.Surface):
    """Recursively draw elements"""
    e.draw(surf)
    for c in e.children:
        draw_r(c, surf)
