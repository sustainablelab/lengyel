#version 330

in vec2 vert_pos;
in vec2 tex_coord;
out vec2 uv;

void main(){
    uv = tex_coord;
    gl_Position = vec4(vert_pos, 0.0, 1.0);
}
