import pygame as pg
import win32gui
import win32con
import pgui
from pgui import input, actions, Element, update_elements_r, draw_r, Text

def wndProc(oldWndProc, draw_callback, hWnd, message, wParam, lParam):
    if message == win32con.WM_SIZE:
        draw_callback()
        win32gui.RedrawWindow(hWnd, None, None, win32con.RDW_INVALIDATE | win32con.RDW_ERASE) # type: ignore
    return win32gui.CallWindowProc(oldWndProc, hWnd, message, wParam, lParam)

# Testbed
pg.init()
display = pg.display.set_mode((1280, 720), pg.RESIZABLE)
clock = pg.Clock()

class GrabBar(Element):
    def __init__(self, **args):
        super().__init__(**args)
        input.sub(actions.m1d, self.on_m1d)

    def on_m1d(self, **args):
        rect = pg.FRect(self.position, self.size)
        if rect.collidepoint(args['pos']):
            input.sub(actions.mouse_move, self.on_mouse_move)
            input.sub(actions.m1u, self.on_m1u)

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
        input.unsub(actions.mouse_move, self.on_mouse_move)
        input.unsub(actions.m1u, self.on_m1u)

    def on_mouse_enter(self):
        pg.mouse.set_cursor(pg.cursors.Cursor(pg.SYSTEM_CURSOR_SIZENS))

    def on_mouse_exit(self):
        pg.mouse.set_cursor(pg.cursors.Cursor(pg.SYSTEM_CURSOR_ARROW))

title = Text(
    text = "HI MOM",
    font = pg.font.SysFont('Arial', 30),
    background = (255, 0, 0)
)

grab_bar = GrabBar(
    height = 10,
    width = 10,
    sizing_w = 1
)
box1 = Element(
    min_height = 50,
    width = 100,
    background = (255, 0, 0),
    sizing_w = 1,
    children = [title],
    align = pgui.element.center,
    justify = pgui.element.center
)
box2 = Element(
    background = (0, 0, 255),
    sizing = (1, 1)
)
box3 = Element(
    horizontal = False,
    min_height = 200,
    size = pg.Vector2(50, 50),
    background = (0, 255, 0),
    sizing_w = 1,
    children = [grab_bar]
)
root = Element(
    horizontal = False,
    size = pg.Vector2(display.get_size()),
    background = (255, 255, 255),
    children = [box1, box2, box3],
)

def draw_and_update():
    global root, display
    root.size = pg.Vector2(display.get_size())
    update_elements_r(root)
    display.fill((0, 0, 0))
    draw_r(root, display)
    pg.display.flip()

oldWndProc = win32gui.SetWindowLong(
    win32gui.GetForegroundWindow(),
    win32con.GWL_WNDPROC,
    lambda *args: wndProc(oldWndProc, draw_and_update, *args)
)

prev_hovered = []

update_elements_r(root)

while True:
    dt = clock.tick(120)
    for e in pg.event.get():
        if e.type == pg.QUIT:
            exit()
        elif e.type == pg.VIDEORESIZE:
            display = pg.display.set_mode(e.size, pg.RESIZABLE)
        else:
            pg.event.post(e)

    input.update()

    hovered = root.get_hovered(input.mpos)
    for e in set(hovered) - set(prev_hovered):
        e.on_mouse_enter()

    for e in set(prev_hovered) - set(hovered):
        e.on_mouse_exit()

    prev_hovered = hovered

    draw_and_update()
