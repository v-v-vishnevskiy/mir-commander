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
layout (location = 2) in mat4 instance_model_matrix;
layout (location = 9) in vec4 instance_color;

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


BILLBOARD_TEXT = """
#version 330 core

layout (location = 0) in vec3 position;  // world vertex position
layout (location = 2) in vec2 in_texcoord;
layout (location = 3) in mat4 instance_model_matrix;
layout (location = 7) in vec3 instance_local_position;
layout (location = 8) in vec3 instance_parent_world_position;
layout (location = 9) in vec3 instance_parent_parent_world_position;
layout (location = 10) in vec4 instance_color;

uniform mat4 scene_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;

out vec2 fragment_texcoord;
out vec4 fragment_color;

void main() {
    vec3 scene_scale;
    scene_scale.x = length(vec3(scene_matrix[0][0], scene_matrix[0][1], scene_matrix[0][2]));
    scene_scale.y = length(vec3(scene_matrix[1][0], scene_matrix[1][1], scene_matrix[1][2]));
    scene_scale.z = length(vec3(scene_matrix[2][0], scene_matrix[2][1], scene_matrix[2][2]));

    vec3 model_scale;
    model_scale.x = length(vec3(instance_model_matrix[0][0], instance_model_matrix[0][1], instance_model_matrix[0][2]));
    model_scale.y = length(vec3(instance_model_matrix[1][0], instance_model_matrix[1][1], instance_model_matrix[1][2]));
    model_scale.z = length(vec3(instance_model_matrix[2][0], instance_model_matrix[2][1], instance_model_matrix[2][2]));

    // get center position in world space
    vec3 parent_pos = vec3(scene_matrix * vec4(instance_parent_world_position, 1.0));
    vec3 parent_parent_pos = vec3(scene_matrix * vec4(instance_parent_parent_world_position, 1.0));

    // apply scale to position
    vec3 scaled_position = (position + instance_local_position) * model_scale * scene_scale;

    vec4 parent_world_pos = vec4(scaled_position + parent_pos, 1.0);
    vec4 parent_parent_world_pos = vec4(scaled_position + parent_parent_pos, 1.0);

    vec4 world_parent = view_matrix * parent_world_pos;
    vec4 world_parent_parent = view_matrix * parent_parent_world_pos;
    vec4 proj_world_parent = projection_matrix * world_parent;
    vec4 proj_world_parent_parent = projection_matrix * world_parent_parent;

    float length_parent = length(proj_world_parent_parent.xyz - proj_world_parent.xyz);
    float z = proj_world_parent_parent.z - length_parent;

    gl_Position = vec4(proj_world_parent_parent.xy, z, proj_world_parent_parent.w);

    fragment_texcoord = vec2(in_texcoord.x, 1.0 - in_texcoord.y);
    fragment_color = instance_color;
}
"""
