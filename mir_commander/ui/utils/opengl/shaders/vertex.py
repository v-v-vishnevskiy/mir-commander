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
    
    // Transform normal to world space
    normal = mat3(transpose(inverse(model_matrix))) * in_normal;
    fragment_position = vec3(model_matrix * vec4(position, 1.0));
}
"""

COMPUTE_POSITION_INSTANCED = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 in_normal;

// Instanced attributes for transformation matrix
layout (location = 2) in mat4 instance_model_matrix;

uniform mat4 view_matrix;
uniform mat4 projection_matrix;

out vec3 normal;
out vec3 fragment_position;

void main() {
    gl_Position = projection_matrix * view_matrix * instance_model_matrix * vec4(position, 1.0);
    
    // Transform normal to world space
    normal = mat3(transpose(inverse(instance_model_matrix))) * in_normal;
    fragment_position = vec3(instance_model_matrix * vec4(position, 1.0));
}
"""
