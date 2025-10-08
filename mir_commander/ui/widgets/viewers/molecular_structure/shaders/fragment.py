ATOM_LABEL = """
#version 330 core

in vec2 fragment_texcoord;
in vec4 fragment_color;
in float fragment_depth;

out vec4 output_color;

uniform sampler2D tex_1;

void main() {
    vec4 color = texture(tex_1, fragment_texcoord);
    if (color.a < 0.01) {
        discard;
    }

    output_color = vec4(fragment_color.rgb, color.a);

    gl_FragDepth = fragment_depth;
}
"""
