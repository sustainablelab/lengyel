#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""Draw a vector in 3D

TODO: write matrix operations
* [ ] transpose
* [ ] multiplication
"""

from pathlib import Path
import atexit
import pygame
from pygame import Surface, Rect, Color
from array import array
from libs.utils import setup_logging, check_array_itemsize
from libs.ui import UI
from libs.os_window import OsWindow
from libs.text import Text
import moderngl
import sys
import math

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
        mpos = pygame.mouse.get_pos()
        self.msg += f"\nMouse: {mpos})"

class GPU:
    def __init__(self, game) -> None:
        self.game = game

        self.ctx = moderngl.create_context()
        self.shaders = self.load_shaders()
        self.t = 0
        self.update_xfms(self.t)

    def update_xfms(self, t:float) -> None:
        """Update values in transformation matrix shader uniforms.

        t -- time (a value that increases at a constant rate as the game runs)
        """
        # Transforms
        a = self.game.os_window.size[1]/self.game.os_window.size[0] # aspect ratio
        self.proj_mat = array('f', [
            a, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
            ])
        if 0:
            a = 2 # scale
            self.view_mat = array('f', [
                2,      1, 0, 0,
                0,      2, 0, 0,
                0.8, -0.8, 1, 0,
                0,      0, 0, 1
                ])
        else:
            a = math.radians(30) # tilt angle
            c = math.cos(a)
            s = math.sin(a)
            # TODO: I want to tilt the xz plane forward so I can see it while
            # it rotates
            self.tilt_mat = array('f', [
                1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 0, 1
                ])
            c=math.cos(t)
            s=math.sin(t)
            self.view_mat = array('f', [
                c, 0,-s, 0,
                0, 1, 0, 0,
                s, 0, c, 0,
                0, 0, 0, 1,
                ])
            # Hacking around making a matrix with constant tilt that rotates over time
            self.view_mat = array('f', [
                 c,    1,-s, 0,
                 0,    1, 0, 0,
                 s, -0.1, c, 0,
                 0, 0, 0, 1,
                ])

    def load_shaders(self) -> dict:
        shaders = {}
        with open("shaders/hud.vert") as f: vert = f.read()
        with open("shaders/hud.frag") as f: frag = f.read()
        shader = self.ctx.program(vertex_shader=vert, fragment_shader=frag)
        shaders['shader_hud'] = shader
        with open("shaders/test_vec.vert") as f: vert = f.read()
        with open("shaders/test_vec.frag") as f: frag = f.read()
        shader = self.ctx.program(vertex_shader=vert, fragment_shader=frag)
        shaders['shader_test_vec'] = shader
        return shaders

    def render(self) -> None:
        self.t += 0.01
        self.update_xfms(self.t)
        self.ctx.clear(0.1,0.1,0.1)
        self.ctx.blend_func = moderngl.DEFAULT_BLENDING
        self.ctx.enable(moderngl.BLEND)
        # RENDER 3D STUFF HERE
        self.render_test_vec_axes()
        self.render_test_vec(x=0.2,y=0.2,z=0.2)
        if self.game.text_hud:
            self.ctx.blend_func = moderngl.PREMULTIPLIED_ALPHA
            self.render_hud()
        self.ctx.disable(moderngl.BLEND)
        pygame.display.flip()

    def render_hud(self) -> None:
        def make_hud_surf() -> Surface:
            """Draw HUD to a texture."""
            # Draw the text on a temporary surface that fills the OS Window
            temp_surf = pygame.Surface(self.game.os_window.size)
            # Get the size (w,h) of the Rect that bounds the text
            size = self.game.text_hud.render(temp_surf, Color(255,255,255))
            # Create a new surface sized exactly for the text
            surf = Surface(size)
            # Copy from the temporary surface to this smaller surface
            surf.blit(temp_surf, (0,0), Rect((0,0),size))
            return surf
        def make_hud_vbo(surf:Surface) -> moderngl.Buffer:
            """Map HUD to window coordinates (-1:1 coord sys).

            * Subtract 0.5 to get a value between -0.5 and 0.5
            * Scale by 2 to get a value between -1 and 1
            * And since down is negative, scale the y value by -2, not +2

            TODO: use self.game.text_hud.pos to control where HUD is placed on screen.
            """
            hud_size = surf.get_size()
            win_size = self.game.os_window.size
            hud_size_in_win_coordinates = (
                     2*(hud_size[0]/win_size[0] - 0.5),
                    -2*(hud_size[1]/win_size[1] - 0.5))
            # Right edge
            r = hud_size_in_win_coordinates[0]
            # Bottom edge
            b = hud_size_in_win_coordinates[1]
            return self.ctx.buffer(data=array('f', [
                # vert  tex
                -1, 1,  0, 0,
                 r, 1,  1, 0,
                -1, b,  0, 1,
                 r, b,  1, 1,
                ]))
        surf = make_hud_surf()
        vbo = make_hud_vbo(surf)
        vao = self.ctx.vertex_array(
                self.shaders['shader_hud'],
                [(vbo, '2f 2f', 'vert_pos', 'tex_coord')])
        tex = self.ctx.texture(surf.get_size(), 4)      # 4 color channels
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.swizzle = 'BGRA'
        tex.write(surf.get_view('1'))
        tex.use(0)
        self.shaders['shader_hud']['tex'] = 0
        self.shaders['shader_hud']['alpha'] = 1.0
        vao.render(mode=moderngl.TRIANGLE_STRIP)
        tex.release()
        vao.release()

    def render_test_vec_axes(self) -> None:
        """Draw x,y,z axes."""
        self.shaders['shader_test_vec']['proj_mat'] = self.proj_mat
        self.shaders['shader_test_vec']['view_mat'] = self.view_mat
        self.shaders['shader_test_vec']['tilt_mat'] = self.tilt_mat
        self.shaders['shader_test_vec']['alpha'] = 0.4
        e=0.5; v=1.0
        vbo = self.ctx.buffer(data=array('f', [
            0.0, 0.0, 0.0,        v, 0.0, 0.0, # 0 Red      (ex)
              e, 0.0, 0.0,        v, 0.0, 0.0, # 1 Red      (ex)
            0.0, 0.0, 0.0,      0.0,   v, 0.0, # 2 Green    (ey)
            0.0,   e, 0.0,      0.0,   v, 0.0, # 3 Green    (ey)
            0.0, 0.0, 0.0,      0.0,   v,   v, # 4 Cyan     (ez)
            0.0, 0.0,   e,      0.0,   v,   v, # 5 Cyan     (ez)
            ]))
        vao = self.ctx.vertex_array(
                self.shaders['shader_test_vec'],
                [(vbo, '3f 3f', 'vert_pos', 'vert_color')])
        vao.render(mode=moderngl.LINES)
        vao.release()

        def render_test_xz_plane() -> None:
            """Draw a square on the xz plane."""
            vbo = self.ctx.buffer(data=array('f', [
                0.0, 0.0, 0.0,        v, 0.0, 0.0, # 0 Red      (ex)
                0.0, 0.0,   e,      0.0,   v,   v, # 3 Cyan     (ez)
                  e, 0.0, 0.0,        v, 0.0, 0.0, # 1 Red      (ex)
                  e, 0.0,   e,      0.0,   v,   v, # 2 Cyan     (ez)
                ]))
            vao = self.ctx.vertex_array(
                    self.shaders['shader_test_vec'],
                    [(vbo, '3f 3f', 'vert_pos', 'vert_color')])
            vao.render(mode=moderngl.TRIANGLE_STRIP)
            vao.release()
        render_test_xz_plane()


    def render_test_vec(self, x=0.1, y=0.4, z=0.3) -> None:
        """Draw a vector and its components."""
        self.shaders['shader_test_vec']['proj_mat'] = self.proj_mat
        self.shaders['shader_test_vec']['view_mat'] = self.view_mat
        self.shaders['shader_test_vec']['tilt_mat'] = self.tilt_mat
        self.shaders['shader_test_vec']['alpha'] = 1.0
        v=1.0 # color value
        vbo = self.ctx.buffer(data=array('f', [
            # position          color
            0.0, 0.0, 0.0,        v,   v,   v, #  0 White   (V)
              x,   y,   z,        v,   v,   v, #  1 White   (V)
            0.0, 0.0, 0.0,        v, 0.0, 0.0, #  2 Red     (Vx)
              x, 0.0, 0.0,        v, 0.0, 0.0, #  3 Red     (Vx)
              x, 0.0, 0.0,      0.0,   v, 0.0, #  4 Green   (Vy)
              x,   y, 0.0,      0.0,   v, 0.0, #  5 Green   (Vy)
              x,   y, 0.0,      0.0,   v,   v, #  6 Cyan    (Vz)
              x,   y,   z,      0.0,   v,   v, #  7 Cyan    (Vz)
            ]))
        if 0: # use indices
            indices = array('B', [
                0,1, # x-axis
                2,3, # y-axis
                4,5, # z-axis
                6,7, # x-component
                8,9, # y-component
                2,3, # z-component
                0,3, # Vector
                ])
            ibo = self.ctx.buffer(data=indices)
            vao = self.ctx.vertex_array(
                    self.shaders['shader_test_vec'],
                    [(vbo, '3f 3f', 'vert_pos', 'vert_color')],
                    index_buffer=ibo,
                    index_element_size=indices.itemsize)
        else:
            vao = self.ctx.vertex_array(
                    self.shaders['shader_test_vec'],
                    [(vbo, '3f 3f', 'vert_pos', 'vert_color')])
        vao.render(mode=moderngl.LINES)
        vao.release()

class Game:
    def __init__(self) -> None:
        check_array_itemsize()
        pygame.init()
        pygame.font.init()
        self.os_window = OsWindow(gpu_render=True)
        self.gpu = GPU(self)

        self.ui = UI(self)
        self.clock = pygame.time.Clock()
        self.debug = True

    def run(self) -> None:
        while True: self.game_loop()

    def game_loop(self) -> None:
        self.text_hud = TextHud(self) if self.debug else None
        self.ui.handle_events()
        self.gpu.render()
        self.clock.tick(60)

if __name__ == '__main__':
    logger = setup_logging()
    logger.info(f"Run {Path(__file__).name}")
    atexit.register(shutdown, f"{Path(__file__).name}")
    Game().run()
