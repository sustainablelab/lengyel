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

* Vim omni-completion (`:h new-omni-completion`) opens empty preview windows
  for moderngl, so use the website documentation instead:
  * [Context Flags](https://moderngl.readthedocs.io/en/latest/reference/context.html#context-flags)
  * [Primitive Modes](https://moderngl.readthedocs.io/en/latest/reference/context.html#primitive-modes)
  * [Texture Filters](https://moderngl.readthedocs.io/en/latest/reference/context.html#texture-filters)
  * [Blend Function Shortcuts](https://moderngl.readthedocs.io/en/latest/reference/context.html#blend-function-shortcuts)
  * [Other Enums](https://moderngl.readthedocs.io/en/latest/reference/context.html#other-enums)
  * [Context.program](https://moderngl.readthedocs.io/en/latest/reference/context.html#Context.program)
  * [Context.buffer](https://moderngl.readthedocs.io/en/latest/reference/context.html#Context.buffer)
  * [Context.vertex_array](https://moderngl.readthedocs.io/en/latest/reference/context.html#Context.vertex_array)
  * [Context.clear()](https://moderngl.readthedocs.io/en/latest/reference/context.html#Context.clear)
  * [Context.enable()](https://moderngl.readthedocs.io/en/latest/reference/context.html#Context.enable)
  * [Context.disable()](https://moderngl.readthedocs.io/en/latest/reference/context.html#Context.disable)
  * [Context.front_face](https://moderngl.readthedocs.io/en/latest/reference/context.html#Context.front_face)
  * [Context.cull_face](https://moderngl.readthedocs.io/en/latest/reference/context.html#Context.cull_face)
  * [Context.wireframe](https://moderngl.readthedocs.io/en/latest/reference/context.html#Context.cull_face)
  * [Context.info](https://moderngl.readthedocs.io/en/latest/reference/context.html#Context.info)
  * [VertexArray.render()](https://moderngl.readthedocs.io/en/latest/reference/vertex_array.html#VertexArray.render)
  * [VertexArray.release()](https://moderngl.readthedocs.io/en/latest/reference/vertex_array.html#VertexArray.release)
* flags
  * Remember to set flags `pygame.OPENGL | pygame.DOUBLEBUF`! Otherwise memory
    in GPU is garbage and the program segfaults.
    ```python
    pygame.display.set_mode((16*50,9*50), flags=pygame.RESIZABLE | pygame.OPENGL | pygame.DOUBLEBUF)
    ```
* `pygame.Surface.get_size()`
  * This returns the size of the OS Window surface (created by
    `pygame.display.set_mode()`) when CPU rendering, **but not when GPU
    rendering**.
  * Use `WINDOWRESIZED` when GPU rendering to get the new size of the OS window
  * Use OS window size to maintain a fixed-size debug HUD: this happens in
    `libs/gpu.py` in `GPU.make_hud_vbo()`.
* `pygame.display.toggle_fullscreen()`
  * This works when GPU rendering, but not when CPU rendering.
  * I don't bother to add the code for CPU rendering, it is a bunch of extra
    work. I start with the CPU rendering just to get an initial window with
    debug HUD set up. After that, I only run with `OsWindow(gpu_render=True)`.
* Shaders read matrices in column order, not row order.
  * For example, the first four entries in a `mat4` are the first column of the
    matrix, **not the first row of the matrix**
* Test size of `array` datatypes, don't assume.
  * I am using the built-in `array` module instead of depending on `numpy`.
  * See docs for module `array` https://docs.python.org/3/library/array.html
    * This documentation starts with a table of byte sizes.
    * These are the **minimum** size in bytes, not the actual size in bytes on your machine.
  * To explore this, make some data and print the 'itemsize':
    ```python
    data=array('L', [ # 'B': uint8, 'H': uint16, 'I': uint32, 'L': uint64
        0,1,2,3
        ])
    logger.debug(data.itemsize)
    sys.exit()
    ```
  * The VAO needs to know the IBO element size. Use `data.itemsize` instead of a hard-coding:
    * Do this:
    ```python
      indices = array('I', [0,1,2,3]) # Store in a variable to access itemsize later
      ibo = self.ctx.buffer(data=indices)
      vao = self.ctx.vertex_array(
              ...
              index_buffer=ibo,
              index_element_size=indices.itemsize) # Use itemsize. Do not hard-code element size.
    ```
    * This avoids some confusing bugs. For example, if OpenGL thinks the
      indices are *half* the size they actually are (using `L` -- 8 bytes --
      but assuming `L` is only 4 bytes), then it will completely misinterpret
      how to index the VBO. The program will still run, but some vertices will
      be skipped and some will be repeated.
  * Using `data.itemsize` helps, but I still need to test data type sizes on different machines:
    * Add initialization code that tests the `data.itemsize` for datatypes in use.
    * Log errors if the size is less than the assumed value: e.g., if `I` is 2, consider that an error.
    * Log warnings if the size is greater than the assumed value. The program
      should still run, but there might be loss in performance.
* Default winding is CCW. See [Face Culling](https://www.khronos.org/opengl/wiki/Face_Culling)
  * But winding only has an effect if face culling is enabled
