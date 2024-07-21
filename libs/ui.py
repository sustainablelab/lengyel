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

    def KEYDOWN(self, event) -> None:
        match event.key:
            case pygame.K_q: sys.exit()
            case pygame.K_F11: pygame.display.toggle_fullscreen()
            case _: logger.debug(f"{event.key}")
