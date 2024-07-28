#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""Draw the math in Lengyel 'Foundations of Game Engine Development Vol 1'

[x] Set up GPU rendering
[x] Create a simple player: a white square to move around
[ ] Mousewheel zoom at the mouse location

[ ] Make the projection and view matrices global to GPU

GPU.render:
    ├─ render_test_square() (scenery)
    │  ├─ proj_mat (correct for window aspect ratio)
    │  └─ view_mat (scale and offset)
    │   shader: gl_Position = view_mat * proj_mat * pos;
    └─ render_player()
       ├─ size : self.game.player.size = (2,2)
       ├─ pos: translate player by self.game.player.pos
       │    Example: move in increments of 1 (1/2 player size)
       ├─ xlat_mat
       │    Player position moves player by changing 'xlat_mat'
       ├─ proj_mat (correct for window aspect ratio)
       └─ view_mat (scale and offset)
        shader: gl_Position = test_mat * view_mat * proj_mat * xlat_mat*pos;
"""

from pathlib import Path
import atexit
import pygame
from array import array
from libs.utils import setup_logging
from libs.ui import UI
from libs.os_window import OsWindow
from libs.cpu import CPU
from libs.text import Text
from libs.gpu import GPU

def shutdown(filename:str) -> None:
    logger.info(f"Shutdown {filename}")
    pygame.font.quit()
    pygame.quit()

class TextHud(Text):
    def __init__(self, game, size:int=15) -> None:
        super().__init__(size)
        self.game = game
        self.msg += f"FPS: {self.game.clock.get_fps():0.1f}"
        self.msg += f"\nWindow: {self.game.os_window.size}"
        self.msg += f"\nPlayer: {self.game.player.size} at {self.game.player.pos}"
        mpos = pygame.mouse.get_pos()
        mpos_world = self.game.xfm_pix_to_world(mpos)
        self.msg += f"\nMouse: {mpos} ({mpos_world[0]:0.3f},{mpos_world[1]:0.3f})"
        self.msg += f"\nScale: {self.game.scale:0.2e}"

class Player:
    def __init__(self) -> None:
        self.pos = [0,0]                                # Initial position in world space (game coordinates)
        self.size = (2,2)                               # Player initial w,h in world space (game coordinates)

    def move_up(self) -> None:
        self.pos[1] += 1

    def move_down(self) -> None:
        self.pos[1] -= 1

    def move_left(self) -> None:
        self.pos[0] -= 1

    def move_right(self) -> None:
        self.pos[0] += 1

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        self.gpu_render = True
        self.os_window = OsWindow(self.gpu_render)
        self.cpu = CPU(self) if not self.gpu_render else None
        self.gpu = GPU(self) if self.gpu_render else None
        self.ui = UI(self)
        self.player = Player()
        self.clock = pygame.time.Clock()
        self.debug = True
        self.scale = 0.1                                # Scale world space to the display
        a = self.scale
        # Testing how to do zoom and pan using a single transformation matrix
        self.test_matrix = array('f', [
            a,0,0,0,
            0,a,0,0,
            0,0,a,0,
            0,0,0,1,
            ])
        self.view_offset = (0,0)

    def run(self) -> None:
        while True: self.game_loop()

    def game_loop(self) -> None:
        self.text_hud = TextHud(self) if self.debug else None
        self.ui.handle_events()
        if self.cpu: self.cpu.render()
        if self.gpu: self.gpu.render()
        self.clock.tick(60)

    def zoom_in(self) -> None:
        self.scale *= 1.1
        self.zoom_at_mouse()

    def zoom_out(self) -> None:
        self.scale *= 0.9
        self.zoom_at_mouse()

    def xfm_pix_to_world(self, p:tuple) -> tuple:
        """Transform pixel coordinates to world coordinates.
        A + λ(B-A) = C

        TODO: the problem is my limits in world coordinates. I need the actual
        limits on screen. This is not just the (-1:1,1:-1) scaled by
        self.scale. It is also offset by previous zooming.

        What I need is three coordinate systems:
        - World: the whole world
        - View: the portion of the world visible on screen
        - Screen: the View, but in pixel coordinates
        """
        # Calculate λ using pixel coordinates
        Cx,Cy = p
        Ax,Ay = (0,0)
        Bx,By = self.os_window.size
        Lx = (Cx-Ax)/(Bx-Ax)
        Ly = (Cy-Ay)/(By-Ay)
        # Use λ to calculate point in world coordinates.
        k = self.scale
        # TODO: incorporate offset as well
        Ax,Ay = (-1*k,1*k)
        Bx,By = (1*k,-1*k)
        Cx = Ax + Lx*(Bx-Ax)
        Cy = Ay + Ly*(By-Ay)
        return (Cx,Cy)

    def zoom_at_mouse(self) -> None:
        """Translate mouse to screen center, zoom, translate back."""
        mpos = pygame.mouse.get_pos()
        cx,cy = (0,0)                                   # World center
        mx,my = self.xfm_pix_to_world(mpos)             # LEFT OFF HERE -- this is wrong
        x,y = (cx-mx,cy-my)                             # Vector from mouse to world center
        a = self.scale
        # Setup the matrix for OpenGL in column-major order
        if 0:
            self.test_matrix = array('f', [
                a,      0,      0,0,
                0,      a,      0,0,
                0,      0,      a,0,
                a*x-x,  a*y-y,  0,1,
                ])
        else:
            # If test matrix replaces view matrix, it must, at a minimum, include self.scale
            self.test_matrix = array('f', [
                a,0,0,0,
                0,a,0,0,
                0,0,a,0,
                0,0,0,1,
                ])

if __name__ == '__main__':
    logger = setup_logging()
    logger.info(f"Run {Path(__file__).name}")
    atexit.register(shutdown, f"{Path(__file__).name}")
    Game().run()
