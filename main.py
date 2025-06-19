import pygame as pg
import win32gui
import win32con
import pgui

def wndProc(oldWndProc, draw_callback, hWnd, message, wParam, lParam):
    if message == win32con.WM_SIZE:
        draw_callback()
        win32gui.RedrawWindow(hWnd, None, None, win32con.RDW_INVALIDATE | win32con.RDW_ERASE) # type: ignore
    return win32gui.CallWindowProc(oldWndProc, hWnd, message, wParam, lParam)

# Testbed
pg.init()
display = pg.display.set_mode((1280, 720), pg.RESIZABLE)
clock = pg.Clock()

class GrabBar(pgui.Element):
    """Example implementation of a grab-bar in-app"""
    def __init__(self, **args):
        super().__init__(**args)
        pgui.input.sub(pgui.actions.m1d, self.on_m1d)

    def on_m1d(self, **args):
        rect = pg.FRect(self.position, self.size)
        if rect.collidepoint(args['pos']):
            pgui.input.sub(pgui.actions.mouse_move, self.on_mouse_move)
            pgui.input.sub(pgui.actions.m1u, self.on_m1u)

    def on_mouse_move(self, **args):
        # Change size of parent element in direction of parent element
        if not self.parent:
            return

        tmp = self.parent.top
        self.centery = args['pos'][1]
        self.parent.top = self.top
        size_change = tmp - self.parent.top
        self.parent.height += size_change

    def on_m1u(self, **args):
        pgui.input.unsub(pgui.actions.mouse_move, self.on_mouse_move)
        pgui.input.unsub(pgui.actions.m1u, self.on_m1u)

    def on_mouse_enter(self):
        pg.mouse.set_cursor(pg.cursors.Cursor(pg.SYSTEM_CURSOR_SIZENS))

    def on_mouse_exit(self):
        pg.mouse.set_cursor(pg.cursors.Cursor(pg.SYSTEM_CURSOR_ARROW))

title = pgui.Text(
    text = "HI MOM",
    font = pg.font.SysFont('Arial', 30),
    background = (255, 0, 0)
)

grab_bar = GrabBar(
    height = 10,
    width = 10,
    sizing_w = 1
)
box1 = pgui.Element(
    min_height = 50,
    width = 100,
    background = (255, 0, 0),
    sizing_w = 1,
    children = [
        title,
        pgui.SVGElement(
            "icon.svg",
            size = (30, 30),
            padding = [5, 5, 5, 5],
            background = (255, 0, 0)
        )
    ],
    align = pgui.element.center,
    justify = pgui.element.center
)
box2 = pgui.Element(
    background = (0, 0, 255),
    sizing = (1, 1)
)
box3 = pgui.Element(
    horizontal = False,
    min_height = 200,
    size = pg.Vector2(50, 50),
    background = (0, 255, 0),
    sizing_w = 1,
    children = [grab_bar]
)
root = pgui.Element(
    horizontal = False,
    size = pg.Vector2(display.get_size()),
    background = (255, 255, 255),
    children = [box1, box2, box3],
)

def draw_and_update():
    global root, display
    root.size = pg.Vector2(display.get_size())
    pgui.update_elements_r(root)
    display.fill((0, 0, 0))
    pgui.draw_r(root, display)
    pg.display.flip()

oldWndProc = win32gui.SetWindowLong(
    win32gui.GetForegroundWindow(),
    win32con.GWL_WNDPROC,
    lambda *args: wndProc(oldWndProc, draw_and_update, *args)
)

prev_hovered = []

pgui.update_elements_r(root)

while True:
    dt = clock.tick(120)
    for e in pg.event.get():
        if e.type == pg.QUIT:
            exit()
        elif e.type == pg.VIDEORESIZE:
            display = pg.display.set_mode(e.size, pg.RESIZABLE)
        else:
            pg.event.post(e)

    pgui.input.update()

    hovered = root.get_hovered(pgui.input.mpos)
    for e in set(hovered) - set(prev_hovered):
        e.on_mouse_enter()

    for e in set(prev_hovered) - set(hovered):
        e.on_mouse_exit()

    prev_hovered = hovered

    draw_and_update()
