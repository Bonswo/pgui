import pygame as pg
from enum import IntEnum, auto

class actions(IntEnum):
    m1d = auto()
    m1u = auto()
    m2d = auto()
    m2u = auto()
    m3d = auto()
    m3u = auto()
    mouse_move = auto()

class Input():
    def __init__(self):
        self.mpos = pg.Vector2()
        self.subs = {
            actions.m1d: [],
            actions.m1u: [],
            actions.m2d: [],
            actions.m2u: [],
            actions.m3d: [],
            actions.m3u: [],
            actions.mouse_move: [],
        }

    def update(self):
        for e in pg.event.get(pump=False):
            action = None
            if e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    action = actions.m1d
                elif e.button == 3:
                    action = actions.m2d

            elif e.type == pg.MOUSEMOTION:
                action = actions.mouse_move

            elif e.type == pg.MOUSEBUTTONUP:
                if e.button == 1:
                    action = actions.m1u

            if action:
                for cb in self.subs[action]:
                    cb(**e.dict)

        self.mpos.update(pg.mouse.get_pos())

    def sub(self, action, callback):
        if action not in self.subs:
            raise ValueError(f"Tried to subscribe to invalid action {action}")

        self.subs[action].append(callback)

    def unsub(self, action, cb):
        if action not in self.subs:
            print(f"Tried to unsubscribe from invalid action {action}")
        elif cb not in self.subs[action]:
            print(f"{cb} not found in {action} subscriptions")

        self.subs[action].remove(cb)

input = Input()
