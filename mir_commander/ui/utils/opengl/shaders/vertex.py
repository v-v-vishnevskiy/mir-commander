COMPUTE_POSITION = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 in_normal;

uniform mat4 scene_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;
uniform mat4 model_matrix;
uniform vec4 color;

out vec3 normal;
out vec4 fragment_color;

void main() {
    gl_Position = projection_matrix * view_matrix * scene_matrix * model_matrix * vec4(position, 1.0);

    // Transform normal to world space
    normal = mat3(transpose(inverse(scene_matrix * model_matrix))) * in_normal;
    fragment_color = color;
}
"""

COMPUTE_POSITION_INSTANCED = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 in_normal;

// Instanced attributes
layout (location = 2) in vec4 instance_color;
layout (location = 3) in mat4 instance_model_matrix;

uniform mat4 scene_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;

out vec3 normal;
out vec4 fragment_color;

void main() {
    gl_Position = projection_matrix * view_matrix * scene_matrix * instance_model_matrix * vec4(position, 1.0);

    // Transform normal to world space
    normal = mat3(transpose(inverse(scene_matrix * instance_model_matrix))) * in_normal;
    fragment_color = instance_color;
}
"""
