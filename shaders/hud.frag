#version 330

in vec2 uv;
uniform sampler2D tex;
uniform float alpha;
out vec4 color;

void main(){
    color = vec4(texture(tex, uv).rgb, alpha);
}
