FLAT_COLOR = """
#version 330 core

out vec4 output_color;

uniform vec4 color;

void main() {
    output_color = color;
}
"""

DIFFUSE = """
#version 330 core

in vec3 normal;
in vec3 fragment_position;
out vec4 output_color;

uniform vec4 color;

void main() {
    vec3 light_color = vec3(1.0, 1.0, 1.0) * 0.9;
    vec3 light_direction = normalize(vec3(0.3, 0.3, 1.0));
    vec3 norm = normalize(normal);

    // Ambient
    float ambient_strength = 0.1;
    vec3 ambient = light_color * ambient_strength;

    // Diffuse
    float diff = max(dot(norm, light_direction), 0.0);
    vec3 diffuse = diff * light_color;

    output_color = vec4((ambient + diffuse) * color.xyz, color.w);
}
"""
