WBOIT_TRANSPARENT_FLAT = """
#version 330 core

in vec3 normal;
in vec4 fragment_color;

layout (location = 0) out vec4 accum;
layout (location = 1) out float alpha;

void main() {
    accum = vec4(fragment_color.rgb * fragment_color.a, fragment_color.a);
    alpha = 1.0 - fragment_color.a;
}
"""


WBOIT_TRANSPARENT = """
#version 330 core

in vec3 normal;
in vec4 fragment_color;

layout (location = 0) out vec4 accum;
layout (location = 1) out float alpha;

void main() {
    const float Pi = 3.14159265;
    const float shininess = 32.0;
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

    vec3 p = ((ambient + diffuse) * fragment_color.rgb) + specular;

	accum = vec4(p.rgb * fragment_color.a, fragment_color.a);
	alpha = 1.0 - fragment_color.a;
}
"""


WBOIT_FINALIZE = """
#version 330 core

in vec2 fragment_texcoord;
uniform sampler2D opaque_texture;
uniform sampler2D accum_texture;
uniform sampler2D alpha_texture;

out vec4 output_color;

void main() {
    vec4 opaque_color = texture(opaque_texture, fragment_texcoord);
    vec4 accum = texture(accum_texture, fragment_texcoord);
    float alpha = 1.0 - texture(alpha_texture, fragment_texcoord).r;

    // If no transparent geometry, show opaque only
    if (accum.a <= 0.0001) {
        output_color = opaque_color;
        return;
    }

    // Compute average transparent color
    vec3 transparent_color = accum.rgb / accum.a;

    // Blend transparent with opaque background using coverage (alpha)
    vec3 color = transparent_color * alpha + opaque_color.rgb * (1.0 - alpha);

    // Output alpha depends on background type
    float output_alpha = opaque_color.a > 0.0 ? max(alpha, opaque_color.a) : alpha;
    output_color = vec4(color, output_alpha);
}
"""


FLAT_COLOR = """
#version 330 core

in vec3 normal;
in vec4 fragment_color;
out vec4 output_color;

void main() {
    output_color = fragment_color;
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
