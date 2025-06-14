import pygame as pg
import win32gui
import win32con
import element as el
from element import Element
from layout import update_elements_r, draw_r

def wndProc(oldWndProc, draw_callback, hWnd, message, wParam, lParam):
    if message == win32con.WM_SIZE:
        draw_callback()
        win32gui.RedrawWindow(hWnd, None, None, win32con.RDW_INVALIDATE | win32con.RDW_ERASE) # type: ignore
    return win32gui.CallWindowProc(oldWndProc, hWnd, message, wParam, lParam)

# Testbed
pg.init()
display = pg.display.set_mode((1280, 720), pg.RESIZABLE)

box1 = Element(
    min_height = 50,
    background = (255, 0, 0)
)
box2 = Element(
    background = (0, 0, 255),
    sizing = 1
)
box3 = Element(
    min_height = 200,
    size = pg.Vector2(50, 50),
    background = (0, 255, 0)
)
root = Element(
    horizontal = False,
    size = pg.Vector2(display.get_size()),
    background = (255, 255, 255),
    children = [box1, box2, box3],
    align = el.stretch
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

while True:
    for e in pg.event.get():
        if e.type == pg.QUIT:
            exit()
        if e.type == pg.VIDEORESIZE:
            display = pg.display.set_mode(e.size, pg.RESIZABLE | pg.SRCALPHA)

    draw_and_update()
