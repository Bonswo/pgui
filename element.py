import pygame as pg
from typing import Optional

# Config consts
horizontal = 0
vertical = 1
start = 0

class Element():
    """A pygame implementation of flexbox-like elements.

    Your root element MUST have a fixed size"""
    def __init__(self, **args):
        # defaults
        self.horizontal = True # Stack items horizontally
        self.parent: Element | None = None
        ## Sizing
        self.size = pg.Vector2(0, 0)
        self.min_width = 0
        self.max_width = float('inf')
        self.sizing_w = 0 # fixed = 0, grow > 0, fit/shrink = -1
        self.min_height = 0
        self.max_height = float('inf')
        self.sizing_h = 0 # fixed = 0, grow > 0, fit/shrink = -1
        self.padding = [0, 0, 0, 0]
        ## Positioning
        self.position = pg.Vector2(0, 0) # Topleft of the element
        # self.align = start # Replaced with
        # self.justify = start # Replaced with spacing
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

    def draw(self, surf: pg.Surface):
        if self.surface is None:
            raise ValueError("Cannot draw None to surface")

        surf.blit(self.surface, self.position)

    # Width getter/setter
    @property
    def width(self): return self.size.x
    @width.setter
    def width(self, value): self.size.x = value

    # Height getter/setter
    @property
    def height(self): return self.size.y
    @height.setter
    def height(self, value): self.size.y = value

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

def update_element(e: "Element"):
    # Size fixed and max-sized elements and
    size_widths(e)
    # Grow elements
    grow_child_widths(e)
    # Set positions
    set_child_positions(e)
    # Create Surfaces and draw to them
    make_surfaces(e)

def set_child_positions(e: Element):
    """The recursively sets all of its childrens' positions"""
    if e.horizontal:
        # Line up children side-by-side
        ## Sizes should have already been set
        ### TODO: Handle spacing and alignment
        curr_pos = e.position + (e.padding[0], e.padding[2])
        for child in e.children:
            child.position.update(curr_pos)
            set_child_positions(child)
            curr_pos += (child.width + e.child_gap, 0)

def make_surfaces(e: Element):
    # Recursively re-draw all elements' surfaces
    new = pg.Surface(e.size)
    new.fill(e.background)
    e.surface = new
    for child in e.children:
        make_surfaces(child)

def draw(e: Element, surf):
    if e.surface is None or surf is None:
        raise ValueError("Cannot draw None to surface")

    surf.blit(e.surface, e.position)
    # Draw the children one after the other
    for child in e.children:
        draw(child, surf)

def size_widths(e: Element):
    # DFPO traversal to size fixed elements
    total_children_widths = 0
    for child in e.children:
        size_widths(child)
        total_children_widths += child.width + e.child_gap

    if e.sizing_w > 0:
        # e will be sized in the "grow_elements" pass
        ## BUT still has to be of min_width, so we let it take that up first
        e.width = e.min_width
    elif e.sizing_w < 0:
        # Element has to be fitted to children
        if total_children_widths < e.min_width:
            e.width = total_children_widths # TODO: Add child gaps n shit
        else:
            e.width = e.min_width
    else:
        # Just clamp its width
        e.width = max(e.min_width, (min(e.max_width, e.width)))

def grow_child_widths(e: Element):
    # BFS traverse elements and grow their widths
    # Assumes e is already sized.
    # Calculate the remaining space available for growing elements
    remaining_space = e.width - e.padding[0] - e.padding[1] - (len(e.children) - 1) * e.child_gap
    for child in e.children:
        remaining_space -= child.width

    # Find all children that can grow (sizing_w > 0)
    growing_children = [child for child in e.children if child.sizing_w > 0]
    if not growing_children or remaining_space <= 0:
        # No children to grow or no space available
        for child in e.children:
            grow_child_widths(child)

        return

    # Iteratively distribute space, handling constraints
    space_to_distribute = remaining_space
    available_children = growing_children.copy()
    while space_to_distribute > 0 and available_children:
        # Calculate total growth factor for remaining children
        total_growth_factor = sum(child.sizing_w for child in available_children)
        # Track children that hit constraints this iteration
        constrained_children = []
        space_used_this_iteration = 0
        for child in available_children:
            # Calculate proportional width for this child
            proportion = child.sizing_w / total_growth_factor
            additional_width = space_to_distribute * proportion
            target_width = child.width + additional_width
            # Apply min/max constraints
            constrained_width = max(child.min_width, min(child.max_width, target_width))
            # Calculate actual space used by this child
            actual_additional_width = constrained_width - child.width
            space_used_this_iteration += actual_additional_width
            # Update child width
            child.width = constrained_width
            # If child hit a constraint, remove it from future iterations
            if constrained_width == child.max_width or constrained_width == child.min_width:
                constrained_children.append(child)

        # Remove constrained children from available list
        for child in constrained_children:
            available_children.remove(child)

        # Update remaining space
        space_to_distribute -= space_used_this_iteration
        # Break if no progress made (If all children hit their max_widths)
        if space_used_this_iteration == 0:
            break

    # Recursively process children
    for child in e.children:
        grow_child_widths(child)
