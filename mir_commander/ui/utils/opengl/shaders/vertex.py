COMPUTE_POSITION = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 in_normal;

uniform mat4 view_matrix;
uniform mat4 projection_matrix;
uniform mat4 model_matrix;

out vec3 normal;
out vec3 fragment_position;

void main() {
    gl_Position = projection_matrix * view_matrix * model_matrix * vec4(position, 1.0);
    normal = in_normal;
    fragment_position = vec3(model_matrix * vec4(position, 1.0));
}
"""
