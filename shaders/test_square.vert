# version 330
in vec2 vert_pos;
uniform mat4 proj_mat;
uniform mat4 view_mat;
void main(){
    vec4 pos = vec4(vert_pos, 0.0, 1.0);
    gl_Position = view_mat * proj_mat * pos;
}
