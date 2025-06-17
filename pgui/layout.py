from .element import *

def update_elements_r(e: Element):
    """Recursively update elements"""
    # Size elements
    set_widths_r(e)
    grow_widths_r(e)
    set_heights_r(e)
    grow_heights_r(e)

    # Position elements
    position_r(e)

    # Make their surfaces
    make_surface_r(e)

def set_widths_r(e: Element):
    """Recursively set fixed and shrink widths"""
    # Have to fix the widths of children first
    for c in e.children:
        set_widths_r(c)

    if e.sizing_w > 0: # If element is set to grow
        e.width = 0
        return
    elif e.sizing_w == shrink:
        if e.horizontal:
            # Width is made of padding, child gap, and sum of child widths
            e.width = sum(e.padding[:2]) + e.child_gap * (len(e.children) - 1) + sum([c.width for c in e.children])
        else:
            e.width = sum(e.padding[:2]) + max([c.width for c in e.children])

def grow_widths_r(e: Element):
    """Recursively grow child widths."""
    # TODO: Text and wrapping text
    if not e.children: # No children to grow
        return

    # If vertical layout, the widths are just equal to the parent widths
    if not e.horizontal:
        for c in e.children:
            if c.sizing_w > 0:
                c.width = e.width - sum(e.padding[:2])
    else:
        to_grow: list[Element] = []
        num_partitions: int = 0
        remaining_space = e.width - sum(e.padding[:2]) - sum([c.width for c in e.children]) - (len(e.children) - 1) * e.child_gap
        for c in e.children:
            if c.sizing_w > 0:
                to_grow.append(c)
                num_partitions += c.sizing_w
                # Add back grow children's width
                # Incase there was a constraint hit when setting its width to 0
                remaining_space += c.width

        # Check if any target widths are smaller than min widths and set those first
        dirty_children = []
        for c in to_grow:
            target_width = c.sizing_w * remaining_space / num_partitions
            if target_width <= c.min_width:
                c.width = c.min_width
                remaining_space -= c.width
                num_partitions -= c.sizing_w
                dirty_children.append(c)

        for c in dirty_children:
            to_grow.remove(c)

        # We might have to redistribute space multiple times if children hit constraints
        while remaining_space > 0 and to_grow: # While there is space to redistribute, and children to grow
            curr_space_used = 0
            dirty_children = []
            for c in to_grow:
                target_width = c.sizing_w * remaining_space / num_partitions
                c.width += target_width
                if c.width < target_width: # If we hit max width
                    curr_space_used += c.width
                    dirty_children.append(c) # We can't grow this child anymore
                    num_partitions -= c.sizing_w

            for c in dirty_children:
                to_grow.remove(c)
            # If there was no progress made this iter
            if curr_space_used == 0:
                break

            remaining_space -= curr_space_used

    for c in e.children:
        grow_widths_r(c)

def set_heights_r(e: Element):
    """Recursively set fixed and shrink heights"""
    for c in e.children:
        set_heights_r(c)

    if e.sizing_h > 0:
        e.height = 0
        return
    elif e.sizing == shrink:
        if e.horizontal:
            e.height = sum(e.padding[2:]) + max([c.height for c in e.children])
        else:
            e.height = sum(e.padding[2:]) + sum([c.height for c in e.children]) + (len(e.children) - 1) * e.child_gap

def grow_heights_r(e: Element):
    """Recursively grow child heights"""
    # TODO: Text and wrapping text
    if not e.children: # No children to grow
        return

    # If horizontal layout, the heights are just equal to the parent heights minus padding
    if e.horizontal:
        for c in e.children:
            c.height = e.height - sum(e.padding[2:])
    else:
        to_grow: list[Element] = []
        num_partitions: int = 0
        remaining_space = e.height - sum(e.padding[2:]) - sum([c.height for c in e.children]) - (len(e.children) - 1) * e.child_gap
        for c in e.children:
            if c.sizing_h > 0:
                to_grow.append(c)
                num_partitions += c.sizing_h
                remaining_space += c.height

        # Allocate minimum heights if min height smaller than target sizes
        dirty_children = []
        for c in to_grow:
            target_height = c.sizing_h * remaining_space / num_partitions
            if target_height <= c.min_height:
                c.height = c.min_height
                remaining_space -= c.height
                num_partitions -= c.sizing_h
                dirty_children.append(c)

        for c in dirty_children:
            to_grow.remove(c)

        while remaining_space > 0 and to_grow: # While there is space to redistribute, and children to grow
            curr_space_used = 0
            dirty_children = []
            for c in to_grow:
                target_height = c.sizing_h * remaining_space / num_partitions
                c.height += target_height
                if c.height < target_height: # If we hit max height
                    curr_space_used += c.height
                    dirty_children.append(c) # We can't grow this child anymore
                    num_partitions -= c.sizing_h

            for c in dirty_children:
                to_grow.remove(c)
            # If there was no progress made this iter
            if curr_space_used == 0:
                break

            remaining_space -= curr_space_used

    for c in e.children:
        grow_heights_r(c)

def position_r(e: Element):
    """Recursively position each element's children"""
    # Position all elements in relation to e
    if len(e.children) == 0:
        return

    align(e)
    justify(e)

    for c in e.children:
        position_r(c)

def align(e: Element):
    """Align the element's children"""
    if e.align == start:
        if e.horizontal:
            ypos = e.top + e.padding[2]
            for c in e.children:
                c.top = ypos
        else:
            xpos = e.left + e.padding[0]
            for c in e.children:
                c.left = xpos
    elif e.align == end:
        if e.horizontal:
            ypos = e.bottom - e.padding[3]
            for c in e.children:
                c.bottom = ypos
        else:
            xpos = e.right - e.padding[1]
            for c in e.children:
                c.right = xpos
    elif e.align == center:
        if e.horizontal:
            for c in e.children:
                c.centery = e.centery
        else:
            for c in e.children:
                c.centerx = e.centerx

def justify(e: Element):
    """Justify the element's children"""
    # TODO: Break this function up
    if e.justify == start:
        if e.horizontal:
            curr_x = e.left + e.padding[0]
            for c in e.children:
                c.left = curr_x
                curr_x += c.width + e.child_gap
        else:
            curr_y = e.top + e.padding[2]
            for c in e.children:
                c.top = curr_y
                curr_y += c.height + e.child_gap
    elif e.justify == end:
        if e.horizontal:
            curr_x = e.right - e.padding[1]
            for c in reversed(e.children):
                c.right = curr_x
                curr_x -= c.width + e.child_gap
        else:
            curr_y = e.bottom - e.padding[3]
            for c in reversed(e.children):
                c.bottom = curr_y
                curr_y = c.height + e.child_gap
    elif e.justify == center:
        if e.horizontal:
            child_total_widths = e.child_gap * (len(e.children) - 1) + sum(c.width for c in e.children)
            curr_x = e.centerx - 0.5 * child_total_widths
            for c in e.children:
                c.left = curr_x
                curr_x += c.width + e.child_gap
        else:
            child_total_heights = e.child_gap * (len(e.children) - 1) + sum(c.height for c in e.children)
            curr_y = e.centery - 0.5 * child_total_heights
            for c in e.children:
                c.top = curr_y
                curr_y += c.height + e.child_gap
    elif e.justify == space_around:
        # Center position and ignore child_gap
        if e.horizontal:
            num_spaces = len(e.children) * 2
            remaining_space = e.width - sum(c.width for c in e.children) - sum(e.padding[:2])
            space_size = remaining_space / num_spaces
            curr_x = e.left + e.padding[0]
            for c in e.children:
                c.left = pg.math.clamp(
                    curr_x + space_size,
                    e.left + e.padding[0],
                    e.right - e.padding[1] - c.width
                )
                curr_x += space_size * 2 + c.width
        else:
            num_spaces = len(e.children) * 2
            remaining_space = e.height - sum(c.height for c in e.children) - sum(e.padding[2:])
            space_size = remaining_space / num_spaces
            curr_y = e.top + e.padding[2]
            for c in e.children:
                c.top = pg.math.clamp(
                    curr_y + space_size,
                    e.top + e.padding[2],
                    e.bottom - e.padding[3] - c.height
                )
                curr_y += space_size * 2 + c.height

    elif e.justify == space_between:
        if e.horizontal:
            num_spaces = len(e.children) - 1
            remaining_space = e.width - sum(c.width for c in e.children) - sum(e.padding[:2])
            space_size = remaining_space / num_spaces
            curr_x = e.left + e.padding[0]
            for c in e.children:
                c.left = curr_x
                curr_x += c.width + space_size
        else:
            num_spaces = len(e.children) - 1
            remaining_space = e.height - sum(c.height for c in e.children) - sum(e.padding[2:])
            space_size = remaining_space / num_spaces
            curr_y = e.top + e.padding[0]
            for c in e.children:
                c.top = curr_y
                curr_y += c.height + space_size
