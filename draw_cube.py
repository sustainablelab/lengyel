#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""TODO: write a script docstring.
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

        # Create a context
        self.ctx = moderngl.create_context()
        self.log_ctx_info()

        # Load shaders
        self.shaders = self.load_shaders()

        # Update transforms
        self.update_transforms()

    def log_ctx_info(self) -> None:
        ### GL_VENDOR: Intel
        logger.debug(f"GL_VENDOR: {self.ctx.info['GL_VENDOR']}")
        ### GL_RENDERER: Mesa Intel(R) Graphics (ADL GT2)
        logger.debug(f"GL_RENDERER: {self.ctx.info['GL_RENDERER']}")
        ### GL_VERSION: 4.6 (Compatibility Profile) Mesa 23.2.1-1ubuntu3.1~22.04.2
        logger.debug(f"GL_VERSION: {self.ctx.info['GL_VERSION']}")

    def update_transforms(self) -> None:
        """Update transforms that are global to all GPU rendering."""
        # Correct for aspect ratio
        a = self.game.os_window.size[1]/self.game.os_window.size[0]
        self.proj_mat = array('f', [
            a, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1,
            ])
        a = 1 # self.game.scale
        self.view_mat = array('f', [
            a, 0, 0, 0,
            0, a, 0, 0,
            0, 0, a, 0,
            0, 0, 0, 1,
            ])

    def load_shaders(self) -> dict:
        shaders = {}
        # HUD
        ### f.read(): Read until EOF. See https://docs.python.org/3/library/io.html#io.BufferedIOBase.read
        with open("shaders/hud.vert") as f: vert = f.read()
        with open("shaders/hud.frag") as f: frag = f.read()
        shader = self.ctx.program(vertex_shader=vert, fragment_shader=frag)
        shaders['shader_hud'] = shader
        # Test square
        with open('shaders/test_square.vert') as f: vert = f.read()
        with open('shaders/test_square.frag') as f: frag = f.read()
        shader = self.ctx.program(vertex_shader=vert, fragment_shader=frag)
        shaders['shader_test_square'] = shader
        # Test cube
        with open('shaders/test_cube.vert') as f: vert = f.read()
        with open('shaders/test_cube.frag') as f: frag = f.read()
        shader = self.ctx.program(vertex_shader=vert, fragment_shader = frag)
        shaders['shader_test_cube'] = shader
        return shaders

    def render(self) -> None:
        self.ctx.clear(0.05,0.05,0.05)
        self.ctx.blend_func = moderngl.PREMULTIPLIED_ALPHA # Makes text background transparent
        self.ctx.enable(moderngl.BLEND)
        self.render_test_cube()
        self.render_test_square()
        if self.game.text_hud: self.render_hud()
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

    def render_test_cube(self) -> None:
        """Test aspect ratio with this cube.

        Cube: eight vertices
        --------------------
        Note that by thinking of four vertices as being on the front face
        and four as being on the back face, we get all eight vertices.

        (We could also have done four vertices on the top face and four on
        the bottom face, like Figure 3.1 of Lengyel.)

        Cube: twelve triangles
        ----------------------
        Right-hand rule: specify CW winding so normal is directed outwards.
        0,2,1, # Front
        1,2,3, # Front
        4,5,6, # Back
        5,7,6, # Back
        5,1,7, # Right
        7,1,3, # Right
        0,4,2, # Left
        6,2,0, # Left
        """
        # Apply transforms
        self.shaders['shader_test_cube']['proj_mat'] = self.proj_mat # aspect ratio
        self.shaders['shader_test_cube']['view_mat'] = self.view_mat # zoom and pan
        # Define the cube in world space.
        k = 0.3
        # Eight vertices
        vbo = self.ctx.buffer(data=array('f', [
            -k, k, k,   # 0 (Front top left)
             k, k, k,   # 1 (Front top right)
            -k,-k, k,   # 2 (Front bottom left)
             k,-k, k,   # 3 (Front bottom right)
            -k, k,-k,   # 4 (Back top left)
             k, k,-k,   # 5 (Back top right)
            -k,-k,-k,   # 6 (Back bottom left)
             k,-k,-k,   # 7 (Back bottom right)
            ]))
        # 12 triangles
        indices = array('B', [ # 'B": uint8, 'I': uint32
            0,1,2, # Front
            1,2,3, # Front
            4,5,6, # Back
            5,7,6, # Back
            5,1,7, # Right
            7,1,3, # Right
            0,4,2, # Left
            6,2,0, # Left
            ])
        ibo = self.ctx.buffer(data=indices)
        vao = self.ctx.vertex_array(
                self.shaders['shader_test_cube'],
                [(vbo, '3f', 'vert_pos')],
                index_buffer=ibo,
                index_element_size=indices.itemsize)
        # Render
        vao.render(mode=moderngl.TRIANGLES)
        # vao.render(mode=moderngl.LINE_STRIP)
        # vao.render(mode=moderngl.POINTS)
        # vao.render(mode=moderngl.LINES)
        # vao.release()

    def render_test_square(self) -> None:
        k = 0.2
        vbo = self.ctx.buffer(data=array('f', [-k,k, k,k, -k,-k, k,-k]))
        vao = self.ctx.vertex_array(
                self.shaders['shader_test_square'],
                [(vbo, '2f', 'vert_pos')])
        self.shaders['shader_test_square']['proj_mat'] = self.proj_mat
        self.shaders['shader_test_square']['view_mat'] = self.view_mat
        vao.render(mode=moderngl.TRIANGLE_STRIP)

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
