#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""Text
"""

import pygame
from pygame import Surface, Color, Rect

class Text:
    def __init__(self, size:int) -> None:
        self.font = pygame.font.SysFont("RobotoMono", size)
        self.msg = ""
        self.pos = (0,0)

    def render(self, surf:Surface, color:Color) -> tuple:
        w = 0
        h = self.line_height*len(self.msg_lines)
        for i,line in enumerate(self.msg_lines):
            ### render(text, antialias, color, background=None) -> Surface
            text_surf = self.font.render(line, True, color)
            w = max(w, text_surf.get_width())
            ### blit(source, dest, area=None, special_flags=0) -> Rect
            surf.blit(text_surf, (self.pos[0], self.pos[1] + i*self.line_height))
        return (w,h)

    @property
    def msg_lines(self) -> list:
        return self.msg.split("\n")

    @property
    def line_height(self) -> int:
        ### get_linesize() -> int
        return self.font.get_linesize()


class TextHud(Text):
    def __init__(self, game, size:int=15) -> None:
        super().__init__(size)
        self.game = game
        self.msg += f"FPS: {self.game.clock.get_fps():0.1f}"
        self.msg += f"\nWindow: {self.game.os_window.size}"
