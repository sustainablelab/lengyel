#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""CPU rendering
"""

import pygame
from pygame import Color, Rect, Surface

class CPU:
    def __init__(self, game) -> None:
        self.game = game

    def render(self) -> None:
        self.game.os_window.surf.fill(Color(100,0,0))
        if self.game.text_hud:
            self.game.text_hud.render(self.game.os_window.surf, Color(255,255,255))
        pygame.display.update()
