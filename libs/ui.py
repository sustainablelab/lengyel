#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""User interface
"""

import pygame
import logging
import sys

logger = logging.getLogger(__name__)

class UI:
    def __init__(self, game) -> None:
        self.game = game

    def handle_events(self) -> None:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT: sys.exit()
                case pygame.KEYDOWN: self.KEYDOWN(event)
                case pygame.WINDOWRESIZED: self.game.os_window.WINDOWRESIZED(event)
                case pygame.MOUSEWHEEL: self.MOUSEWHEEL(event)

    def MOUSEWHEEL(self, event) -> None:
        match event.y:
            case 1: self.game.zoom_in()
            case -1: self.game.zoom_out()
            case _: pass

    def KEYDOWN(self, event) -> None:
        match event.key:
            case pygame.K_q: sys.exit()
            case pygame.K_F11: pygame.display.toggle_fullscreen()
            case pygame.K_F2: self.game.debug = not self.game.debug
            case pygame.K_w: self.game.player.move_up()
            case pygame.K_a: self.game.player.move_left()
            case pygame.K_s: self.game.player.move_down()
            case pygame.K_d: self.game.player.move_right()
            case _: logger.debug(f"{event.key}")
