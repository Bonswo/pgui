import pygame as pg
from typing import Deque

# Config consts
## Axis
horizontal = 0
vertical = 1
## Positioning and Spacing
start = 0
end = 1
center = 2
space_between = 3
space_around = 4
## Sizing
fit = shrink = -1
fixed = 0

class Element():
    def __init__(self, **args):
        self.id: int = 0
        # defaults
        self.horizontal: bool = True # Stack items horizontally
        self.parent: Element | None = None
        ## Sizing
        self._size: pg.Vector2 = pg.Vector2(0, 0)
        self._sizing: pg.Vector2 = pg.Vector2(0, 0) # fixed = 0, grow > 0, fit/shrink = -1
        self.min_width: float = 0
        self.max_width: float = float('inf')
        self.min_height: float = 0
        self.max_height: float = float('inf')
        self.padding: list[int] = [0, 0, 0, 0]
        ## Positioning
        self.position: pg.Vector2 = pg.Vector2(0, 0) # Topleft pos of the element
        self.align: int = start # Start, end, center
        self.justify: int = start # Start, end, center, space_between, space_around
        self.children: list[Element] = []
        self.child_gap: int = 0
        ## Graphic
        self.visible = True
        self.background = (0, 0, 0, 0)
        ## Other
        self.hovered = False
        self.flatten = False
        self.clickthrough = False

        # Override defaults
        for arg in args:
            if arg in self.__dict__:
                self.__dict__[arg] = args[arg]

        self.width, self.height = self._size # Make sure size respects min/max constraints

        # Custom properties
        if size := args.get('size'):
            self.size = size

        if w := args.get('width'):
            self.width = w

        if h := args.get('height'):
            self.height = h

        if sizing := args.get('sizing'):
            self.sizing = sizing

        if size_w := args.get('sizing_w'):
            self.sizing_w = size_w

        if size_h := args.get('sizing_h'):
            self.sizing_h = size_h

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

    @property
    def sizing(self): return self._sizing # Returns the object so other elements can reference its size if needed
    @sizing.setter
    def sizing(self, value):
        self._sizing.update(value)

    @property
    def sizing_w(self): return int(self._sizing.x)
    @sizing_w.setter
    def sizing_w(self, value):
        self._sizing.x = value

    @property
    def sizing_h(self): return int(self._sizing.y)
    @sizing_h.setter
    def sizing_h(self, value):
        self._sizing.y = value

    @property
    def size(self): return self._size
    @size.setter
    def size(self, value):
        w, h = value
        self.width = w
        self.height = h

    def inflate(self, left=0, right=0, top=0, bottom=0):
        # TODO: Account for hitting size constraints
        if left > 0:
            self.width += left
            self.left -= left
        if right > 0:
            self.width += right
        if top > 0:
            self.height += top
            self.top -= top
        if bottom > 0:
            self.height += bottom

    # Width getter/setter
    @property
    def width(self): return self._size.x
    @width.setter
    def width(self, value): self._size.x = pg.math.clamp(value, self.min_width, self.max_width)

    # Height getter/setter
    @property
    def height(self): return self._size.y
    @height.setter
    def height(self, value): self._size.y = pg.math.clamp(value, self.min_height, self.max_height)

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
    def right(self): return self.position.x + self._size.x
    @right.setter
    def right(self, value): self.position.x = value - self._size.x

    @property
    def bottom(self): return self.position.y + self._size.y
    @bottom.setter
    def bottom(self, value): self.position.y = value - self._size.y

    @property
    def center(self): return self.position + 0.5 * self._size
    @center.setter
    def center(self, value):
        self.position = value - 0.5 * self.size

    @property
    def centerx(self): return self.position.x + 0.5 * self._size.x
    @centerx.setter
    def centerx(self, value):
        self.position.x = value - 0.5 * self._size.x

    @property
    def centery(self): return self.position.y + 0.5 * self.height
    @centery.setter
    def centery(self, value):
        self.top = value - 0.5 * self.height

    def on_mouse_enter(self):
        pass

    def on_mouse_exit(self):
        pass

    def bfs(self):
        result = [self]
        if self.flatten:
            return result

        q = Deque()
        for c in self.children:
            q.append(c)

        while len(q) > 0:
            curr = q.popleft()
            if not curr.clickthrough:
                result.append(curr)
            for c in curr.children:
                q.append(c)

        return result

    def get_hovered(self, pos):
        """Returns the hovered elements, deepest first"""
        elements = reversed(self.bfs())
        collided = []
        for e in elements:
            rect = pg.FRect(e.position, e.size)
            if rect.collidepoint(pos):
                collided.append(e)

        return collided

def make_surface_r(e: Element):
    """Recursively make the elements' textures"""
    e.surface = pg.Surface(e.size, pg.SRCALPHA)
    e.surface.fill(e.background)

    for child in e.children:
        make_surface_r(child)

def draw_r(e: Element, surf: pg.Surface):
    """Recursively draw elements"""
    e.draw(surf)
    for c in e.children:
        draw_r(c, surf)
