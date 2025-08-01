ATOM_LABEL = """
#version 330 core

in vec2 fragment_texcoord;
in vec4 fragment_color;
in float fragment_depth;

out vec4 output_color;

uniform sampler2D tex_1;

void main() {
    output_color = texture(tex_1, fragment_texcoord) * fragment_color;
    gl_FragDepth = fragment_depth;
}
"""
