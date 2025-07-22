FLAT_COLOR = """
#version 330 core

in vec4 fragment_color;

out vec4 output_color;

void main() {
    output_color = fragment_color;
}
"""

TEXTURE = """
#version 330 core

in vec2 fragment_texcoord;
in vec4 fragment_color;

out vec4 output_color;

uniform sampler2D tex_1;

void main() {
    output_color = texture(tex_1, fragment_texcoord) * fragment_color;
}
"""

BLINN_PHONG = """
#version 330 core

in vec3 normal;
in vec4 fragment_color;
out vec4 output_color;

void main() {
    const float Pi = 3.14159265;
    const float shininess = 16.0;
    vec3 light_color = vec3(1.0, 1.0, 1.0) * 0.9;
    vec3 light_pos = vec3(0.3, 0.3, 1.0);
    vec3 light_dir = normalize(light_pos);
    vec3 norm = normalize(normal);
    float spec = 0.0;

    // Ambient
    float ambient_strength = 0.3;
    vec3 ambient = light_color * ambient_strength;

    // Diffuse
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diff * light_color;

    // Specular
    float specular_strength = 0.6;

    const float energy_conservation = ( 8.0 + shininess ) / ( 8.0 * Pi );
    spec = energy_conservation * pow(max(dot(norm, light_dir), 0.0), shininess);

    vec3 specular = specular_strength * spec * light_color;

    vec3 p = ((ambient + diffuse) * fragment_color.xyz) + specular;
    output_color = vec4(p, fragment_color.w);
}
"""
