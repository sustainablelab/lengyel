# About

I am reading *Foundations of Game Engine Development Volume 1 Mathematics* by Eric Lengyel.

In addition to doing the pencil-and-paper exercises, I want to apply this
knowledge. I set up a simple game loop for drawing with OpenGL.

# Usage

* `F11` toggle fullscreen
* `F2` toggle debug HUD

# Tools

* `pygame`: wrapper around SDL2; creates the context used by `moderngl`
* `moderngl`: Python package for using OpenGL

# Gotchas

* flags
  * Remember to set flags `pygame.OPENGL | pygame.DOUBLEBUF`! Otherwise memory
    in GPU is garbage and the program segfaults.
* `pygame.Surface.get_size()`
  * This returns the size of the OS Window surface (created by
    `pygame.display.set_mode()`) when CPU rendering, **but not when GPU
    rendering**.
  * Use `WINDOWRESIZED` when GPU rendering to get the new size of the OS window
  * Use OS window size to maintain a fixed-size debug HUD: this happens in
    `libs/gpu.py` in `make_hud_vbo()`.
* `pygame.display.toggle_fullscreen()`
  * This works when GPU rendering, but not when CPU rendering.
  * I don't bother to add the code for CPU rendering, it is a bunch of extra
    work. I start with the CPU rendering just to get an initial window with
    debug HUD set up. After that, I only run with `gpu_render=True`.
