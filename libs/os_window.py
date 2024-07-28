#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""OS Window
"""

import pygame

class OsWindow:
    def __init__(self, gpu_render:bool=True) -> None:
        if gpu_render:
            flags = pygame.RESIZABLE | pygame.OPENGL | pygame.DOUBLEBUF
        else:
            flags = pygame.RESIZABLE
        self.surf = pygame.display.set_mode((16*50,9*50), flags=flags)
        self._size = self.surf.get_size()

    @property
    def size(self) -> tuple:
        """Using GPU, get_size() doesn't update with new window size. Use events instead."""
        return self._size

    def WINDOWRESIZED(self, event) -> None:
        """Use events to track window size."""
        self._size = (event.x, event.y)

