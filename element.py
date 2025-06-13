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
    """A pygame implementation of flexbox-like elements.

    Your root element MUST have a fixed size"""
    def __init__(self, **args):
        # defaults
        self.horizontal = True # Stack items horizontally
        self.parent: Element | None = None
        ## Sizing
        self.size = pg.Vector2(0, 0)
        self.sizing = 0 # fixed = 0, grow > 0, fit/shrink = -1
        self.min_width = 0
        self.max_width = float('inf')
        self.min_height = 0
        self.max_height = float('inf')
        self.padding = [0, 0, 0, 0]
        ## Positioning
        self.position = pg.Vector2(0, 0) # Topleft pos of the element
        self.align = start # Start, end, center, stretch
        self.justify = start # Start, end, center, space_between, space_around
        self.children: list[Element] = []
        self.child_gap = 0
        ## Graphic
        self.visible = True
        self.background = (0, 0, 0, 0)

        # Override defaults
        self.__dict__ |= args

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

def update_elements_r(e: Element):
    """Recursively update elements"""
    # Size elements
    size_main_axis_r(e)
    grow_r(e)
    size_cross_axis_r(e)

    # Make their surfaces
    make_surface_r(e)

def size_main_axis_r(e: Element):
    """Depth first post order size fit elements"""
    # Traversal
    for c in e.children:
        size_main_axis_r(c)

    # Skip fixed elements
    if e.sizing == 0:
        return

    # Skip grow elements
    if e.sizing > 0:
        if e.horizontal:
            e.width = 0 # Setter clamps value for us
        else:
            e.height = 0
        return

    # Shrink element
    ## Get total size of children along main-axis
    if e.horizontal:
        content_size = 0 # TODO: Padding and child gap
        for c in e.children:
            content_size += c.width

        e.width = content_size
    else:
        content_size = 0 # TODO: Padding and child gap
        for c in e.children:
            content_size += c.height

        e.height = content_size

def size_cross_axis_r(e: Element):
    """DFPO fit elements cross axis wise"""
    for c in e.children:
        size_cross_axis_r(c)

    if e.sizing >= 0:
        return

    # Fit on cross axis
    if e.horizontal:
        e.height = max(c.height for c in e.children) # TODO: Padding
    else:
        e.width = max(c.width for c in e.children)

def stretch_r(e: Element):
    """Recursivly stretch children"""
    if e.align == 3:
        for c in e.children:
            c.height = e.height # TODO: Padding

    for c in e.children:
        stretch_r(c)

def grow_r(e: Element):
    """Recursively grow children along the main axis of `e`"""
    # Calculate remaining space and find children to grow
    remaining_space = 0 # TODO: Padding and child gap
    grow_children = []
    for c in e.children:
        remaining_space += c.width if e.horizontal else c.height
        if c.sizing > 0:
            grow_children.append(c)

    while remaining_space > 0 and grow_children:
        num_partitions = sum(c.sizing for c in grow_children)
        # Keep track of the children who hit their max size during each iter
        ms_children = []
        curr_iter_used_space = 0
        for c in grow_children:
            unit_size = (remaining_space * (c.sizing / num_partitions))
            if e.horizontal:
                target_size = c.width + unit_size
                max_size = c.max_width
                c.width = target_size
            else:
                target_size = c.height + unit_size
                max_size = c.max_height
                c.height = target_size

            if target_size >= max_size:
                ms_children.append(c)
                curr_iter_used_space += max_size
            else:
                curr_iter_used_space += target_size

        # Remove children who hit their max size
        for c in ms_children:
            grow_children.remove(c)

        # If all children hit max sizes
        if curr_iter_used_space == 0:
            break

        remaining_space -= curr_iter_used_space

    for c in e.children:
        grow_r(c)

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
