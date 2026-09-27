# version 330
in vec3 vert_pos;
in vec3 vert_color;
out vec4 frag_color;
uniform mat4 proj_mat;
uniform mat4 view_mat;
uniform mat4 tilt_mat;
void main(){
    frag_color = vec4(vert_color, 1.0);
    vec4 pos = vec4(vert_pos, 1.0);
    gl_Position = view_mat * tilt_mat * proj_mat * pos;
}
