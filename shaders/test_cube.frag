# version 330
in vec4 frag_color;
out vec4 color;
void main(){
    color = vec4(frag_color.rgb, 1);
}

