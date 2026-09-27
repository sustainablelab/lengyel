# version 330
in vec4 frag_color;
out vec4 color;
uniform float alpha;
void main(){
    color = vec4(frag_color.rgb, alpha);
}

