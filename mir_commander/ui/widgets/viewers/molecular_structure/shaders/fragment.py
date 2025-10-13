ATOM_LABEL = """
#version 330 core

in vec2 fragment_texcoord;
in vec4 fragment_color;
in float fragment_depth;

layout (location = 0) out vec4 accum;
layout (location = 1) out float alpha;

uniform sampler2D tex_1;

void main() {
    vec4 color = texture(tex_1, fragment_texcoord);
    if (color.a < 0.01) {
        discard;
    }

    accum = vec4(color.rgb * fragment_color.rgb, color.a);
    alpha = 1.0 - color.a;

    gl_FragDepth = fragment_depth;
}
"""
