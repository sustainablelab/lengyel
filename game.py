#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""Draw the math in Lengyel 'Foundations of Game Engine Development Vol 1'
"""

from pathlib import Path
import atexit
import pygame
from libs.utils import setup_logging
from libs.ui import UI
from libs.os_window import OsWindow
from libs.cpu import CPU
from libs.text import TextHud
from libs.gpu import GPU

def shutdown(filename:str) -> None:
    logger.info(f"Shutdown {filename}")
    pygame.font.quit()
    pygame.quit()

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        self.gpu_render = True
        self.os_window = OsWindow(self.gpu_render)
        self.cpu = CPU(self) if not self.gpu_render else None
        self.gpu = GPU(self) if self.gpu_render else None
        self.ui = UI(self)
        self.clock = pygame.time.Clock()
        self.debug = True

    def run(self) -> None:
        while True: self.game_loop()

    def game_loop(self) -> None:
        self.text_hud = TextHud(self) if self.debug else None
        self.ui.handle_events()
        if self.cpu: self.cpu.render()
        if self.gpu: self.gpu.render()
        self.clock.tick(60)

if __name__ == '__main__':
    logger = setup_logging()
    logger.info(f"Run {Path(__file__).name}")
    atexit.register(shutdown, f"{Path(__file__).name}")
    Game().run()
