from element import *

def update_elements_r(e: Element):
    """Recursively update elements"""
    # Size elements
    size_main_axis_r(e)
    grow_r(e)
    size_cross_axis_r(e)
    stretch_r(e)
    # Position elements
    position_r(e)

    # Make their surfaces
    make_surface_r(e)

def size_main_axis_r(e: Element):
    """Depth first post order size fit elements"""
    # Traversal
    for c in e.children:
        size_main_axis_r(c)

    # Skip fixed elements
    if e.sizing == fixed:
        return

    # Skip grow elements
    elif e.sizing > fixed:
        if e.horizontal:
            e.width = 0 # Setter clamps value for us
        else:
            e.height = 0
        return

    # Shrink element
    ## Get total size of children along main-axis
    elif e.sizing == shrink:
        if e.horizontal:
            content_size = sum(e.padding[:2]) + e.child_gap * (len(e.children) - 1)
            for c in e.children:
                content_size += c.width

            e.width = content_size
        else:
            content_size = sum(e.padding[2:]) + e.child_gap * (len(e.children) - 1)
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
        e.height = max(c.height for c in e.children) + sum(e.padding[2:])
    else:
        e.width = max(c.width for c in e.children) + sum(e.padding[:2])

def stretch_r(e: Element):
    """Recursivly stretch children"""
    if e.align == 3 and not e.sizing == -1: # shrink overrides align
        for c in e.children:
            if e.horizontal:
                c.height = e.height - sum(e.padding[2:])
            else:
                c.width = e.width - sum(e.padding[:2])

    for c in e.children:
        stretch_r(c)

def grow_r(e: Element):
    """Recursively grow children along the main axis of `e`"""
    # Calculate remaining space and find children to grow
    if len(e.children) == 0:
        return

    if e.horizontal:
        remaining_space = e.width - sum(e.padding[:2])
    else:
        remaining_space = e.height - sum(e.padding[2:])

    remaining_space -= e.child_gap * (len(e.children) - 1)
    grow_children = []
    for c in e.children:
        if c.sizing > 0:
            grow_children.append(c)
        else:
            remaining_space -= c.width if e.horizontal else c.height

    # Prevent the loop from going again with tiny tiny amounts of space left due to floating point error
    while remaining_space > 1 and grow_children:
        num_partitions = sum(c.sizing for c in grow_children)
        # Keep track of the children who hit their max size during each iter
        ms_children = []
        curr_iter_used_space = 0
        for c in grow_children:
            target_size = (remaining_space * (c.sizing / num_partitions))
            if e.horizontal:
                max_size = c.max_width
                min_size = c.min_width
                c.width = target_size
            else:
                max_size = c.max_height
                min_size = c.min_height
                c.height = target_size

            if target_size >= max_size:
                ms_children.append(c)
                curr_iter_used_space += max_size
            elif target_size <= min_size:
                ms_children.append(c)
                curr_iter_used_space += min_size
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
    if e.align in [start, stretch]:
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
