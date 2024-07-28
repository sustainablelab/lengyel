#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""GPU rendering
"""
import pygame
from pygame import Surface, Rect, Color
import moderngl
from array import array
import logging

logger = logging.getLogger(__name__)

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
        shader = self.ctx.program(vertex_shader=vert, fragment_shader = frag)
        shaders['shader_test_square'] = shader
        # Player
        with open('shaders/debug_player.vert') as f: vert = f.read()
        with open('shaders/debug_player.frag') as f: frag = f.read()
        shader = self.ctx.program(vertex_shader=vert, fragment_shader = frag)
        shaders['shader_debug_player'] = shader
        return shaders

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
        # Zoom out
        a = 1 # self.game.scale
        self.view_mat = array('f', [
            a, 0, 0, 0,
            0, a, 0, 0,
            0, 0, a, 0,
            0, 0, 0, 1,
            ])

    def render(self) -> None:
        self.ctx.clear(0.1,0.1,0.8)
        self.ctx.blend_func = moderngl.PREMULTIPLIED_ALPHA # Makes text background transparent
        self.ctx.enable(moderngl.BLEND)
        self.render_test_square()
        self.render_player()
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

    def render_test_square(self) -> None:
        """Test aspect ratio with this square."""
        # Define the square in world space
        k = 0.2
        vbo = self.ctx.buffer(data=array('f', [-k,k, k,k, -k,-k, k,-k]))
        vao = self.ctx.vertex_array(
                self.shaders['shader_test_square'],
                [(vbo, '2f', 'vert_pos')])
        # Apply transforms
        self.shaders['shader_test_square']['proj_mat'] = self.proj_mat # aspect ratio
        self.shaders['shader_test_square']['view_mat'] = self.view_mat # zoom and pan
        # Render
        vao.render(mode=moderngl.TRIANGLE_STRIP)

    def render_player(self) -> None:
        # Draw a debug rect
        size = self.game.player.size
        x,y = size
        vbo = self.ctx.buffer(data=array('f', [0,y, x,y, 0,0, x,0]))
        vao = self.ctx.vertex_array(
                self.shaders['shader_debug_player'],
                [(vbo, '2f', 'vert_pos')])
        # Translate
        x,y = self.game.player.pos                      # Player position in world space (game coordinates)
        # Let u,v be the player position in model space
        # Move the player to world space position x,y
        # | 1, 0, 0, x ||u| = |u + x|
        # | 0, 1, 0, y ||v|   |v + y|
        # | 0, 0, 1, 0 ||0|   |0    |
        # | 0, 0, 0, 1 ||1|   |1    |
        self.shaders['shader_debug_player']['xlat_mat'] = array('f', [
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            x, y, 0, 1,
            ])
        # Correct for aspect ratio
        self.shaders['shader_debug_player']['proj_mat'] = self.proj_mat # aspect ratio
        self.shaders['shader_debug_player']['view_mat'] = self.view_mat # zoom and pan
        # Testing mouse zoom
        self.shaders['shader_debug_player']['test_mat'] = self.game.test_matrix
        vao.render(mode=moderngl.TRIANGLE_STRIP)
